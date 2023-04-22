from pymongo.database import Database
from utils.api_call_handler import APICallHandler

class teamSize:

    def __init__(self, database: Database = None):
        self.database = database

        self.api_url = 'https://api.github.com/'
        self.apiCall = APICallHandler()

    def teste(self):

        collection_pull_request = self.database['pull_requests']
        collection_comments = self.database['comments']
        collection_commits = self.database['commits']

        pr_numbers = collection_pull_request.find({})
        commits = collection_commits.find({})
        users_by_pr = {}

        for pr in pr_numbers:
            pr_number = pr['number']
            comments = self.database['comments'].find({'issue_number': pr_number})
            users = set()  # Use a set to avoid duplicates

            #add creator and who merged the pr
            users.add(pr['user']['login'])
            if pr['merged_by']:
                users.add(pr['merged_by']['login'])


            for comment in comments:
                users.add(comment['user']['login'])

            #fetch commit information and extract authors
            commits_url = pr['commits_url']
            commit_url = self.apiCall.request(commits_url)
            if commit_url:
                for commit in commit_url:
                    users.add(commit['commit']['author']['name'])
                    print(commit['commit']['author']['name'], 'in PR', pr_number)
            users_by_pr[pr_number] = list(users)

        print(users_by_pr)

