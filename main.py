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

from metrics.implementation.gendercomputer import GenderDiversity
from metrics.implementation.team_size import teamSize



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

            NumberOf(project_owner, project_name, database).fix_merged_prs()

            DiscussionDuration(project_owner, project_name, database).get_time_in_days_between_open_and_close(issue=False)
            DiscussionSize(project_owner, project_name, database).get_discussion_size(issue=False)
            DeveloperStatus(project_owner, project_name, database).user_profiling()

            #NumberSnippets(project_owner, project_name, database).get_snippet_metrics()

            TimeBetweenReplies(project_owner, project_name, database).mean_time_between_replies()
            TimeBetweenReplies(project_owner, project_name, database).mean_time_between_open_and_first_last_and_merge()

            # User Metrics
            self._run_user_metrics(project_owner, project_name, database)

            print("________________________")

    def collect_merged_commits_subset(self):

        commits_subsets = {}
        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            merged_commits = set()
            database_commits = database['commits']
            database_prs = database['pull_requests']
            regex = '#[0-9]*'
            for commit in database_commits.find({'commit.message': {'$regex': regex}}):
                if commit['sha']:
                    merged_commits.add(commit['sha'])

            for pull_request in database_prs.find({'merge_commit_sha': {'$ne': None}}):
                if pull_request['merge_commit_sha']:
                    merged_commits.add(pull_request['merge_commit_sha'])

            commits_subsets[project_name] = list(merged_commits)

        with open('merged_commits.json', 'w') as f:
            json.dump(commits_subsets, f, indent=4)

    def sample_refactoring_and_design_messages(self):

        comments = {}

        keywords = ['refactor', 'split', 'introduc', 'fix', 'decompos', 'reorganiz', 'mov', 'extract', 'merg', 'renam',
                    'chang', 'restructur', 'format', 'extend', 'rewrite', 'replace', 'simplif', 'recreat', 'improv',
                    'add', 'modif', 'enhanc', 'rework', 'inlin', 'redesign', 'clean', 'reduc', 'encapsulat']

        output = []

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']


            database = self.mongo_connection[project_owner + '-' + project_name]

            for keyword in keywords:
                count = 0
                for comment in database['comments'].find({'body': {'$regex': keyword}}):
                    output.append(
                        {
                            'project': project_name,
                            'id': comment['id'],
                            'body': comment['body'],
                            'url': comment['html_url']
                        }
                    )

                    count += 1

                    if count > 5:
                        break

        sample1 = random.sample(output, 200)
        sample2 = random.sample(output, 200)

        with open('comments_1.json', 'w') as f:
            json.dump(sample1, f, indent=4)

        with open('comments_2.json', 'w') as f:
            json.dump(sample2, f, indent=4)

            #comments[project_name] = list(comments[project_name])

    def import_refactorings(self):
        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            refact = RefactoringManager(project_owner, project_name, database)
            refact.run()

    @staticmethod
    def _run_user_metrics(project_owner, project_name, database):

        DeveloperStatus(project_owner, project_name, database).turnover()
        DeveloperStatus(project_owner, project_name, database).experience()

        NumberOf(project_owner, project_name, database).get_commits_by_file_type()
        NumberOf(project_owner, project_name, database).get_number_of_reviews_by_developer()
        NumberOf(project_owner, project_name, database).get_mean_between_merged_prs_by_user()
        NumberOf(project_owner, project_name, database).get_labels_rank_by_user()
        NumberOf(project_owner, project_name, database).get_number_of_prs_opened_by_user()
        NumberOf(project_owner, project_name, database).get_number_of_prs_closed_by_user()
        NumberOf(project_owner, project_name, database).get_number_of_comments_by_user()
        NumberOf(project_owner, project_name, database).get_number_of_commits_by_user()
        NumberOf(project_owner, project_name, database).get_size_of_commits_by_user()
        NumberOf(project_owner, project_name, database).get_number_of_merged_prs_by_user()
        NumberOf(project_owner, project_name, database).get_number_of_words_comments_by_user()

    def test_gender_metric(self):

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            users_list = GenderDiversity(database).gender()
            users_json = APICollector(database).collect_users('Netflix', 'zuul', users_list)
            user_info = GenderDiversity(database).gender_extraction()

    def test_team_user_metric(self):
        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            team_user = teamSize(database).teste()


#Number of Reviews by the developer
#Number of lines revised by the developer
#Number of Files revised by developer
#Number of Modules revised by developer
#Number of Commits by type of file (.java, .xml)

main = Main()
#main.test_gender_metric()
#main.run_collector()
#main.run_metrics()
main.test_team_user_metric()

#main.output_results_oliveira()
#main.collect_merged_commits_subset()

#main.sample_refactoring_and_design_messages()

#main.import_refactorings()

