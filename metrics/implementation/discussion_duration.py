from pymongo.database import Database
from utils.date import DateUtils


__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class DiscussionDuration:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database

    def get_time_in_days_between_open_and_close(self, issue: bool = True, pull: bool = True):
        """
        Collects the time in days between the day an issue or pull request was opened and the day it was closed.
        """
        print('#### Discussion Duration ####')

        database = self.database

        if issue:
            database = self.database['issues']

        if pull:
            database = self.database['pull_requests']

        query_result = database.find({"state": "closed"})


        for pull_request in query_result:
            merged = pull_request['created_at']
            if 'merged_at' in pull_request.keys() and pull_request['merged_at']:
                merged = pull_request['merged_at']

            delta = DateUtils().get_days_between_dates(pull_request['created_at'], merged)
            if delta < 0:
                delta = delta * -1
            delta += 1

            if self.database['metrics'].find_one({"issue_number": pull_request['number']}):
                self.database['metrics'].update_one({"issue_number": pull_request['number']},
                                                    {
                                                        "$set": {
                                                            "discussion_duration": delta
                                                        }
                                                    }
                                                    )
                continue

            self.database['metrics'].insert_one({"issue_number": pull_request['number'],
                                                 "discussion_duration": delta})
