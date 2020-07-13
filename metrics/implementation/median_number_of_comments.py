from os import listdir
from os.path import isfile, join
from statistics import median

from utils.csv_handler import CSVHandler
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class NumberComments:

    def __init__(self, project):
        config = JSONHandler('../').open_json('config.json')
        self.project = project
        self.path = config['output_path']

    def get_median_of_number_of_comments(self):
        """
        Collects the median of the number of comments inside an issue or pull requests
        :return: list with the median of the number of comments per issue or pull request
        :rtype: list
        """
        print("#### Median Comments ####")

        mypath = self.path + self.project + '/comments/individual/'
        json = JSONHandler(mypath)

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        comments_per_issue = {}
        for file in onlyfiles:
            comments = json.open_json(file)
            for comment in comments:
                if 'issue_url' in comment.keys():
                    issue = comment['issue_url'].split('/')
                    issue = issue[len(issue) - 1]
                    if int(issue) not in comments_per_issue:
                        comments_per_issue[int(issue)] = 0
                    comments_per_issue[int(issue)] = comments_per_issue[int(issue)] + 1

        values = []
        median_comments = [['issue', 'median_comments']]
        number_comments = [['id', 'number_comments']]


        for key in sorted(comments_per_issue):
            #print(str(key) + ': ' + str(comments_per_issue[key]))
            values.append(comments_per_issue[key])
            median_comments.append([key, median(values)])
            number_comments.append([key, comments_per_issue[key]])

        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_median_comments.csv',
                      median_comments)

        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_number_comments.csv',
                      number_comments)

        return number_comments


