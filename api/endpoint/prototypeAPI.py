from api.endpoint.api_interface import APIInterface
from utils.api_call_handler import APICallHandler
from utils.json_handler import JSONHandler


class PrototypeAPI(APIInterface):

    def __init__(self, owner: str = '', repo: str = '', private_path: str = '', private_url: str = ''):
        self.owner = owner
        self.repo = repo
        self.api_url = 'https://api.github.com/repos/'
        config = JSONHandler('../').open_json('config.json')
        self.path = config['output_path']
        self.apiHandler = APICallHandler()
        self.private_path = private_path
        self.private_url = private_url

    def collect_batch(self, save: bool = True):
        """
        Collect several groups of 30 elements returned by the API until the pages return an empty JSON
        :param save: if it should persist the json downloaded on the hard drive
        :type save: bool
        :return: list of elements returned by the API
        :rtype: list
        """
        request_url = self.api_url + self.owner + '/' + self.repo + self.private_url + '?page='
        path = self.path + self.repo + self.private_path + 'all/'
        page = 1
        data_list = []
        json = JSONHandler(path)
        while True:
            if json.file_exists(path + str(page) + '.json'):
                page = page + 1
                continue

            data = self.apiHandler.request(request_url + str(page))

            if not data:
                break

            data_list.append(data)

            if save:
                json.save_json(data, str(page))
            page = page + 1

        return data_list

    def collect_single(self, parameter: str, save: bool = True):
        """
        Collect a single element of the API
        :param parameter: parameter that will be used by the function to know which element it should download
        :type parameter: str
        :param save: if it should persist the json downloaded on the hard drive
        :type save: bool
        :return: json downloaded
        :rtype: dict
        """
        path = self.path + self.repo + self.private_path + 'individual/'
        json = JSONHandler(path)

        if json.file_exists(path + str(parameter) + '.json'):
            return JSONHandler(path).open_json(str(parameter) + '.json')

        request_url = self.api_url + self.owner + '/' + self.repo + self.private_url + '/' + str(parameter)
        data = self.apiHandler.request(request_url)
        if not data:
            print('JSON returned empty. Please check your parameters for URL: ' + request_url)
            data = []

        if save:
            json.save_json(data, str(parameter))

        return data
