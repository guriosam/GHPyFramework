from gender_extractor import GenderExtractor
from pymongo import MongoClient
from pymongo.database import Database

from api.api_collector import APICollector
from api.endpoint.users import UsersAPI
from utils.common_mongo_queries import CommonQueries


class GenderDiversity:

    def __init__(self, database: Database = None):
        self.database = database
        self.extractor = GenderExtractor()

    def gender_extraction(self):
        collection_users_api = self.database['users_api']
        names = collection_users_api.find({})

        genders = []

        collection_users = self.database['users']
        for name in names:
            if not name['name']:
                continue

            first_name = name['name'].split()[0]

            location = None
            if name['location']:
                location = name['location']

            user_info = self.extractor.extract_gender(first_name, country=location)
            genders.append(user_info)

            if not collection_users.find_one({"username": name['login']}):
                collection_users.insert_one({"username": name['login']})

            collection_users.update_one({"username": name['login']}, {'$set': {'gender': user_info}})

        print(genders)

    def team_gender(self):
        prs = self.database['pull_requests'].find({})

        for pr in prs:

            if not pr['merged']:
                continue

            users = {'contributor': set()}

            users = CommonQueries.collect_participating_users(self.database, pr, users)

            males = 0
            females = 0

            for user in users['contributor']:

                if not self.database['users'].find_one({"username": user}):
                    self.database['users'].insert_one({"username": user})
                    print('This user should already exist in the database: ' + user)

                user_obj = self.database['users'].find_one({'username': user})

                if 'gender' not in user_obj.keys():
                    continue

                user_gender = user_obj['gender']

                if not user_gender:
                    continue

                if 'female' in user_gender:
                    females += 1
                else:
                    males += 1

            self.database['metrics'].update_one({'issue_number': pr['number']},
                                                      {'$set': {'number_males': males,
                                                                'number_females': females}})
