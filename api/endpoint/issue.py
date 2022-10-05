import json

from pymongo.database import Database

from api.endpoint.api_interface import APIInterface
from utils.api_call_handler import APICallHandler


class IssueAPI(APIInterface):

    def __init__(self, owner: str, repo: str, database: Database):
        # config = JSONHandler('../').open_json('config.json')
        self.owner = owner
        self.repo = repo

        self.database = database

        if 'issues' not in database.name:
            self.database = database['issues']

        # self.path = config['output_path']
        self.apiHandler = APICallHandler()
        self.api_url = 'https://api.github.com/repos/'

    def collect_batch(self, review: bool = False, save: bool = False):
        """
        Collect several groups of 30 elements returned by the API until the pages return an empty JSON
        :param save: if it should persist the json downloaded on the hard drive
        :type save: bool
        :return: list of elements returned by the API
        :rtype: list
        """
        request_url = self.api_url + self.owner + '/' + self.repo + '/issues?state=all&page='
        page = 1
        issues = []
        # json = JSONHandler(self.path + self.repo + '/issues/all/')
        while True:
            issue_batch = self.apiHandler.request(request_url + str(page))
            if issue_batch:
                issues.append(issue_batch)
                for issue in issue_batch:
                    if self.database.find_one({'number': issue['number']}):
                        return issues
                page = page + 1
            else:
                break

        return issues

    def collect_single(self, number: str):
        """
        Collect a single element of the API
        :param number: parameter that will be used by the function to know which element it should download
        :type number: str
        :return: json downloaded
        :rtype: dict
        """

        number = int(number)
        #json = JSONHandler(self.path + self.repo + '/issues/individual/')
        issue = self.database.find_one({'number': number})
        if issue:
            return issue

        issue = self.apiHandler.request(self.api_url + self.owner + '/' + self.repo + '/issues/' + str(number))
        if issue:
            #issue_json = json.dumps(issue)
            self.database.insert_one(issue)
            return self.database.find_one({'number': number})
        else:
            print('Empty JSON of ' + str(number))

        return issue
