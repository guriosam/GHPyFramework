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

    def __init__(self, project: str):
        config = JSONHandler('../').open_json('config.json')
        self.project = project
        self.path = config['output_path']

    def get_time_in_days_between_open_and_close(self):
        """
        Collects the time in days between the day an issue or pull request was opened and the day it was closed.
        :return: list of time in days per issue/pull request.
        :rtype: list
        """
        print('#### Discussion Length ####')

        path = self.path + '/' + self.project
        json = JSONHandler(path + '/')
        issues = json.open_json(self.project + '_issues.json')
        pulls = json.open_json(self.project + '_pulls.json')

        days_between = [['number', 'status']]

        date_utils = DateUtils()
        for issue in issues:
            days = 0

            if 'closed' in issue['state']:
                days = date_utils.get_days_between_dates(issue['created_at'], issue['closed_at'])
                # print(issue['author_association'])
                days_between.append(
                    [issue['issue_number'], days])

        for pull in pulls:
            days = 0
            if 'closed' in pull['state']:
                if pull['merged_at']:
                    days = date_utils.get_days_between_dates(pull['created_at'], pull['merged_at'])
                else:
                    days = date_utils.get_days_between_dates(pull['created_at'], pull['closed_at'])

                days_between.append(
                    [pull['pull_request_number'], days])

        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_discussion_length.csv',
                      days_between)

        return days_between
