from os import listdir
from os.path import isfile, join

from utils.csv_handler import CSVHandler
from utils.json_handler import JSONHandler
from utils.date import DateUtils

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class TimeBetweenReplies:

    def __init__(self, project: str):
        config = JSONHandler('../').open_json('config.json')
        self.project = project
        self.path = config['output_path']

    def mean_time_between_replies(self):
        """
        Collect the mean time between comments inside an issue or pull request
        :return: list if mean time between comments per issue/pull request
        :rtype: list
        """
        print('#### Mean Time Between Comments ####')

        mypath = self.path + self.project + '/comments/individual/'
        json = JSONHandler(mypath)
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        comments_per_issue = {}

        for file in onlyfiles:
            comments = json.open_json(file)

            for comment in comments:
                issue = comment['issue_url'].split('/')
                issue = issue[len(issue) - 1]

                if issue not in comments_per_issue.keys():
                    comments_per_issue[issue] = []

                comments_per_issue[issue].append(comment['created_at'])

        date_utils = DateUtils()
        mean_time = [['issue', 'mean_time']]
        for key in comments_per_issue.keys():
            days_between = []
            sorted_dates = date_utils.sort_dates(comments_per_issue[key])
            aux = None
            for date in sorted_dates:
                if not aux:
                    aux = date
                    continue

                days = date_utils.get_days_between_dates(aux, date)
                days_between.append(days)
                aux = date

            length = len(days_between)

            length += 1

            sum_days = sum(days_between)
            mean_days = sum_days / length
            mean_time.append([key, mean_days])

        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_mean_time_between_replies.csv',
                      mean_time)

        return mean_time