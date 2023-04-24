

class CommonQueries:

    def __init__(self):
        pass

    @staticmethod
    def get_user_interactions(database, group_key, push_key, push_value):
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
