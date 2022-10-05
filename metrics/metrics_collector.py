#!/usr/bin/env python
"""
This class is responsible for running the metrics implemented and compile the data in a CSV.
"""

from metrics.implementation.developer_status import DeveloperStatus
from metrics.implementation.discussion_duration import DiscussionLength
from metrics.implementation.mean_time_between_replies import TimeBetweenReplies
from metrics.implementation.developers_number_of import NumberComments
from metrics.implementation.number_of_patches import NumberSnippets
from metrics.implementation.opened_employment import OpenedByEmployeeOrTemporary
from metrics.implementation.words_in_discussion import WordsInDiscussion
from utils.csv_handler import CSVHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"


class MetricsCollector:

    def __init__(self, path: str, project: str):
        self.project = project
        self.path = path

    def run_metrics(self, metrics: list = ['number_of_users', 'number_of_contributors',
                                           'number_of_core_members', 'opened_by', 'median_comments',
                                           'words_in_discussion', 'words_in_discussion_per_comment',
                                           'number_of_snippets', 'snippets_size',
                                           'mean_time_between_comments',
                                           'discussion_length']):
        """
        Run the implementation of each metric based on the input list of metrics desired.

        :param metrics: list of metrics that should be executed
        :type metrics: list
        :return: list with the length of each CSV generated (number of lines, header included).
        :rtype: list
        """
        print('Running metrics for ' + self.project + ' project.\n')
        output = []

        if 'number_of_users' in metrics:
            number_users = DeveloperStatus(self.project)
            output.append(len(number_users.number_of_users()))

        if 'number_of_contributors' in metrics:
            number_contri = DeveloperStatus(self.project)
            output.append(len(number_contri.number_of_contributors()))

        if 'number_of_core_members' in metrics:
            number_core = DeveloperStatus(self.project)
            output.append(len(number_core.number_of_core_devs()))

        if 'opened_by' in metrics:
            opened_by = OpenedByEmployeeOrTemporary(self.project)
            output.append(len(opened_by.opened_employee_or_temporary()))

        if 'median_comments' in metrics:
            median_comments = NumberComments(self.project)
            output.append(len(median_comments.get_median_of_number_of_comments()))

        if 'words_in_discussion' in metrics:
            words_discussion = WordsInDiscussion(self.project)
            output.append(len(words_discussion.get_words_in_discussion()))

        if 'words_in_discussion_per_comment' in metrics:
            words_discussion = WordsInDiscussion(self.project)
            output.append(len(words_discussion.get_words_per_comment_in_discussion()))

        if 'number_of_snippets' in metrics:
            number_of_patches = NumberSnippets(self.project)
            output.append(len(number_of_patches.get_number_of_patches()))

        if 'snippets_size' in metrics:
            snippets_size = NumberSnippets(self.project)
            output.append(len(snippets_size.get_patch_size()))

        if 'mean_time_between_comments' in metrics:
            mean_time = TimeBetweenReplies(self.project)
            output.append(len(mean_time.mean_time_between_replies()))

        if 'discussion_length' in metrics:
            discussion_length = DiscussionLength(self.project)
            output.append(len(discussion_length.get_time_in_days_between_open_and_close()))

        return output

    def compile_data(self):
        """
        Collect all the metrics CSV generated and compile in a final CSV with all metrics together by Pull Request/Issue

        :return: list with the lines from the generated CSV
        :rtype: list
        """
        path = self.path + self.project

        output = [['id',
                   'number_comments', 'number_users',
                   'number_contributors', 'number_core_devs',
                   'opened_by', 'number_of_patches',
                   'words_in_discussion'
                   'words_per_comment_in_discussion',
                   'snippets_size',
                   'mean_time_between_replies',
                   'discussion_length'
                   ]]

        csv = CSVHandler()

        number_comments = csv.open_csv_as_dict(path + '/metrics/' +
                                               self.project + '_number_comments.csv')

        number_users = csv.open_csv_as_dict(path + '/metrics/' +
                                            self.project + '_number_of_users.csv')

        number_contributors = csv.open_csv_as_dict(path + '/metrics/' +
                                                   self.project + '_number_of_contributors.csv')

        number_core_developers = csv.open_csv_as_dict(path + '/metrics/' +
                                                      self.project + '_number_of_core_developers.csv')

        opened_by = csv.open_csv_as_dict(path + '/metrics/' +
                                         self.project + '_opened_by.csv')

        number_of_patches = csv.open_csv_as_dict(path + '/metrics/' +
                                                 self.project + '_patches_in_discussion.csv')

        words = csv.open_csv_as_dict(path + '/metrics/' +
                                     self.project + '_words_in_discussion.csv')

        words_per_comment_in_discussion = csv.open_csv_as_dict(path + '/metrics/' +
                                                               self.project + '_words_per_comments_in_discussion.csv')
        snippets_size = csv.open_csv_as_dict(path + '/metrics/' +
                                             self.project + '_patches_size_in_discussion.csv')
        mean_time_between_replies = csv.open_csv_as_dict(path + '/metrics/' +
                                                         self.project + '_mean_time_between_replies.csv')
        discussion_length = csv.open_csv_as_dict(path + '/metrics/' +
                                                 self.project + '_discussion_length.csv')

        for key in discussion_length.keys():
            discussion_length[key] = discussion_length[key][0]

        employees = {}
        temporaries = {}
        for key in opened_by.keys():
            opened = opened_by[key]
            emp = 0
            temp = 0
            for open in opened:
                if 'employee' in open:
                    emp = 1
                elif 'temporary' in open:
                    temp = 1

            employees[key] = emp
            temporaries[key] = temp

        keys = number_comments.keys()

        unique = []
        for k in keys:
            unique.append(k)

        for k in unique:

            comments = number_comments.get(k, None)
            if not comments:
                continue

            line = [k,
                    number_comments.get(k, 0),
                    number_users.get(k, 0),
                    number_contributors.get(k, 0),
                    number_core_developers.get(k, 0),
                    opened_by.get(k, None)[0],
                    number_of_patches.get(k, 0),
                    words.get(k, 0),
                    words_per_comment_in_discussion.get(k, 0),
                    snippets_size.get(k, 0),
                    mean_time_between_replies.get(k, 0),
                    discussion_length.get(k, 0)
                    ]

            flag = False
            for col in line:
                if col is None:
                    flag = True

            if flag:
                continue

            output.append(line)

        csv.write_csv(path + '/' + self.project + '/', self.project + '_all_metrics.csv', output)

        return output

