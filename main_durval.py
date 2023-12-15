import re

import pandas as pd
from pymongo import MongoClient

from utils.json_handler import JSONHandler


class MainDurval:

    def __init__(self):
        json_handler = JSONHandler('./')
        self.config = json_handler.open_json('config_dev.json')
        self.projects = self.config['projects']
        self.mongo_connection = MongoClient("mongodb://localhost:27017/")

    def run(self):

        df = pd.DataFrame(columns=['project', 'commit', 'file_path', 'patch'])

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']
            print(project_name)

            database = self.mongo_connection[project_owner + '-' + project_name]

            commits_database = database['commits']
            pulls_database = database['pull_requests']
            issues_database = database['issues']

            issue_numbers = self._get_issues_prs_fixed(commits_database)

            commits = set()

            #df_project = pd.DataFrame(columns=['project', 'commit'])
            df_project = pd.DataFrame(columns=['project', 'commit', 'file_path', 'patch'])

            for fixed_issues in issue_numbers:

                try:
                    pulls = pulls_database.find({'number': int(fixed_issues['issue_number'])})
                    issues2 = issues_database.find({'number': int(fixed_issues['issue_number'])})
                except:
                    continue

                for pull in pulls:
                    if pull['labels']:
                        for label in pull['labels']:
                            if 'bug' in label['name']:
                                commits.add(fixed_issues['commit_sha'])
                            if 'defect' in label['name']:
                                commits.add(fixed_issues['commit_sha'])

                for issue in issues2:
                    if issue['labels']:
                        for label in issue['labels']:
                            if 'bug' in label['name']:
                                commits.add(fixed_issues['commit_sha'])
                            if 'defect' in label['name']:
                                commits.add(fixed_issues['commit_sha'])

            commits = list(commits)

            for commit in commits:
                c = commits_database.find_one({'sha': commit})
                if not c:
                    continue
                if 'files' not in c.keys():
                    continue

                for file in c['files']:
                    filename = file['filename']
                    if 'patch' not in file.keys():
                        continue
                    patch = file['patch']

                    df_project.loc[-1] = [project_name, commit, filename, patch]  # adding a row
                    df_project.index = df_project.index + 1  # shifting index
                    df_project = df_project.sort_index()

                    df.loc[-1] = [project_name, commit, filename, patch] # adding a row
                    df.index = df.index + 1  # shifting index
                    df = df.sort_index()

            #df_project.to_csv('data/buggy/' + project_name + '.csv', index=False)

        #df.to_csv('data/buggy/all.csv', index=False)
        df.to_csv('data/buggy/projects_patches.csv', index=False)



    @staticmethod
    def _get_issues_prs_fixed(commits_database):

        commits = commits_database.find({})

        issues = list()
        for commit in commits:
            fixes = re.findall("fixes \#[0-9]*", commit['commit']['message'])
            fixed = re.findall("fixed \#[0-9]*", commit['commit']['message'])
            fixs = re.findall("fix \#[0-9]*", commit['commit']['message'])
            closes = re.findall("closes \#[0-9]*", commit['commit']['message'])
            closed = re.findall("closed \#[0-9]*", commit['commit']['message'])
            close = re.findall("close \#[0-9]*", commit['commit']['message'])

            issue = {'commit_sha': commit['sha'], 'commit_parent_sha': None}

            if commit['parents']:
                issue['commit_parent_sha'] = commit['parents'][0]['sha']

            if fixes:
                for fix in fixes:
                    issue['issue_number'] = fix.split('#')[1]
                    issues.append(issue)

            if fixed:
                for fix in fixed:
                    issue['issue_number'] = fix.split('#')[1]
                    issues.append(issue)

            if fixs:
                for fix in fixs:
                    issue['issue_number'] = fix.split('#')[1]
                    issues.append(issue)

            if closes:
                for close1 in closes:
                    issue['issue_number'] = close1.split('#')[1]
                    issues.append(issue)

            if closed:
                for close1 in closed:
                    issue['issue_number'] = close1.split('#')[1]
                    issues.append(issue)

            if close:
                for cl in close:
                    issue['issue_number'] = cl.split('#')[1]
                    issues.append(issue)

        return issues

MainDurval().run()