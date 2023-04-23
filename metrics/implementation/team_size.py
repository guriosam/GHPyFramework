from pymongo.database import Database
from utils.api_call_handler import APICallHandler
from utils.date import DateUtils

class teamSize:

    def __init__(self, database: Database = None):
        self.database = database

        self.api_url = 'https://api.github.com/'
        self.apiCall = APICallHandler()

    def get_team(self):

        collection_pull_request = self.database['pull_requests']
        collection_comments = self.database['comments']
        collection_commits = self.database['commits']

        pr_numbers = collection_pull_request.find({})
        commits = collection_commits.find({})
        users_by_pr = {}

        for pr in pr_numbers:

            pr_number = pr['number']
            if pr['merged']:
                comments = collection_comments.find({'issue_number': pr_number})
                users = {'New': set(), 'Left': set(), 'Contributor': set()}

                # add creator and who merged the pr
                if pr['user'] and pr['user']['type'] != 'Bot':
                    users['Contributor'].add(pr['user']['login'])
                if pr['merged_by'] and pr['merged_by']['type'] != 'Bot':
                    users['Contributor'].add(pr['merged_by']['login'])

                for comment in comments:
                    if comment['user']['type'] != 'Bot':
                        user_login = comment['user']['login']
                        days_since_commit = DateUtils.get_days_between_dates(comment['created_at'], pr['closed_at'])
                        # Check if user has commented before and after 180 days
                        if days_since_commit < 180:
                            users['New'].add(user_login)
                        else:
                            users['Left'].add(user_login)

                # fetch commit information and extract authors
                commits_url = pr['commits_url']
                commit_url = self.apiCall.request(commits_url)
                if commit_url:
                    for commit in commit_url:
                        if commit['author']:
                            if commit['author']['type'] != 'Bot':
                                days_since_commit = DateUtils.get_days_between_dates(commit['commit']['author']['date'], pr['closed_at'])

                                if days_since_commit < 180:
                                    users['New'].add(commit['author']['login'])
                                else:
                                    users['Left'].add(commit['author']['login'])

                # classify users as Contributors if they meet both requirements
                users['Contributor'] = users['Contributor'].union(users['New'].intersection(users['Left']))
                users['New'] = list(users['New'])
                users['Left'] = list(users['Left'])
                users['Contributor'] = list(users['Contributor'])
                #check if user is on the contributor list
                for user_check in users['Contributor']:
                    if user_check in users['New']:
                        users['New'].remove(user_check)
                    if user_check in users['Left']:
                        users['Left'].remove(user_check)
                print(users, 'from PR', pr_number)

                users_by_pr[pr_number] = users
        print(users_by_pr)

        return users_by_pr

    def save_team(self, team):

