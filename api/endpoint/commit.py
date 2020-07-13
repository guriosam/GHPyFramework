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

    def __init__(self, owner : str, repo : str):
        self.owner = owner
        self.repo = repo
        config = JSONHandler('../').open_json('config.json')
        self.path = config['output_path']
        self.api_url = 'https://api.github.com/repos/'
        self.apiCall = APICallHandler()

    def collect_batch(self, save : bool = True):
        """
        Collect several groups of 30 elements returned by the API until the pages return an empty JSON
        :param save: if it should persist the json downloaded on the hard drive
        :type save: bool
        :return: list of elements returned by the API
        :rtype: list
        """
        page = 1
        commits = []
        json = JSONHandler(self.path + self.repo + '/commits/all/')

        while True:
            if json.file_exists(self.path + self.repo + '/commits/all/' + str(page) + '.json'):
                page = page + 1
                continue

            request_url = self.api_url + self.owner + '/' + self.repo + '/commits?page=' + str(page)
            commit_batch = self.apiCall.request(request_url)
            if not commit_batch:
                break

            if save:
                json.save_json(commit_batch, str(page))
            for commit in commit_batch:
                commits.append(commit['sha'])
            page = page + 1

        return commits

    def collect_single(self, sha : str):
        """
        Collect a single element of the API
        :param sha: parameter that will be used by the function to know which element it should download
        :type sha: str
        :return: json downloaded
        :rtype: dict
        """
        json = JSONHandler(self.path + self.repo + '/commits/individual/')

        if json.file_exists(self.path + self.repo + '/commits/individual/' + sha + '.json'):
            try:
                return JSONHandler(self.path + self.repo + '/commits/individual/').open_json(str(sha) + '.json')
            except:
                return {}

        commit = self.apiCall.request(self.api_url + self.owner + '/' + self.repo + '/commits/' + sha)

        if commit:
            json.save_json(commit, sha)
        else:
            print('Empty JSON of ' + sha)

        return commit
