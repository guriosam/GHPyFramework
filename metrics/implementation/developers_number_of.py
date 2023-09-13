import re
from os import listdir
from os.path import isfile, join
from statistics import median

from bson import ObjectId
from pymongo.database import Database

from utils.csv_handler import CSVHandler
from utils.date import DateUtils
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

from utils.text_cleaning import TextCleaner


class NumberOf:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database

    # Number of Merged PR
    # Number of words (Mean by comment)

    def get_number_of_comments_by_user(self):
        """
        Collects the number of the number of comments inside an issue or pull requests
        """
        print("#### Number of Comments ####")

        number_of_comments = self._get_number_of(self.database['comments'], '$user.login', 'number_of_comments')
        database_users = self.database['users']

        for comments in number_of_comments:
            username = comments['_id']

            if not username:
                continue

            if database_users.find_one({"username": username}):
                database_users.update_one({"username": username},
                                          {'$set': {'number_of_comments': comments['number_of_comments']}})
            else:
                database_users.insert_one({"username": username,
                                           'number_of_comments': comments['number_of_comments']})

    def get_number_of_words_comments_by_user(self):
        """
        Collects the number of the number of words in comments inside an issue or pull requests
        """
        print("#### Number of Words in Comments ####")

        self._set_number_of_words_in_comments(self.database['comments'])

        comments_by_user = self._get_user_comments(self.database['comments'])

        database_metrics = self.database['metrics']

        document = {}
        for user in comments_by_user:
            username = user['_id']
            document[username] = {}

            for comment in user['comments']:
                issue_number = comment['issue_number']
                if issue_number not in document[username].keys():
                    document[username][issue_number] = []

                document[username][issue_number].append(comment)

        database_users = self.database['users']

        for username in document.keys():

            issues = document[username]

            if not username:
                continue

            total_all_words, total_mean_words, total_mean_comments = self._get_user_total_words_and_mean_comments(
                issues)

            mean_duration = self._get_user_discussion_duration(database_metrics, issues)

            if database_users.find_one({"username": username}):
                database_users.update_one({"username": username},
                                          {'$set': {
                                              'total_words': total_all_words,
                                              'mean_words': total_mean_words,
                                              'mean_time_between_comments': total_mean_comments,
                                              'mean_discussion_duration': mean_duration}})
            else:
                database_users.insert_one({"username": username,
                                           'total_words': total_all_words,
                                           'mean_words': total_mean_words,
                                           'mean_time_between_comments': total_mean_comments,
                                           'mean_discussion_duration': mean_duration})

    def get_number_of_reviews_by_developer(self):
        database_reviews = self.database['reviews']
        database_users = self.database['users']

        users = database_users.find({})

        for user in users:

            if 'username' not in user.keys():
                continue

            username = user['username']

            reviews = database_reviews.find({'user.login': username})

            lines = 0
            files = set()
            modules = set()
            reviews_number = set()

            for review in reviews:

                reviews_number.add(review['pull_request_review_id'])

                if '.java' in review['path'] or '.xml' in review['path']:
                    files.add(review['path'])

                if '.java' in review['path'] or '.xml' in review['path']:
                    modules.add(review['path'].rsplit('/', 1)[0])

                lines += len(review['diff_hunk'].splitlines()) - 1

            number_reviews = len(reviews_number)
            number_modules = len(modules)
            number_files = len(files)

            database_users.update_one({'username': username}, {'$set': {'number_reviews': number_reviews,
                                                                        'number_modules_revised': number_modules,
                                                                        'number_files_revised': number_files,
                                                                        'lines_revised': lines}})

    def get_commits_by_file_type(self):
        database_commits = self.database['commits']
        database_users = self.database['users']

        java, xml = self._get_commits_by_file_type(database_commits)

        users_java_file_type = {}
        for commit in java:
            if not commit['author']:
                continue
            user = commit['author']['login']

            if user not in users_java_file_type.keys():
                users_java_file_type[user] = 0

            users_java_file_type[user] += 1

        users_xml_file_type = {}
        for commit in xml:
            if not commit['author']:
                continue
            user = commit['author']['login']

            if user not in users_xml_file_type.keys():
                users_xml_file_type[user] = 0

            users_xml_file_type[user] += 1

        for user in users_xml_file_type.keys():
            database_users.update_one({'username': user}, {'$set': {'xml_commits': users_xml_file_type[user]}})

        for user in users_java_file_type.keys():
            database_users.update_one({'username': user}, {'$set': {'java_commits': users_java_file_type[user]}})

    def get_number_of_commits_by_user(self):
        print("#### Number of Commits ####")

        number_of_commits = self._get_number_of(self.database['commits'], '$author.login', 'number_of_commits')

        database_users = self.database['users']

        for commits in number_of_commits:
            username = commits['_id']

            if not username:
                continue

            if database_users.find_one({"username": username}):
                database_users.update_one({"username": username},
                                          {'$set': {'number_of_commits': commits['number_of_commits']}})
            else:
                database_users.insert_one({"username": username,
                                           'number_of_commits': commits['number_of_commits']})

    def get_size_of_commits_by_user(self):
        print("#### Size of Commits ####")

        size_of_commits = self._get_avg_of(self.database['commits'], '$author.login', 'avg_size_of_commits',
                                           '$stats.total')

        database_users = self.database['users']

        for size in size_of_commits:
            username = size['_id']

            if not username:
                continue

            if database_users.find_one({"username": username}):
                database_users.update_one({"username": username},
                                          {'$set': {'avg_size_of_commits': size['avg_size_of_commits']}})
            else:
                database_users.insert_one({"username": username,
                                           'avg_size_of_commits': size['avg_size_of_commits']})

    def get_number_of_merged_prs_by_user(self):
        print("#### Number of Merged PRs ####")

        merged_prs_by_user = self._get_user_merged_prs(self.database['pull_requests'])
        database_users = self.database['users']

        for merged_prs in merged_prs_by_user:
            username = merged_prs['_id']

            if not username:
                continue

            if database_users.find_one({"username": username}):
                database_users.update_one({"username": username},
                                          {'$set': {'number_of_merged_prs': len(merged_prs['merged_prs'])}})
            else:
                database_users.insert_one({"username": username,
                                           'number_of_merged_prs': len(merged_prs['merged_prs'])})

    def get_number_of_prs_opened_by_user(self):
        print("#### Number of PRs Opened ####")

        number_of_prs_opened = self._get_number_of(self.database['pull_requests'], '$user.login',
                                                   'pulls_opened')

        database_users = self.database['users']

        for opened_prs in number_of_prs_opened:
            username = opened_prs['_id']

            if not username:
                continue

            if database_users.find_one({"username": username}):
                database_users.update_one({"username": username},
                                          {'$set': {'pulls_opened': opened_prs['pulls_opened']}})
            else:
                database_users.insert_one({"username": username,
                                           'pulls_opened': opened_prs['pulls_opened']})

    def get_number_of_prs_closed_by_user(self):
        print("#### Number of PRs Closed ####")

        number_of_prs_closed = self._get_number_of(self.database['pull_requests'], '$merged_by.login',
                                                   'pulls_closed')

        database_users = self.database['users']

        for closed_prs in number_of_prs_closed:
            username = closed_prs['_id']

            if not username:
                continue

            if database_users.find_one({"username": username}):
                database_users.update_one({"username": username},
                                          {'$set': {'pulls_closed': closed_prs['pulls_closed']}})
            else:
                database_users.insert_one({"username": username,
                                           'pulls_closed': closed_prs['pulls_closed']})

    def get_mean_between_merged_prs_by_user(self):
        print("#### Mean Time Between Merged PRs ####")

        merged_prs_by_user = self._get_user_merged_prs(self.database['pull_requests'])
        database_users = self.database['users']

        for merged_prs in merged_prs_by_user:
            username = merged_prs['_id']

            if not username:
                continue

            prs = merged_prs['merged_prs']

            total = 0

            for i in range(0, len(prs) - 1):
                if prs[i + 1]['merged_at'] and prs[i]['merged_at']:
                    delta = DateUtils().get_days_between_dates(prs[i + 1]['merged_at'], prs[i]['merged_at'])
                else:
                    delta = DateUtils().get_days_between_dates(prs[i + 1]['updated_at'], prs[i]['updated_at'])

                if delta < 0:
                    delta = delta * -1

                total += delta

            mean = 0
            if len(prs) > 0:
                mean = total / len(prs)

            if database_users.find_one({"username": username}):
                database_users.update_one({"username": username},
                                          {'$set': {'mean_time_between_merged_prs': mean}})
            else:
                database_users.insert_one({"username": username,
                                           'mean_time_between_merged_prs': mean})

    def get_labels_rank_by_user(self):
        print("#### Label Ranking ####")

        labels_by_user = self._get_user_labels(self.database['pull_requests'], 'user_labels', 'labels', '$labels.name')

        database_users = self.database['users']

        rank = {}
        for labels in labels_by_user:
            username = labels['_id']
            if username not in rank.keys():
                rank[username] = {}

            user_rank = rank[username]

            labels = labels['user_labels']
            for label_obj in labels:
                label_list = label_obj['labels']
                for label in label_list:
                    if label not in user_rank.keys():
                        user_rank[label] = 0

                    user_rank[label] += 1

            if database_users.find_one({"username": username}):
                database_users.update_one({"username": username},
                                          {'$set': {'label_rank': user_rank}})
            else:
                database_users.insert_one({"username": username,
                                           'label_rank': user_rank})

    @staticmethod
    def _get_avg_of(database, element, label, avg_value):
        return database.aggregate([
            {
                '$group': {
                    '_id': element,
                    label: {
                        '$avg': avg_value
                    }
                }
            }
        ])

    @staticmethod
    def _get_number_of(database, element, label):
        return database.aggregate([
            {
                '$group': {
                    '_id': element,
                    label: {
                        '$count': {}
                    }
                }
            }
        ])

    @staticmethod
    def _get_user_comments(database):
        return database.aggregate([
            {
                '$group': {
                    '_id': '$user.login',
                    'comments': {
                        '$addToSet': {
                            'total_words': '$total_words',
                            'issue_number': '$issue_number',
                            'created_at': '$created_at'
                        }
                    }
                }
            }, {
                '$sort': {
                    'created_at': -1
                }
            }
        ])

    @staticmethod
    def _get_user_labels(database, group_key, push_key, push_value):
        return database.aggregate([
            {
                '$group': {
                    '_id': '$user.login',
                    group_key: {
                        '$push': {
                            push_key: push_value
                        }
                    }
                }
            }
        ])

    @staticmethod
    def _get_commits_by_file_type(database):
        commits_with_files = database.find({'files': {'$exists': True, '$not': {'$size': 0}}})

        commits_with_java = []
        commits_with_xml = []
        for commit in commits_with_files:
            java = False
            xml = False
            for commit_file in commit['files']:
                if '.java' in commit_file['filename'] and not java:
                    java = True
                    commits_with_java.append(commit)

                if '.xml' in commit_file['filename'] and not xml:
                    xml = True
                    commits_with_xml.append(commit)

        return commits_with_java, commits_with_xml

    @staticmethod
    def _get_user_merged_prs(database):
        return database.aggregate([
            {
                '$match': {
                    'merged': True
                }
            }, {
                '$group': {
                    '_id': '$merged_by.login',
                    'merged_prs': {
                        '$addToSet': {
                            'prs': '$number',
                            'merged_at': '$merged_at',
                            'updated_at': '$updated_at'
                        }
                    }
                }
            }, {
                '$sort': {
                    'updated_at': -1,
                    'merged_at': -1
                }
            }
        ])

    @staticmethod
    def _set_user_merged_prs_from_commits(database_users, database_pulls):
        regex = '#[0-9]+'
        for commit in database_users.find({'commit.message': {'$regex': regex}}):
            message = commit['commit']['message']

            pulls = re.findall(regex, message)
            for pull in pulls:
                pull = pull.replace('#', '')
                if not pull:
                    continue
                pull = int(pull)
                if database_pulls.find_one({'number': pull}):
                    database_pulls.update_one({'number': pull}, {'$set': {'merged_by': commit['author'],
                                                                          'merge_commit_sha': commit['sha'],
                                                                          'merged_at': commit['commit']['author'][
                                                                              'date'],
                                                                          'merged': True}})

    @staticmethod
    def _get_avg_user_merged_prs(database):
        return database.aggregate([
            {
                '$match': {
                    'merged': True
                }
            }, {
                '$group': {
                    '_id': '$merged_by.login',
                    'merged_prs': {
                        '$push': {
                            'prs': '$number',
                            'merged_at': '$merged_at',
                            'updated_at': '$updated_at'
                        }
                    }
                }
            }
        ])

    ## TODO
    @staticmethod
    def _get_avg_user_merged_prs_in_events(database):
        return database.aggregate([
            {
                '$match': {
                    'merged': True
                }
            }, {
                '$group': {
                    '_id': '$merged_by.login',
                    'merged_prs': {
                        '$push': {
                            'prs': '$number',
                            'merged_at': '$merged_at',
                            'updated_at': '$updated_at'
                        }
                    }
                }
            }
        ])

    def fix_merged_prs(self):
        database_commits = self.database['commits']

        self._set_user_merged_prs_from_commits(database_commits, self.database['pull_requests'])

    @staticmethod
    def _set_number_of_words_in_comments(database):
        comments = database.find({'total_words': {'$exists': False}})

        cleaning = TextCleaner()

        for comment in comments:
            body = comment['body']
            body = cleaning.clean(body)
            total_words = len(body.split())
            _id = comment['_id']
            database.update_one({'_id': _id},
                                {
                                    '$set': {
                                        'total_words': total_words
                                    }
                                })

    @staticmethod
    def _get_user_discussion_duration(database_metrics, issues):
        count = 0
        mean_duration = 0
        for issue_number in issues.keys():

            pr = database_metrics.find_one({'issue_number': issue_number})

            if not pr:
                continue

            if not 'discussion_duration' in pr.keys():
                continue

            duration = pr['discussion_duration']
            mean_duration += duration
            count += 1

        if count == 0:
            count = 1

        mean_duration = mean_duration / count

        return mean_duration

    @staticmethod
    def _get_user_total_words_and_mean_comments(issues):
        total_all_words = 0
        total_mean_words = 0
        total_mean_comments = 0

        for issue_number in issues.keys():
            comments = issues[issue_number]

            total = 0

            for i in range(0, len(comments) - 1):
                delta = DateUtils().get_days_between_dates(comments[i]['created_at'], comments[i + 1]['created_at'])
                if delta < 0:
                    delta = delta * -1
                total += delta

            mean_comments = 0

            if len(comments) > 0:
                mean_comments = total / len(comments)

            total_mean_comments += mean_comments
            total_words = 0

            for comment in comments:
                total_words += comment['total_words']

            total_all_words += total_words

            mean_words = 0
            if len(comments) > 0:
                mean_words = total_words / len(comments)

            total_mean_words += mean_words

        return total_mean_comments, total_all_words, total_mean_words
