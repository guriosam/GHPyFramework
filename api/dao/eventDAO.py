from api.dao.dao_interface import DAOInterface

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class EventDAO(DAOInterface):

    def __init__(self):
        self.id = -1
        self.issue_number = -1
        self.event = ""
        self.user = ''
        self.label = ""
        self.created_at = ""
        self.commit_id = ''

    def read_from_json(self, event: dict):
        """
        Filters the GitHub API JSON to collect only the proposed fields.

        :param event: json containing the event object from the GitHub API
        :type event: dict
        """
        self.id = event['id']
        self.issue_number = event['issue']['number']
        self.event = event['event']
        self.user = event['actor']['login']
        if 'label' in event.keys():
            self.label = event['label']

        self.created_at = event['created_at']
        if 'commit_id' in event.keys():
            self.commit_id = event['commit_id']
