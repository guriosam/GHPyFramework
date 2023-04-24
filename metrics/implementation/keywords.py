from pymongo import MongoClient
from pymongo.database import Database


class Keywords:

    def __init__(self, database: Database = None):
        self.database = database

    def number_of_keywords(self, pr, keywords):
        collection = self.database['comments']
        comments = collection.find({})

        keywords_quantity = 0
        for keyword in keywords:
            if keyword in pr['title']:
                keywords_quantity += 1
        if pr['body']:
            for keyword in keywords:
                if keyword in pr['body']:
                    keywords_quantity += 1
        for comment in comments:
            if comment['issue_number'] != pr['number']:
                continue
            for keyword in keywords:
                if keyword in comment['body']:
                    keywords_quantity += 1

        return {pr['number']: keywords_quantity}

    def density_of_comments(self, pr, quantity_of_keywords):
        collection = self.database['comments']
        comments = collection.find({})
        comments_quantity = 1 #+1 because of the pr title and body
        for comment in comments:
            if comment['issue_number'] != pr['number']:
                continue
            comments_quantity += 1

        return {pr['number']: quantity_of_keywords / comments_quantity}


    def get_pr_keywords(self):

        collection = self.database['pull_requests']
        design_keywords = ['design', 'architect', 'dependenc', 'requir', 'interface', 'servic', 'artifact', 'document',
                           'behavior', 'modul']
        refactoring_keywords = ['refactor', 'mov', 'split', 'fix', 'introduc', 'decompos', 'reorganiz', 'extract',
                                'merg', 'renam', 'chang',
                                'restructur', 'reformat', 'extend', 'remov', 'replac', 'rewrit', 'simplif', 'creat',
                                'improv', 'add', 'modif', 'enhanc', 'rework',
                                'inlin', 'redesign', 'cleanup', 'reduc', 'encapsulat']

        prs = collection.find({})
        pr_design_keywords = {}
        pr_refactoring_keywords = {}
        pr_design_density = {}
        pr_refactoring_density = {}

        for pr in prs:
            pr_design_keywords.update(self.number_of_keywords(pr, design_keywords))
            pr_refactoring_keywords.update(self.number_of_keywords(pr, refactoring_keywords))
            pr_design_density.update(self.density_of_comments(pr, pr_design_keywords[pr['number']]))
            pr_refactoring_density.update(self.density_of_comments(pr, pr_refactoring_keywords[pr['number']]))

            self.database['metrics'].update_one({"issue_number": pr['number']},
                                                {'$set': {'design_keyword': pr_design_keywords[pr['number']],
                                                          'refactoring_keyword': pr_refactoring_keywords[pr['number']],
                                                          'design_density': pr_design_density[pr['number']],
                                                          'refactoring_density': pr_refactoring_density[pr['number']]}})

        print(pr_design_keywords)
        print(pr_refactoring_keywords)
        print(pr_design_density)
        print(pr_refactoring_density)

