from api.endpoint.api_interface import APIInterface
from utils.api_call_handler import APICallHandler
from utils.json_handler import JSONHandler

class IssueAPI(APIInterface):

    def __init__(self, owner : str, repo : str):
        config = JSONHandler('../').open_json('config.json')
        self.owner = owner
        self.repo = repo
        self.path = config['output_path']
        self.apiHandler = APICallHandler()
        self.api_url = 'https://api.github.com/repos/'

    def collect_batch(self, save : bool = False):
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
        json = JSONHandler(self.path + self.repo + '/issues/all/')
        while True:
            if json.file_exists(self.path + self.repo + '/issues/all/' + str(page) + '.json'):
                page = page + 1
                continue

            issue_batch = self.apiHandler.request(request_url + str(page))
            if issue_batch:
                issues.append(issue_batch)
                if save:
                    json.save_json(issue_batch, str(page))
                page = page + 1
            else:
                break

        return issues

    def collect_single(self, number : str):
        """
        Collect a single element of the API
        :param number: parameter that will be used by the function to know which element it should download
        :type number: str
        :return: json downloaded
        :rtype: dict
        """
        json = JSONHandler(self.path + self.repo + '/issues/individual/')

        if json.file_exists(self.path + self.repo + '/issues/individual/' + str(number) + '.json'):
            return JSONHandler(self.path + self.repo + '/issues/individual/').open_json(str(number) + '.json')

        issue = self.apiHandler.request(self.api_url + self.owner + '/' + self.repo + '/issues/' + str(number))
        if issue:
            json.save_json(issue, str(number))
        else:
            print('Empty JSON of ' + str(number))

        return issue

