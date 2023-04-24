from pymongo import MongoClient
from pymongo.database import Database


class Keywords:

    def __init__(self, database: Database = None):
        self.database = database

    def keywords(self):
