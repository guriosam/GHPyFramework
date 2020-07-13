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

    def __init__(self, owner, repo):
        super()
        self.owner = owner
        self.repo = repo
        config = JSONHandler('../').open_json('config.json')
        self.path = config['output_path']
        self.apiHandler = APICallHandler()

    def collect_batch(self, save: bool = True):
        """

        :param save:
        :type save:
        :return:
        :rtype:
        """
        request_url = self.api_url + self.owner + '/' + self.repo + '/pulls?state=all&page='
        page = 1 
        pulls = []
        json = JSONHandler(self.path + self.repo + '/pulls/all/')
        while True:
            if json.file_exists(self.path + self.repo + '/pulls/all/' + str(page) + '.json'):
                page = page + 1
                continue

            pull_batch = self.apiHandler.request(request_url + str(page))

            if pull_batch:
                json.save_json(pull_batch, str(page))
                pulls.append(pull_batch)
                page = page + 1
            else:
                break

        return pulls

    def collect_single(self, number):
        """

        :param number:
        :type number:
        :return:
        :rtype:
        """
        json = JSONHandler(self.path + self.repo + '/pulls/individual/')

        if json.file_exists(self.path + self.repo + '/pulls/individual/' + str(number) + '.json'):
            return JSONHandler(self.path + self.repo + '/pulls/individual/').open_json(str(number) + '.json')

        pull = self.apiHandler.request(self.api_url + self.owner + '/' + self.repo + '/pulls/' + str(number))
        if pull:
            json.save_json(pull, str(number))
        else:
            print('Empty JSON of ' + str(number))

        return pull
