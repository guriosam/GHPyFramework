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


class PullsAPI(APIInterface):
    api_url = 'https://api.github.com/repos/'

    def __init__(self, owner, repo, database: Database):
        super()
        self.owner = owner
        self.repo = repo

        self.root_database = database
        self.database = database

        if 'pull_requests' not in database.name:
            self.database = database['pull_requests']

        self.apiHandler = APICallHandler()

    def collect_batch(self, review: bool = False, save: bool = True):
        """
        Collect several groups of 30 elements returned by the API until the pages return an empty JSON
        :param save: if it should persist the json downloaded on the hard drive
        :type save: bool
        :return: list of elements returned by the API
        :rtype: list
        """
        request_url = self.api_url + self.owner + '/' + self.repo + '/pulls?state=all&page='
        page = 1
        pulls = []

        while True:
            pull_batch = self.apiHandler.request(request_url + str(page))
            if pull_batch:
                pulls.append(pull_batch)

                for pull in pull_batch:
                    if self.database.find_one({'number': pull['number']}):
                        continue

                page = page + 1
            else:
                break

        return pulls

    def collect_single(self, number: str):
        """
        Collect a single element of the API
        :param number: parameter that will be used by the function to know which element it should download
        :type number: str
        :return: json downloaded
        :rtype: dict
        """


        print("******* Pull request number " + str(number) + " *********")

        pull = self.database.find_one({'number': number})

        issue = self.root_database['issues'].find_one({'number': number})

        if issue:
            self.root_database['issues'].remove({'number': number})

        if pull:
            print('PR ' + str(number) + ' already in the database')
            return pull

        pull = self.apiHandler.request(self.api_url + self.owner + '/' + self.repo + '/pulls/' + str(number))
        if pull:
            self.database.insert_one(pull)
            print('PR ' + str(number) + ' saved')
            return self.database.find_one({'number': number})
        else:
            print('Empty JSON of ' + str(number))

        return pull

