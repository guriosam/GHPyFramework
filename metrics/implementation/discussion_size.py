from pymongo.database import Database
from utils.date import DateUtils


__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class DiscussionSize:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database

    def get_discussion_size(self, issue: bool = True, pull: bool = True):
        """
        Collects the time in days between the day an issue or pull request was opened and the day it was closed.
        """
        print('#### Discussion Size ####')

        database = self.database

        if issue:
            database = self.database['issues']

        if pull:
            database = self.database['pull_requests']

        query_result = database.find({"merged": True})

        for pull_request in query_result:

            if self.database['metrics'].find_one({"issue_number": pull_request['number']}):
                self.database['metrics'].update_one({"issue_number": pull_request['number']},
                                                        {"$set":{"discussion_size": pull_request['comments']}})

                continue

            self.database['metrics'].insert_one(
                {"issue_number": pull_request['number'], "discussion_size": pull_request['comments']})

