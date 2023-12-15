import json
import re

from pymongo import MongoClient
from bson.json_util import loads


class MongoUtils:

    def __init__(self):
        self.projects = ['conductor']
        self.mongo_connection = MongoClient("mongodb://localhost:27017/")

    def load_data(self, source_folder='./'):

        for project in self.projects:
            source_folder = source_folder + '/' + project + '/'
            collections = ['comments', 'issues', 'pull_requests', 'commits']
            database = self.mongo_connection[project]

            for collection_name in collections:

                collection = database[collection_name]

                with open(source_folder + collection_name + '.json', 'r') as file:
                    file_data = json.loads(file.read())

                    for f in file_data:
                        f = json.dumps(f)
                        f = f.replace('False', 'false')
                        f = f.replace('True', 'true')
                        f = f.replace('None', 'null')
                        file_data = loads(f)
                        if not collection.find_one({'_id': file_data['_id']}):
                            collection.insert_one(file_data)



mongo_utils = MongoUtils()
mongo_utils.load_data('/Users/caio/Downloads/dump esem 2023/')
