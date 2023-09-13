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
        self.database_pulls = database['pull_requests']
        self.database_issues = database['issues']
        self.database_comments = database['comments']
        self.database_reviews = database['reviews']

        self.api_url = 'https://api.github.com/repos/'
        self.apiHandler = APICallHandler()

    def collect_batch(self, review: bool = False, save: bool = True):
        """
        Collect several groups of 30 elements returned by the API until the pages return an empty JSON
        :param review:
        :param save: if it should persist the json downloaded on the hard drive
        :type save: bool
        :return: list of elements returned by the API
        :rtype: list
        """

        try:
            pulls = self.database_pulls.find({}, no_cursor_timeout=True)

            for pull in pulls:
                number_comments = int(pull['comments'])
                if number_comments == 0:
                    continue

                if review:
                    self.collect_single_review(str(pull['number']))
                else:
                    comment, end = self.collect_single(str(pull['number']))
                    if end:
                        break
        except:
            pass

    def collect_single(self, issue_number: str):
        """
        Collect a single element of the API
        :param issue_number: parameter that will be used by the function to know which element it should download
        :type issue_number: str
        :return: json downloaded
        :rtype: dict
        """
        page = 1

        while True:

            comment = self.database_comments.find_one({'issue_number': int(issue_number)})
            if comment:
                print('Comments of Issue number ' + str(issue_number) + ' already in the database.')
                return comment, True

            request_url = self.api_url + self.owner + '/' + self.repo + '/issues/' + str(issue_number) + \
                          '/comments?page=' + str(page)

            print("******* Comments of Issue number " + str(issue_number) + " *********")

            comments = self.apiHandler.request(request_url)

            if not comments:
                break

            for comment in comments:
                comment['issue_number'] = int(issue_number)
                comment_database = self.database_comments.find_one({'id': comment['id']})
                if comment_database:
                    return comment_database, True

                self.database_comments.insert_one(comment)

            print('Comments of Issue number ' + str(issue_number) + ' saved.')

            page = page + 1

        return self.database_comments.find({}), False

    def collect_single_review(self, pull_number: str):
        """
        Collect a single element of the API
        :param pull_number: parameter that will be used by the function to know which element it should download
        :type pull_number: str
        :return: json downloaded
        :rtype: dict
        """
        page = 1

        print("******* Comments of Pull number " + str(pull_number) + " *********")

        while True:

            comment = self.database_reviews.find_one({'pull_number': pull_number})
            if comment:
                print('Comments of Pull number ' + str(pull_number) + ' already in the database.')
                return comment

            request_url = self.api_url + self.owner + '/' + self.repo + '/pulls/' + str(pull_number) + \
                          '/comments?page=' + str(page)

            comments = self.apiHandler.request(request_url)

            if not comments:
                break

            for comment in comments:
                comment['pull_number'] = int(pull_number)

                comment_database = self.database_reviews.find_one({'id': comment['id']})
                if comment_database:
                    return self.database_comments.find({})

                self.database_reviews.insert_one(comment)

            print('Comments of Pull number ' + str(pull_number) + ' saved.')

            page = page + 1

        return self.database_reviews.find({})
