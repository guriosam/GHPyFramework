import json
import random
import re

from pymongo import MongoClient

from api.api_collector import APICollector
from metrics.implementation.developer_status import DeveloperStatus
from metrics.implementation.developers_number_of import NumberOf
from metrics.implementation.discussion_duration import DiscussionDuration
from metrics.implementation.discussion_size import DiscussionSize
from metrics.implementation.mean_time_between_replies import TimeBetweenReplies
from metrics.implementation.number_of_patches import NumberSnippets
from refactorings.refactoring import RefactoringManager
from utils.csv_handler import CSVHandler
from utils.date import DateUtils
from utils.json_handler import JSONHandler


class Main:

    def __init__(self):
        json_handler = JSONHandler('./')
        self.config = json_handler.open_json('config_dev.json')
        self.projects = self.config['projects']
        self.mongo_connection = MongoClient("mongodb://localhost:27017/")

    def run_collector(self):


        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            collector = APICollector(database)

            collector.collect_issues(project_owner, project_name)
            collector.collect_pulls(project_owner, project_name)
            collector.collect_commits(project_owner, project_name)
            collector.collect_comments(project_owner, project_name)
            collector.collect_comments_pulls(project_owner, project_name)

    def run_metrics(self):

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            print('###########' + project_name + '############\n')

            #NumberOf(project_owner, project_name, database).fix_merged_prs()

            #self.fix_prs_in_mongo()

            #DiscussionDuration(project_owner, project_name, database).get_time_in_days_between_open_and_close(issue=False)
            #DiscussionSize(project_owner, project_name, database).get_discussion_size(issue=False)
            #DeveloperStatus(project_owner, project_name, database).user_profiling()

            #NumberSnippets(project_owner, project_name, database).get_snippet_metrics()

            #TimeBetweenReplies(project_owner, project_name, database).mean_time_between_replies()
            #TimeBetweenReplies(project_owner, project_name, database).mean_time_between_open_and_first_last_and_merge()

            # User Metrics - Oliveira
            #self._run_user_metrics(project_owner, project_name, database)

            print("________________________")

    @staticmethod
    def _run_user_metrics(project_owner, project_name, database):

        #DeveloperStatus(project_owner, project_name, database).turnover()
        #DeveloperStatus(project_owner, project_name, database).experience()

        NumberOf(project_owner, project_name, database).get_commits_by_file_type()
        NumberOf(project_owner, project_name, database).get_number_of_reviews_by_developer()
        #NumberOf(project_owner, project_name, database).get_mean_between_merged_prs_by_user()
        #NumberOf(project_owner, project_name, database).get_labels_rank_by_user()
        #NumberOf(project_owner, project_name, database).get_number_of_prs_opened_by_user()
        #NumberOf(project_owner, project_name, database).get_number_of_prs_closed_by_user()
        #NumberOf(project_owner, project_name, database).get_number_of_comments_by_user()
        #NumberOf(project_owner, project_name, database).get_number_of_commits_by_user()

        #NumberOf(project_owner, project_name, database).get_size_of_commits_by_user()
        #NumberOf(project_owner, project_name, database).get_number_of_merged_prs_by_user()
        #NumberOf(project_owner, project_name, database).get_number_of_words_comments_by_user()

#Number of Reviews by the developer
#Number of lines revised by the developer
#Number of Files revised by developer
#Number of Modules revised by developer
#Number of Commits by type of file (.java, .xml)

main = Main()
#main.run_collector()
#main.run_metrics()


