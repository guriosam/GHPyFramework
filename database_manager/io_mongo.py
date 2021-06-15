from os import listdir
from os.path import isfile, join

from pymongo.database import Database

from utils.json_handler import JSONHandler


class IOMongo:

    ### TODO set master and merged commits

    def __init__(self, database: Database, project: str):
        self.database = database
        self.project = project
        config = JSONHandler('./').open_json('config.json')
        self.path = config['output_path'] + self.project + '/'

    def insert_issues(self):
        database = self.database['issues']

        issues_path = self.path + 'issues/individual/'

        json = JSONHandler(issues_path)
        issues = [f for f in listdir(issues_path) if isfile(join(issues_path, f))]

        for file in issues:

            issue = json.open_json(file)

            if database.find_one({'number': issue['number']}):
                continue

            database.insert_one(issue)

    def insert_pulls(self):
        database = self.database['pull_requests']

        pulls_path = self.path + 'pulls/individual/'

        json = JSONHandler(pulls_path)
        pulls = [f for f in listdir(pulls_path) if isfile(join(pulls_path, f))]

        for file in pulls:

            pull = json.open_json(file)

            if database.find_one({'number': pull['number']}):
                continue

            database.insert_one(pull)

    def insert_commits(self):
        database = self.database['commits']

        commits_path = self.path + 'commits/individual/'

        json = JSONHandler(commits_path)
        commits = [f for f in listdir(commits_path) if isfile(join(commits_path, f))]

        for file in commits:

            commit = json.open_json(file)

            if database.find_one({'sha': commit['sha']}):
                continue

            commit['from_pull'] = False
            commit['pull_origin'] = []

            database.insert_one(commit)

    def insert_commits_from_pulls(self):
        database = self.database['commits']

        pulls_commits_path = self.path + 'pulls_commits/commits/'

        json = JSONHandler(pulls_commits_path)
        commits = [f for f in listdir(pulls_commits_path) if isfile(join(pulls_commits_path, f))]

        commit_pulls = {}
        for file in commits:
            commit_batch = json.open_json(file)
            for commit_list in commit_batch:
                for commit in commit_list:
                    if commit['sha'] not in commit_pulls.keys():
                        commit_pulls[commit['sha']] = []

                    commit_pulls[commit['sha']].append(file.split('.')[0])

        pulls_commits_path = self.path + 'pulls_commits/individual/'

        json = JSONHandler(pulls_commits_path)
        commits = [f for f in listdir(pulls_commits_path) if isfile(join(pulls_commits_path, f))]

        for file in commits:

            commit = json.open_json(file)

            if database.find_one({'sha': commit['sha']}):
                database.update_one({'sha': commit['sha']}, {"$set": {'from_pull': True}})

                if commit['sha'] in commit_pulls.keys():
                    database.update_one({'sha': commit['sha']}, {"$set": {'pull_origin': commit_pulls[commit['sha']]}})

                continue

            commit['from_pull'] = True
            commit['pull_origin'] = []

            if commit['sha'] in commit_pulls.keys():
                commit['pull_origin'] = commit_pulls[commit['sha']]

            database.insert_one(commit)

    def insert_comments(self):
        database = self.database['comments']

        comments_path = self.path + 'comments/individual/'

        json = JSONHandler(comments_path)
        comments = [f for f in listdir(comments_path) if isfile(join(comments_path, f))]

        for file in comments:

            comment_batch = json.open_json(file)

            for comment in comment_batch:

                if database.find_one({'id': comment['id']}):
                    continue

                issue_number = comment['issue_url'].split('issues/')[1]

                comment['issue_number'] = int(issue_number)

                database.insert_one(comment)

        comments_path = self.path + 'comments/issues/all/'

        json = JSONHandler(comments_path)
        comments = [f for f in listdir(comments_path) if isfile(join(comments_path, f))]

        for file in comments:

            comment_batch = json.open_json(file)

            for comment in comment_batch:

                if database.find_one({'id': comment['id']}):
                    continue

                issue_number = comment['issue_url'].split('issues/')[1]

                comment['issue_number'] = int(issue_number)

                database.insert_one(comment)


    def insert_users(self):
        database = self.database['users']
        pass

    def insert_events(self):
        database = self.database['events']

        events_path = self.path + 'events/all/'

        json = JSONHandler(events_path)
        events = [f for f in listdir(events_path) if isfile(join(events_path, f))]

        for file in events:

            event_batch = json.open_json(file)
            for event in event_batch:

                if database.find_one({'id': event['id']}):
                    continue

                database.insert_one(event)

        pass
