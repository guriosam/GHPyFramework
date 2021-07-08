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


class CommitAPI(APIInterface):

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo

        self.database = database

        if 'commits' not in database.name:
            self.database = database['commits']

        self.api_url = 'https://api.github.com/repos/'
        self.apiCall = APICallHandler()

    def collect_batch(self, save: bool = True):
        """
        Collect several groups of 30 elements returned by the API until the pages return an empty JSON
        :param save: if it should persist the json downloaded on the hard drive
        :type save: bool
        :return: list of elements returned by the API
        :rtype: list
        """
        page = 1
        commits = []
        request_url = self.api_url + self.owner + '/' + self.repo + '/commits?page='
        while True:
            commit_batch = self.apiCall.request(request_url + str(page))
            if not commit_batch:
                break

            commits.append(commit_batch)
            for commit in commit_batch:
                if self.database.find_one({'sha': commit['sha']}):
                    return commits

            page = page + 1

        return commits

    def collect_single(self, sha: str):
        """
        Collect a single element of the API
        :param sha: parameter that will be used by the function to know which element it should download
        :type sha: str
        :return: json downloaded
        :rtype: dict
        """

        commit = self.database.find_one({'sha': sha})
        if commit:
            return False

        commit = self.apiCall.request(self.api_url + self.owner + '/' + self.repo + '/commits/' + sha)

        if commit:
            self.database.insert_one(commit)
            return True
        else:
            print('Empty JSON of ' + sha)

        return False
