from pymongo import MongoClient
from pymongo.database import Database


class Keywords:

    def __init__(self, database: Database = None):
        self.database = database

    def get_comments_keywords(self, pr_number):
        collection = self.database['comments']
        comments = collection.find({})
        keywords = ['design', 'architect', 'dependenc', 'requir', 'interface', 'servic', 'artifact', 'document', 'behavior', 'modul']
        for comment in comments:
            if comment['issue_number'] is not pr_number:
                continue
            for keyword in keywords:
                if keyword in comment['body']:



    def get_prs(self):
        collection = self.database['pull_requests']
        prs = collection.find({})
        for pr in prs:
            self.get_comments(pr['number'])

    def get_pr_keywords(self):
        collection = self.database['pull_requests']
        prs = collection.find({})
        for pr_number in prs:
            self.get_comments_keywords(pr_number['number'])