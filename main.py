import json
import os
import random
import re
from bson import json_util

import numpy as np
import pandas as pd
from numpy import NaN
from pymongo import MongoClient

from api.api_collector import APICollector
from metrics.implementation.developer_status import DeveloperStatus
from metrics.implementation.developers_number_of import NumberOf
from metrics.implementation.discussion_duration import DiscussionDuration
from metrics.implementation.discussion_size import DiscussionSize
from metrics.implementation.gender import GenderDiversity
from metrics.implementation.keywords import Keywords
from metrics.implementation.mean_time_between_replies import TimeBetweenReplies
from metrics.implementation.number_of_patches import NumberSnippets
from metrics.implementation.team_size import TeamSize
from refactorings.refactoring import RefactoringManager
from smells_main import SmellsMain
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
            print(project_name)

            database = self.mongo_connection[project_owner + '-' + project_name]

            collector = APICollector(project_name, database)

            collector.collect_issues(project_owner, project_name)
            collector.collect_pulls(project_owner, project_name)
            collector.collect_commits(project_owner, project_name)

            collector.collect_comments(project_owner, project_name)
            collector.collect_comments_pulls(project_owner, project_name)
            collector.collect_users(project_owner, project_name)

    def pre_processing_data_before_metrics(self):
        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]
            NumberOf(project_owner, project_name, database).fix_merged_prs()

    def run_metrics(self):

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            print('###########' + project_name + '############\n')

            DiscussionDuration(project_owner, project_name, database).get_time_in_days_between_open_and_close(
                issue=False)
            DiscussionSize(project_owner, project_name, database).get_discussion_size(issue=False)
            DeveloperStatus(project_owner, project_name, database).user_profiling()

            NumberSnippets(project_owner, project_name, database).get_snippet_metrics()

            TimeBetweenReplies(project_owner, project_name, database).mean_time_between_replies()
            TimeBetweenReplies(project_owner, project_name, database).mean_time_between_open_and_first_last_and_merge()

            Keywords(database).get_pr_keywords()

            TeamSize(database).get_team()
            gender = GenderDiversity(database)
            gender.gender_extraction()
            gender.team_gender()
            # User Metrics
            # self._run_user_metrics(project_owner, project_name, database)

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

            # comments[project_name] = list(comments[project_name])

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

        # NumberOf(project_owner, project_name, database).get_commits_by_file_type()
        # NumberOf(project_owner, project_name, database).get_number_of_reviews_by_developer()
        # NumberOf(project_owner, project_name, database).get_mean_between_merged_prs_by_user()
        # NumberOf(project_owner, project_name, database).get_labels_rank_by_user()
        # NumberOf(project_owner, project_name, database).get_number_of_prs_opened_by_user()
        # NumberOf(project_owner, project_name, database).get_number_of_prs_closed_by_user()
        # NumberOf(project_owner, project_name, database).get_number_of_comments_by_user()
        # NumberOf(project_owner, project_name, database).get_number_of_commits_by_user()
        # NumberOf(project_owner, project_name, database).get_size_of_commits_by_user()
        # NumberOf(project_owner, project_name, database).get_number_of_merged_prs_by_user()
        # NumberOf(project_owner, project_name, database).get_number_of_words_comments_by_user()

    def run(self):
        #self.run_collector()
        #self.pre_processing_data_before_metrics()
        #self.run_metrics()
        SmellsMain().run()

    def export_cases(self):

        cases_newcomers = list()
        cases_gender = list()
        cases_keywords = list()
        cases_newcomers_rq2 = list()
        cases_team_size_rq2 = list()
        cases_gender_rq2 = list()
        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            # Newcomers -> Design change
            metrics = list(
                database['metrics'].find({'newcomers_size': {'$gt': 2}, 'class_design_change_density': True}))

            for metric in metrics:

                cases_newcomers.append({
                    'issue_url': 'https://github.com/' + project_owner + '/' + project_name +
                                 '/pull/' + str(metric['issue_number']),
                    'project': project_name,
                    'newcomers_size': metric['newcomers_size'],
                                           'class_design_change_density': metric['class_design_change_density'],
                                           'class_design_change_diversity': metric['class_design_change_diversity'],
                                           'method_design_change_density': metric['method_design_change_density'],
                                           'method_design_change_diversity': metric['method_design_change_diversity'],
                                           'issue': metric['issue_number']
                                          })

            # Number Males -> Design change
            metrics = list(
                database['metrics'].find({'number_males': {'$gt': 2}, 'class_design_change_density': True}))

            for metric in metrics:
                cases_gender.append({
                    'issue_url': 'https://github.com/' + project_owner + '/' + project_name +
                                 '/pull/' + str(metric['issue_number']),
                    'project': project_name,
                    'number_males': metric['number_males'],
                    'class_design_change_density': metric['class_design_change_density'],
                    'class_design_change_diversity': metric['class_design_change_diversity'],
                    'method_design_change_density': metric['method_design_change_density'],
                    'method_design_change_diversity': metric['method_design_change_diversity'],
                    'issue': metric['issue_number']})

            # Keywords -> Design change
            metrics = list(
                database['metrics'].find({'mean_number_of_words': {'$gt': 1},
                                          'number_of_words': {'$gt': 1},
                                          'density_design_keywords': {'$gt': 2},
                                          'density_refactoring_keywords': {'$gt': 2},
                                          'number_design_keywords': {'$gt': 2},
                                          'number_refactoring_keywords': {'$gt': 2},
                                          'class_design_change_density': True}))

            for metric in metrics:
                cases_keywords.append(
                    {
                        'issue_url': 'https://github.com/' + project_owner + '/' + project_name +
                                     '/pull/' + str(metric['issue_number']),
                        'project': project_name,
                        'keywords':
                            {
                                'mean_number_of_words': metric['mean_number_of_words'],
                                'number_of_words': metric['number_of_words'],
                                'density_design_keywords': metric['density_design_keywords'],
                                'density_refactoring_keywords': metric['density_refactoring_keywords'],
                                'number_refactoring_keywords': metric['number_refactoring_keywords'],
                                'number_design_keywords': metric['number_design_keywords']
                            },
                        'class_design_change_density': metric['class_design_change_density'],
                        'class_design_change_diversity': metric['class_design_change_diversity'],
                        'method_design_change_density': metric['method_design_change_density'],
                        'method_design_change_diversity': metric['method_design_change_diversity'],
                        'issue': metric['issue_number']}
                )

            #RQ2


            # Newcomers -> Degradation
            metrics = list(
                database['metrics'].find({'newcomers_size': {'$gt': 3}, 'class_degradation_density': True}))

            for metric in metrics:
                cases_newcomers_rq2.append({
                    'issue_url': 'https://github.com/' + project_owner + '/' + project_name +
                                 '/pull/' + str(metric['issue_number']),
                    'project': project_name,
                    'newcomers_size': metric['newcomers_size'],
                    'class_design_change_density': metric['class_degradation_density'],
                    'class_design_change_diversity': metric['class_degradation_diversity'],
                    'method_design_change_density': metric['method_degradation_density'],
                    'method_design_change_diversity': metric['method_degradation_diversity'],
                    'issue': metric['issue_number']
                })

            # Team Size -> Degradation
            metrics = list(
                database['metrics'].find({'team_size': {'$gt': 2}, 'class_degradation_density': True}))

            for metric in metrics:
                cases_team_size_rq2.append({
                    'issue_url': 'https://github.com/' + project_owner + '/' + project_name +
                                 '/pull/' + str(metric['issue_number']),
                    'project': project_name,
                    'team_size': metric['team_size'],
                    'class_design_change_density': metric['class_degradation_density'],
                    'class_design_change_diversity': metric['class_degradation_diversity'],
                    'method_design_change_density': metric['method_degradation_density'],
                    'method_design_change_diversity': metric['method_degradation_diversity'],
                    'issue': metric['issue_number']
                })

            # Team Size -> Degradation
            metrics = list(
                database['metrics'].find({'number_males': {'$gt': 3}, 'class_degradation_density': True}))

            for metric in metrics:
                cases_gender_rq2.append({
                    'issue_url': 'https://github.com/' + project_owner + '/' + project_name +
                                 '/pull/' + str(metric['issue_number']),
                    'project': project_name,
                    'number_males': metric['number_males'],
                    'number_females': metric['number_females'],
                    'class_design_change_density': metric['class_degradation_density'],
                    'class_design_change_diversity': metric['class_degradation_diversity'],
                    'method_design_change_density': metric['method_degradation_density'],
                    'method_design_change_diversity': metric['method_degradation_diversity'],
                    'issue': metric['issue_number']
                })

        df = pd.DataFrame(cases_gender_rq2)
        print(df.to_csv(index=False))
                #print(cases)

    def remove_duplicated_comments(self):
        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            comments_database = database['comments']

            comments = list(comments_database.find({}))
            print(len(comments))

            ids = set()
            for comment in comments:

                if comment['id'] in ids:
                    comments_database.delete_one({'_id': comment['_id']})
                    continue
                ids.add(comment['id'])

            comments = list(comments_database.find({}))

            print(len(comments))

    def dump_database(self):
        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            names = database.collection_names()

            for name in names:
                cursor = list(database[name].find({}))

                try:
                    if not os.path.exists('data/dumps/' + project_name + '/'):
                        os.makedirs('data/dumps/' + project_name + '/')
                except OSError:
                    print("Creation of the directory %s failed" % 'data/dumps/' + project_name + '/')

                with open('data/dumps/' + project_name + '/' + name + '.json', 'w') as file:
                    json.dump(json.loads(json_util.dumps(cursor)), file)



main = Main()
# main.calc_blau_index()
main.run()
#main.dump_database()
