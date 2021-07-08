
import json

from api.api_collector import APICollector
from database_manager.io_mongo import IOMongo
from metrics.metrics_collector import MetricsCollector
from metrics.number_of_modified_files import NumberModifiedFiles
from utils.csv_handler import CSVHandler
from utils.json_handler import JSONHandler
import pymongo


class Main:

    def __init__(self):

        json_handler = JSONHandler('C:/Users/gurio/PycharmProjects/GHPyFramework/')

        self.config = json_handler.open_json('config.json')
        self.projects = self.config['projects']

    def collect_data_daniel(self):


        self.commits_limit = {
            "dubbo": "b288ad7e3812d2354e54aa2f20f8127f24586a5e",
            "fresco": "d35e8f32441bc84bce1bb3a056d221ffa9537ca2",
            "RxJava": "fd496db9a64320fcb9f9b4d110018bcd41e46c82",
            "netty": "6f602cbd147a3f42b20a8fa2433a7c1da9da190d",
            "presto": "951c5653da4d3b7fb9c925f123d264a93daaba9d",
            "okhttp": "6a8f479134a3976ad1a30169e6ab0d3a1b4c65c6"
        }

        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        output = [['project', 'email', 'name', 'commits_as_author', 'commits_as_committer']]

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = myclient[project_owner + '-' + project_name]

            issues_prs = self._get_commit_issues_prs(database, project_name)

            comments_per_issue = {}

            for issues_pr in issues_prs:

                events_database = database['comments']

                comments = events_database.find({'issue_number': issues_pr})

                if issues_pr not in comments_per_issue.keys():
                    comments_per_issue[issues_pr] = []

                for comment in comments:
                    comments_per_issue[issues_pr].append(comment['body'])

            with open(project_name + '_comments.json', 'w', encoding='utf8') as outfile:
                json.dump(comments_per_issue, outfile, indent=4)
                print(project_name + ' saved.')

    def _get_commit_issues_prs(self, database, project_name):

        commits_database = database['commits']
        events_database = database['events']

        last_commit = commits_database.find_one({'sha': self.commits_limit[project_name]})
        final_date = last_commit['commit']['author']['date']
        commits = commits_database.find({'commit.author.date': {'$lt': final_date}, 'from_pull': True})
        output = {}

        issues_prs = set()

        for commit in commits:
            if commit['sha'] not in output.keys():
                output[commit['sha']] = {}

            pulls = commit['pull_origin']

            if 'pulls' not in output[commit['sha']].keys():
                output[commit['sha']]['pulls'] = []

            for pull in pulls:
                output[commit['sha']]['pulls'].append(pull)
                issues_prs.add(pull)

            events_issues = events_database.find({'commit_id': commit['sha']})

            if 'issues' not in output[commit['sha']].keys():
                output[commit['sha']]['issues'] = []

            for event_issue in events_issues:

                issue = event_issue['issue']

                if issue:
                    if 'issues' in issue['html_url']:
                        output[commit['sha']]['issues'].append(issue['number'])
                        issues_prs.add(issue['number'])

        with open(project_name + '_commits_issues_prs.json', 'w', encoding='utf8') as outfile:
            json.dump(output, outfile, indent=4)
            print(project_name + ' saved.')

        return issues_prs

    def get_authors_info(self):

        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        output = [['project', 'email', 'name', 'commits_as_author', 'commits_as_committer']]

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = myclient[project_owner + '-' + project_name]

            result = database['commits'].aggregate([
                {
                    '$match': {
                        'commit.committer.date': {
                            '$gte': '2019-06-01T00:00:01Z'
                        }
                    }
                }, {
                    '$group': {
                        '_id': 1,
                        'list': {
                            '$addToSet': '$commit.author.email'
                        }
                    }
                }
            ])

            for resul in result:
                print(project_name)
                for el in resul['list']:
                    if 'bot' in el:
                        continue
                    if 'reply' in el:
                        continue
                    if '@' in el:
                        commit = database['commits'].find_one({'commit.author.email': el})
                        commits_as_author = database['commits'].find({'commit.author.email': el}).count()
                        commits_as_committer = database['commits'].find({'commit.committer.email': el}).count()
                        if commit:
                            output.append([project_name, el, commit['commit']['author']['name'], commits_as_author,
                                           commits_as_committer])

            csv = CSVHandler()
            csv.write_csv('./', 'all_emails2.csv', output)


Main().get_authors_info()