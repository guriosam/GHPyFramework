from pymongo import MongoClient
from pymongo.database import Database


class Keywords:

    def __init__(self, database: Database = None):
        self.database = database

    def number_of_keywords(self, pr, keywords):
        collection = self.database['comments']
        comments = collection.find({'issue_number': pr['number']})

        keywords_quantity = 0
        for keyword in keywords:
            if keyword in pr['title']:
                keywords_quantity += 1

            if pr['body']:
                if keyword in pr['body']:
                    keywords_quantity += 1

        for comment in comments:
            for keyword in keywords:
                if keyword in comment['body']:
                    keywords_quantity += 1

        return keywords_quantity

    def density_of_comments(self, pr, quantity_of_keywords):
        collection = self.database['comments']
        comments = collection.find({})
        comments_quantity = 1  # +1 because of the pr title and body
        for comment in comments:
            if comment['issue_number'] != pr['number']:
                continue
            comments_quantity += 1

        return {pr['number']: quantity_of_keywords / comments_quantity}

    def get_pr_keywords(self):

        database_pulls = self.database['pull_requests']

        design_keywords = ['design', 'architect', 'dependenc', 'requir', 'interface', 'servic', 'artifact', 'document',
                           'behavior', 'modul']

        refactoring_keywords = ['refactor', 'mov', 'split', 'fix', 'introduc', 'decompos', 'reorganiz', 'extract',
                                'merg', 'renam', 'chang',
                                'restructur', 'reformat', 'extend', 'remov', 'replac', 'rewrit', 'simplif', 'creat',
                                'improv', 'add', 'modif', 'enhanc', 'rework',
                                'inlin', 'redesign', 'cleanup', 'reduc', 'encapsulat']

        prs = database_pulls.find({})

        database_metrics = self.database['metrics']

        for pr in prs:

            issue_number = pr['number']
            number_comments = pr['comments']

            if number_comments == 0:
                number_comments = 1

            number_design_keywords = self.number_of_keywords(pr, design_keywords)
            number_refactoring_keywords = self.number_of_keywords(pr, refactoring_keywords)
            density_design_keywords = number_design_keywords / number_comments
            density_refactoring_keywords = number_refactoring_keywords / number_comments

            if not database_metrics.find_one({"issue_number": issue_number}):
                database_metrics.insert_one({"issue_number": issue_number})

            database_metrics.update_one({"issue_number": issue_number},
                                        {'$set': {'number_design_keywords': number_design_keywords,
                                                  'number_refactoring_keywords': number_refactoring_keywords,
                                                  'density_design_keywords': density_design_keywords,
                                                  'density_refactoring_keywords': density_refactoring_keywords}})
