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

    def __init__(self, owner: str, repo: str):
        super()
        self.owner = owner
        self.repo = repo
        self.api_url = 'https://api.github.com/repos/'
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
        request_url = self.api_url + self.owner + '/' + self.repo + '/issues/comments?page='
        path = self.path + self.repo + '/comments/issues/all/'
        page = 1
        comments = []
        json = JSONHandler(path)
        while True:
            if json.file_exists(path + str(page) + '.json'):
                page = page + 1
                continue

            comment_batch = self.apiHandler.request(request_url + str(page))
            if not comment_batch:
                break

            comments.append(comment_batch)
            if save:
                json.save_json(comment_batch, str(page))
            page = page + 1

        return comments

    def collect_single(self, issue_number: str):
        path = self.path + self.repo + '/comments/individual/'
        json = JSONHandler(path)
        page = 1

        issue_number = issue_number.split('/')
        issue_number = issue_number[len(issue_number) - 1]

        comments = []
        while True:

            if json.file_exists(path + str(issue_number) + '_' + str(page) + '.json'):
                comment = json.open_json(str(issue_number) + '_' + str(page) + '.json')
                for cmt in comment:
                    comments.append(cmt)
                page = page + 1
                continue

            request_url = self.api_url + self.owner + '/' + self.repo + '/issues/' + str(issue_number) + \
                          '/comments?page=' + str(page)
            comment = self.apiHandler.request(request_url)

            if not comment:
                break

            json.save_json(comment, str(issue_number) + '_' + str(page))
            page = page + 1
            for cmt in comment:
                comments.append(cmt)


        return comments
