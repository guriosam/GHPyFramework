from pymongo.database import Database

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

from utils.common_mongo_queries import CommonQueries
from utils.date import DateUtils


class DeveloperStatus:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database

    def user_profiling(self):
        """
        Collect the amount of users with author_association equals to NONE, FIRST_TIMER and FIRST_TIME_CONTRIBUTOR on the comments
        """
        print("#### User Profiling ####")

        database = self.database['comments']
        database_users = self.database['users']
        database_metrics = self.database['metrics']
        database_pulls = self.database['pull_requests']

        comments = database.find({})

        type_users = {}
        for comment in comments:
            issue_number = comment['issue_number']

            if issue_number not in type_users.keys():
                type_users[issue_number] = {}
                type_users[issue_number]['newbies'] = set()
                type_users[issue_number]['contributors'] = set()
                type_users[issue_number]['core'] = set()

            user_status = self._check_user_status(comment['author_association'])

            user_login = comment['user']['login']

            self.save_user_info(type_users, issue_number, database_users, user_status, user_login)

        opened_by = {}
        for pull in database_pulls.find({}):
            issue_number = pull['number']

            if issue_number not in type_users.keys():
                type_users[issue_number] = {}
                type_users[issue_number]['newbies'] = set()
                type_users[issue_number]['contributors'] = set()
                type_users[issue_number]['core'] = set()

            user_status = self._check_user_status(pull['author_association'])

            user_login = pull['user']['login']

            opened_by[issue_number] = user_status

            self.save_user_info(type_users, issue_number, database_users, user_status, user_login)

            if pull['merged_by']:
                user_login = pull['merged_by']['login']

                author = database_users.find_one({'username': user_login})
                if author:
                    if 'author_association' not in author.keys():
                        continue

                    status = author['author_association']

                    if not status:
                        continue

                    self.save_user_info(type_users, issue_number, database_users, status, user_login)

            if pull['assignees']:
                for assignee in pull['assignees']:
                    user_login = assignee['login']

                    author = database_users.find_one({'username': user_login})
                    if author:
                        if 'author_association' not in author.keys():
                            continue

                        status = author['author_association']

                        if not status:
                            continue

                        self.save_user_info(type_users, issue_number, database_users, status, user_login)

            if pull['requested_reviewers']:
                for reviewer in pull['requested_reviewers']:
                    user_login = reviewer['login']

                    author = database_users.find_one({'username': user_login})
                    if author:
                        if 'author_association' not in author.keys():
                            continue

                        status = author['author_association']

                        if not status:
                            continue

                        self.save_user_info(type_users, issue_number, database_users, status, user_login)

        for issue_number in type_users.keys():

            if database_metrics.find_one({'issue_number': issue_number}):
                database_metrics.update_one({'issue_number': issue_number},
                    {"$set": {
                        "newbies": len(type_users[issue_number]['newbies']),
                        "contributors": len(type_users[issue_number]['contributors']),
                        "core_developers": len(type_users[issue_number]['core'])
                    }})
                continue
            database_users.insert_one({
                        'issue_number': issue_number,
                        "newbies": len(type_users[issue_number]['newbies']),
                        "contributors": len(type_users[issue_number]['contributors']),
                        "core_developers": len(type_users[issue_number]['core']),
                        "opened_by": opened_by[issue_number]
                    })

    @staticmethod
    def _check_user_status(author_association: str):
        if author_association == 'MEMBER' or author_association == 'OWNER':
            return "CORE_DEVELOPER"

        if author_association == 'CONTRIBUTOR' or author_association == 'COLLABORATOR':
            return "CONTRIBUTOR"

        if author_association == 'NONE' or author_association == 'FIRST_TIMER' or author_association == 'FIRST_TIME_CONTRIBUTOR':
            return "NEWCOMER"

    def turnover(self):

        print("#### User Turnover ####")

        database_pulls = self.database['pull_requests']
        database_comments = self.database['comments']
        database_commits = self.database['commits']

        prs_by_user = self._get_user_interactions(database_pulls, 'user_pulls', 'pr_number', '$number')
        comments_by_user = self._get_user_interactions(database_comments, 'user_comments', 'comment_id', '$id')
        commits_by_user = self._get_user_interactions(database_commits, 'user_commits', 'commit', '$sha')

        user_action = {}

        user_action = self._check_interactions_days(prs_by_user, 'user_pulls', user_action)
        user_action = self._check_interactions_days(comments_by_user, 'user_comments', user_action)
        user_action = self._check_interactions_days(commits_by_user, 'user_commits', user_action)

        database_users = self.database['users']

        for user in user_action.keys():

            before = user_action[user]['interacted_before_180_days']
            within = user_action[user]['interacted_within_180_days']
            status = None

            if before and not within:
                status = "Left"
            if within and not before:
                status = "New"

            if database_users.find_one({"username": user}):
                database_users.update_one({"username": user},
                                    {'$set': {"interacted_before_180_days": before,
                                    "interacted_within_180_days": within,
                                     "turnover": status}})
            else:
                database_users.insert_one({"username": user,
                                    "interacted_before_180_days": before,
                                    "interacted_within_180_days": within,
                                           "turnover": status})

        users = database_users.find()

    def experience(self):

        print("#### User Experience ####")

        database_pulls = self.database['pull_requests']
        database_comments = self.database['comments']
        database_commits = self.database['commits']
        database_users = self.database['users']

        prs_by_user = CommonQueries.get_user_interactions(database_pulls, 'user_pulls', 'pr_number', '$number')
        comments_by_user = CommonQueries.get_user_interactions(database_comments, 'user_comments', 'comment_id', '$id')
        commits_by_user = CommonQueries.get_user_interactions(database_commits, 'user_commits', 'commit', '$sha')

        user_days = {}
        user_days = self._get_first_day(prs_by_user, user_days, 'user_pulls', 'pr_days')
        user_days = self._get_first_day(comments_by_user, user_days, 'user_comments', 'comment_days')
        user_days = self._get_first_day(commits_by_user, user_days, 'user_commits', 'commit_days')

        for user in user_days.keys():
            bigger = max(user_days[user]['commit_days'], user_days[user]['pr_days'], user_days[user]['comment_days'])

            if database_users.find_one({"username": user}):
                database_users.update_one({"username": user},
                                    {'$set': {'experience_in_days': bigger}})
            else:
                database_users.insert_one({"username": user,
                                    'experience_in_days': bigger})

    @staticmethod
    def _get_first_day(array, user_days, group_key, elem_key):
        for elem in array:
            username = elem['_id']

            if not username:
                continue

            first = elem[group_key][-1]

            if username not in user_days.keys():
                user_days[username] = {
                    'pr_days': 0,
                    'comment_days': 0,
                    'commit_days': 0
                }

            user_days[username][elem_key] = DateUtils.days_between_date_and_now(first['created_at'])

        return user_days

    @staticmethod
    def _check_interactions_days(elements, key, last_user_action):
        for element in elements:
            if element['_id'] not in last_user_action.keys():
                last_user_action[element['_id']] = {
                    "interacted_before_180_days": False,
                    "interacted_within_180_days": False
                }

            if element['_id'] in last_user_action.keys():
                if last_user_action[element['_id']]['interacted_before_180_days'] and \
                        last_user_action[element['_id']]['interacted_within_180_days']:
                    continue

            for user_elem_list in element[key]:
                if DateUtils.days_between_date_and_now(user_elem_list['created_at']) >= 180:
                    last_user_action[element['_id']]['interacted_before_180_days'] = True
                    break

                if DateUtils.days_between_date_and_now(user_elem_list['created_at']) < 180:
                    last_user_action[element['_id']]['interacted_within_180_days'] = True

        return last_user_action

    def save_user_info(self, type_users, issue_number, database_users, user_status, user_login):

        if database_users.find_one({"username": user_login}):
            database_users.update_one({"username": user_login}, {'$set': {"author_association": user_status}})
        else:
            database_users.insert_one({"username": user_login, "author_association": user_status})
            database_users.insert_one({"username": user_login, "author_association": user_status})

        if user_status == 'NEWCOMER':
            type_users[issue_number]['newbies'].add(user_login)
        elif user_status == 'CONTRIBUTOR':
            type_users[issue_number]['contributors'].add(user_login)
        elif user_status == 'CORE_DEVELOPER':
            type_users[issue_number]['core'].add(user_login)


