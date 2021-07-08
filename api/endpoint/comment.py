import json

from pymongo.database import Database

from api.endpoint.api_interface import APIInterface
from utils.api_call_handler import APICallHandler
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"


class CommentAPI(APIInterface):

    def __init__(self, owner: str, repo: str, database: Database = None):
        super()
        self.owner = owner
        self.repo = repo

        self.database = database

        if 'comments' not in database.name:
            self.database = database['comments']

        self.api_url = 'https://api.github.com/repos/'
        self.apiHandler = APICallHandler()

    def collect_batch(self, save: bool = True):
        """
        Collect several groups of 30 elements returned by the API until the pages return an empty JSON
        :param save: if it should persist the json downloaded on the hard drive
        :type save: bool
        :return: list of elements returned by the API
        :rtype: list
        """
        request_url = self.api_url + self.owner + '/' + self.repo + '/issues/comments?page='
        page = 1
        new_comments = True

        comments_size = self.database.find({}).count()

        while True:
            comment_batch = self.apiHandler.request(request_url + str(page))

            if not comment_batch:
                break

            for comment in comment_batch:
                if self.database.find_one({'id': comment['id']}):
                    break

                comment['issue_number'] = int(comment['issue_url'].split('issues/')[1])
                self.database.insert_one(comment)

            page += 1

        return comments_size < self.database.find({}).count()




    def collect_single(self, issue_number: str):
        """
        Collect a single element of the API
        :param issue_number: parameter that will be used by the function to know which element it should download
        :type issue_number: str
        :return: json downloaded
        :rtype: dict
        """
        page = 1

        issue_number = issue_number.split('/')
        issue_number = issue_number[len(issue_number) - 1]

        while True:

            comment = self.database.find_one({'id': issue_number})
            if comment:
                return comment

            request_url = self.api_url + self.owner + '/' + self.repo + '/issues/' + str(issue_number) + \
                          '/comments?page=' + str(page)

            comments = self.apiHandler.request(request_url)

            if not comment:
                break

            for comment in comments:
                self.database.insert_one(comment)

            page = page + 1

        return self.database.find()
