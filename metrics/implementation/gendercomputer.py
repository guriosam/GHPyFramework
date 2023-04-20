from gender_extractor import GenderExtractor
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



