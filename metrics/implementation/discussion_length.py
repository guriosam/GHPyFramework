from pymongo.database import Database

from utils.csv_handler import CSVHandler
from utils.date import DateUtils
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"


class DiscussionLength:

    def __init__(self, database: Database):
        self.database = database

    def get_time_in_days_between_open_and_close(self):
        """
        Collects the time in days between the day an issue or pull request was opened and the day it was closed.
        :return: list of time in days per issue/pull request.
        :rtype: list
        """
        print('#### Discussion Length ####')

        issues = self.database['issues'].find({'state': 'closed'})
        pulls = self.database['pull_requests'].find({'state': 'merged'})

        days_between = [['number', 'status']]

        date_utils = DateUtils()
        for issue in issues:
            days = 0

            if 'closed' in issue['state']:
                days = date_utils.get_days_between_dates(issue['created_at'], issue['closed_at'])
                # print(issue['author_association'])
                self.database['metrics'].insert_one(
                    {'pull_request_id': issue['number'], 'days_between_open_and_close': days})

        for pull in pulls:
            days = 0
            if 'closed' in pull['state']:
                if pull['merged_at']:
                    days = date_utils.get_days_between_dates(pull['created_at'], pull['merged_at'])
                else:
                    days = date_utils.get_days_between_dates(pull['created_at'], pull['closed_at'])

                self.database['metrics'].insert_one(
                    {'pull_request_id': pull['number'], 'days_between_open_and_close': days})


        return self.database['metrics'].find({'days_between_open_and_close': {'$ne': None}})
