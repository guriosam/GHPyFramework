#from gender_extractor import GenderExtractor
from pymongo import MongoClient
from pymongo.database import Database

from api.api_collector import APICollector
from api.endpoint.users import UsersAPI


class GenderDiversity:

    def __init__(self, database: Database = None):
        self.database = database

    def gender(self):

        #client = MongoClient("localhost", 27017)
        #db = client['Netflix-zuul']
        collection = self.database['commits']

        commits = collection.find({})
        users = set()
        for commit in commits:

            if not commit['author']:
                continue

            if "Bot" not in commit['author']['type']:
                user = commit['author']['login']
                users.add(user)

        print(users)
        return users

    def gender_extraction(self):

        collection = self.database['users_api']
        names = collection.find({})
        genero = []
        c = GenderExtractor()
        collection = self.database['users']
        for name in names:
            if name['name']:
                full_name = name['name']
                first_name = full_name.split()[0]
                if name['location']:
                    pass
                    userinfo = gc.extract_gender(first_name, name['location'])
                    genero.append(userinfo)
                else:
                    pass
                    userinfo = gc.extract_gender(first_name)
                    genero.append(userinfo)
                collection.update_one({"username": name['login']},{'$set': {'gender': userinfo}})


        print(genero)



