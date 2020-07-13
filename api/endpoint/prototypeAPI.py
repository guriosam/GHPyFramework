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

        :param save:
        :type save:
        :return:
        :rtype:
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
