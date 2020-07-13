from api.dao.dao_interface import DAOInterface
from api.dao.labelDAO import LabelDAO

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class IssueDAO(DAOInterface):

    def __init__(self):
        self.id = -1
        self.issue_number = -1
        self.state = ""
        self.title = ""
        self.body = ""
        self.locked = False
        self.user = ''
        self.labels = []
        self.assignees = []
        self.comments = 0
        self.created_at = ""
        self.updated_at = ""
        self.closed_at = ""
        self.author_association = ""
        self.pull_request = False
        self.closed_by = ''

    def read_from_json(self, issue: dict):
        """
        Filters the GitHub API JSON to collect only the proposed fields.

        :param issue: json containing the issue object from the GitHub API
        :type issue: dict
        """
        self.id = issue['id']
        self.issue_number = issue['number']
        self.state = issue['state']
        self.title = issue['title']
        self.body = issue['body']
        self.locked = issue['locked']

        if issue['user']:
            self.user = issue['user']['login']

        if issue['labels']:
            self.labels = []
            for labelJSON in issue['labels']:
                label = LabelDAO()
                label.read_from_json(labelJSON)
                self.labels.append(label.__dict__)

        if issue['assignees']:
            self.assignees = []
            for userJSON in issue['assignees']:
                self.assignees.append(userJSON['login'])

        self.comments = issue['comments']
        self.created_at = issue['created_at']
        self.updated_at = issue['updated_at']
        self.closed_at = issue['closed_at']
        self.author_association = issue['author_association']

        if 'pull_request' in issue.keys():
            self.pull_request = True

        if issue['closed_by']:
            self.closed_by = issue['closed_by']['login']
