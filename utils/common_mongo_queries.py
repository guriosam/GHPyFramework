from pymongo.database import Database


class CommonQueries:

    def __init__(self):
        pass

    @staticmethod
    def get_user_interactions(database, group_key, push_key, push_value):
        push = {push_key: push_value, 'created_at': '$created_at'}
        push_commit = {push_key: push_value, 'created_at': '$commit.author.date'}

        if 'commit' in group_key:
            push = push_commit

            return list(database.aggregate([
                {
                    '$group': {
                        '_id': '$author.login',
                        group_key: {
                            '$push': push
                        }
                    }
                }, {
                    '$sort': {
                        'created_at': -1
                    }
                }
            ]))

        return list(database.aggregate([
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
        ]))

    @staticmethod
    def collect_participating_users(database, pr: dict, users: dict):
        users = CommonQueries._collect_users_in_comments(database, pr['number'], users)

        if pr['user'] and 'Bot' not in pr['user']['type']:
            users['contributor'].add(pr['user']['login'])
        if pr['merged_by'] and 'Bot' not in pr['merged_by']['type']:
            users['contributor'].add(pr['merged_by']['login'])

        return users

    @staticmethod
    def _collect_users_in_comments(database, pr_number: int, users: dict):
        comments = database['comments'].find({'issue_number': pr_number})

        for comment in comments:
            if comment['user']['type'] != 'Bot':
                user_login = comment['user']['login']
                users['contributor'].add(user_login)

        return users

