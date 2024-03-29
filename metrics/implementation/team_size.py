from pymongo.database import Database
from utils.api_call_handler import APICallHandler
from utils.common_mongo_queries import CommonQueries
from utils.date import DateUtils


class TeamSize:

    def __init__(self, database: Database = None):
        self.database = database

    def get_team(self):
        collection_pull_request = self.database['pull_requests']
        collection_comments = self.database['comments']
        collection_commits = self.database['commits']

        prs_by_user = CommonQueries.get_user_interactions(collection_pull_request, 'user_pulls', 'pr_number', '$number')
        comments_by_user = CommonQueries.get_user_interactions(collection_comments, 'user_comments', 'comment_id',
                                                               '$id')
        commits_by_user = CommonQueries.get_user_interactions(collection_commits, 'user_commits', 'commit', '$sha')

        pr_numbers = collection_pull_request.find({})
        users_by_pr = {}

        for pr in pr_numbers:

            if not pr['merged']:
                continue

            users = {'new': set(), 'left': set(), 'contributor': set()}

            users = CommonQueries.collect_participating_users(self.database, pr, users)

            pr_merged_at = pr['merged_at']

            for user in users['contributor']:
                user_commits, user_prs, user_comments = self._get_user_past_interactions_list(user, commits_by_user,
                                                                                              prs_by_user,
                                                                                              comments_by_user)

                users = self._days_since(user, users, user_commits, pr_merged_at)
                users = self._days_since(user, users, user_prs, pr_merged_at)
                users = self._days_since(user, users, user_comments, pr_merged_at)

                # classify users as Contributors if they meet both requirements
                team = users['new'].union(users['left'])
                new = users['new'] - users['left']
                left = users['left'] - users['new']

                if not self.database['metrics'].find_one({'issue_number': pr['number']}):
                    self.database['metrics'].insert_one({'issue_number': pr['number']})

                self.database['metrics'].update_one({"issue_number": pr['number']},
                                                    {'$set': {'team_size': len(team), 'newcomers_size': len(new),
                                                              'users_left_size': len(left)}})

        return users_by_pr

    def _get_user_past_interactions_list(self, user, commits_by_user, prs_by_user, comments_by_user):
        user_commits = self._get_user_dates_list(user, commits_by_user, 'user_commits')

        user_prs = self._get_user_dates_list(user, prs_by_user, 'user_pulls')

        user_comments = self._get_user_dates_list(user, comments_by_user, 'user_comments')

        return user_commits, user_prs, user_comments

    @staticmethod
    def _get_user_dates_list(user, by_user, key):
        items = []
        for item in by_user:
            if not item['_id']:
                continue

            if user in item['_id']:
                items = item[key]
                break

        return items

    @staticmethod
    def _days_since(user, users, user_items, pr_merged_at):
        count = 0

        for user_item in user_items:
            days_since = DateUtils().get_days_between_dates(user_item['created_at'], pr_merged_at)

            if days_since < 0:
                continue

            # Check if user has commented before and after 180 days
            if days_since < 180:
                users['new'].add(user)
                count += 1
            else:
                users['left'].add(user)
                count += 1

            if count > 2:
                break

        return users
