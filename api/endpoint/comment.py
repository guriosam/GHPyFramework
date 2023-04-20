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
                if review:
                    self.collect_single_review(str(pull['number']))
                else:
                    self.collect_single(str(pull['number']))

        except:
            pass
        #issues = self.database_issues.find({})

        #for issue in issues:
        #    self.collect_single(issue['issue_url'])

        #request_url = self.api_url + self.owner + '/' + self.repo + '/issues/comments?page='
        #page = 1
        #comments = []

        #while True:
        #    comment_batch = self.apiHandler.request(request_url + str(page))
        #    if not comment_batch:
        #        break
        #    comments.append(comment_batch)

        #    for comment in comment_batch:
        #        if self.database.find_one({'id': comment['id']}):
        #            continue

        #        self.database.insert_one({'id': comment['id']})

        #    page = page + 1

        #return comments

    def collect_single(self, issue_number: str):
        """
        Collect a single element of the API
        :param issue_number: parameter that will be used by the function to know which element it should download
        :type issue_number: str
        :return: json downloaded
        :rtype: dict
        """
        page = 1

        print("******* Comments of Issue number " + str(issue_number) + " *********")

        while True:

            comment = self.database_comments.find_one({'issue_number': issue_number})
            if comment:
                print('Comments of Issue number ' + str(issue_number) + ' already in the database.')
                return comment

            request_url = self.api_url + self.owner + '/' + self.repo + '/issues/' + str(issue_number) + \
                          '/comments?page=' + str(page)

            comments = self.apiHandler.request(request_url)

            if not comments:
                break

            for comment in comments:
                comment['issue_number'] = int(issue_number)
                self.database_comments.insert_one(comment)

            print('Comments of Issue number ' + str(issue_number) + ' saved.')

            page = page + 1

        return self.database_comments.find({})

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
                self.database_reviews.insert_one(comment)

            print('Comments of Pull number ' + str(pull_number) + ' saved.')

            page = page + 1

        return self.database_reviews.find({})