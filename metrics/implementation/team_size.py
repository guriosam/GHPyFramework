from pymongo.database import Database
from utils.api_call_handler import APICallHandler
from utils.date import DateUtils


class TeamSize:

    def __init__(self, database: Database = None):
        self.database = database

        self.api_url = 'https://api.github.com/'
        self.apiCall = APICallHandler()

    def get_team(self):

        collection_pull_request = self.database['pull_requests']
        collection_comments = self.database['comments']
        collection_commits = self.database['commits']

        prs_by_user = self._get_user_interactions(collection_pull_request, 'user_pulls', 'pr_number', '$number')
        comments_by_user = self._get_user_interactions(collection_comments, 'user_comments', 'comment_id', '$id')
        commits_by_user = self._get_user_interactions(collection_commits, 'user_commits', 'commit', '$sha')

        pr_numbers = collection_pull_request.find({})
        commits = collection_commits.find({})
        users_by_pr = {}

        for pr in pr_numbers:

            pr_number = pr['number']
            if not pr['merged']:
                continue
            comments = collection_comments.find({'issue_number': pr_number})
            users = {'new': set(), 'left': set(), 'contributor': set()}

            # add creator and who merged the pr
            if pr['user'] and pr['user']['type'] != 'Bot':
                users['contributor'].add(pr['user']['login'])
            if pr['merged_by'] and pr['merged_by']['type'] != 'Bot':
                users['contributor'].add(pr['merged_by']['login'])

            for comment in comments:
                if comment['user']['type'] != 'Bot':
                    user_login = comment['user']['login']
                    users['contributor'].add(user_login)

            pr_merged_at = pr['merged_at']

            for user in users['contributor']:
                user_commits = []
                for commit in commits_by_user:
                    if not commit['_id']:
                        continue
                    if user in commit['_id']:
                        user_commits = commit['user_commits']
                        break

                user_prs = []
                for prs in prs_by_user:
                    if not prs['_id']:
                        continue
                    if user in prs['_id']:
                        user_prs = prs['user_pulls']
                        break

                user_comments = []
                for comment in prs_by_user:
                    if not comment['_id']:
                        continue
                    if user in comment['_id']:
                        user_comments = comment['user_comments']
                        break

                for user_commit in user_commits:
                    days_since_commit = DateUtils().get_days_between_dates(user_commit['created_at'], pr_merged_at)
                    print("Days since commits: ", days_since_commit)
                    if days_since_commit < 0:
                        continue
                    # Check if user has commented before and after 180 days
                    if days_since_commit < 180:
                        users['new'].add(user)
                    else:
                        users['left'].add(user)

                for user_pr in user_prs:
                    days_since_pr = DateUtils().get_days_between_dates(user_pr['created_at'], pr_merged_at)
                    print("Days since pr: ", days_since_pr)
                    if days_since_pr < 0:
                        continue
                    # Check if user has commented before and after 180 days
                    if days_since_pr < 180:
                        users['new'].add(user)
                    else:
                        users['left'].add(user)

                for user_comment in user_comments:
                    days_since_comment = DateUtils().get_days_between_dates(user_comment['created_at'], pr_merged_at)
                    print("Days since comments: ", days_since_comment)
                    if days_since_comment < 0:
                        continue
                    # Check if user has commented before and after 180 days
                    if days_since_comment < 180:
                        users['new'].add(user)
                    else:
                        users['left'].add(user)


                # classify users as Contributors if they meet both requirements
                team = users['new'].intersection(users['left'])
                new = users['new'] - team
                left = users['left'] - team

                print(users['new'])
                print(users['left'])

                #print(team)
                #print(new)
                #print(left)





        return users_by_pr

    @staticmethod
    def _get_user_interactions(database, group_key, push_key, push_value):

        push = {push_key: push_value, 'created_at': '$created_at'}
        push_commit = {push_key: push_value, 'created_at': '$commit.author.date'}

        if 'commit' in group_key:
            push = push_commit

        return database.aggregate([
            {
                '$group': {
                    '_id': '$user.login',
                    group_key: {
                        '$push': push
                    }
                }
            }, {
                '$sort': {
                    'created_at': -1
                }
            }
        ])

