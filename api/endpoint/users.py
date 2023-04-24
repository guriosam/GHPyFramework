from pymongo.database import Database

from api.endpoint.api_interface import APIInterface
from utils.api_call_handler import APICallHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"


class UsersAPI(APIInterface):

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo

        self.database = database

        if 'users_api' not in database.name:
            self.database = database['users_api']

        self.api_url = 'https://api.github.com/'
        self.apiCall = APICallHandler()

    def collect_batch(self, review: bool = False, save: bool = True):
        """
        Collect several groups of 30 elements returned by the API until the pages return an empty JSON
        :param save: if it should persist the json downloaded on the hard drive
        :type save: bool
        :return: list of elements returned by the API
        :rtype: list
        """
        return []

    def collect_single(self, login: str):
        """
        Collect a single element of the API
        :param login: parameter that will be used by the function to know which element it should download
        :type login: str
        :return: json downloaded
        :rtype: dict
        """

        print("******* User login " + str(login) + " *********")

        user = self.database.find_one({'login': login})
        if user:
            print('User ' + str(login) + ' already in the database')
            return user

        user = self.apiCall.request(self.api_url + 'users/' + login)

        if user:
            self.database.insert_one(user)
            print('User ' + str(login) + ' saved')
            return self.database.find_one({'login': login})
        else:
            print('Empty JSON of ' + login)

        return user