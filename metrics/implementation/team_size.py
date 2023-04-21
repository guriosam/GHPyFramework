from pymongo.database import Database

class teamSize:

    def __init__(self, database: Database = None):
        self.database = database

    def teste(self):
        collections_pull_resquest = self.database['pull_requests']
        numbers = collections_pull_resquest.find({})
        collections_comments = self.database['comments']

        prnumbers = set()
        users_comments = []
        comments_user = []
        users_team = {}
        for number in numbers:
            prnumbers.add(number['number'])
            comments = collections_comments.find({})
            for comment in comments:
                if comment['issue_number'] == number['number']:
                    comments_user.append(comment['user']['login'])
                    users_team[number['number']] = comments_user
                    comments_user.clear()
            users_comments.append(users_team)
        print(users_comments)

    def _get_user_info(database, group_key, push_key, push_value):

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

"""    def get_team(self):

        collection = self.database['users']
        users = collection.find({})
        if 'users_api' not in self.database.name:
            self.database = self.database['team_users']
        team = set()
        collection = self.database
        for user in users:
            try:
                if user['turnover'] != 'Left' or user['turnover'] is None:
                    if user['interacted_before_180_days'] and user['interacted_within_180_days']:
                        team.add(user['username'])
                        collection.insert_one(user)
            except:
                print('Errooouuu')

"""