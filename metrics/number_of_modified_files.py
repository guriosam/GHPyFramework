from os import listdir
from os.path import isfile, join

from pymongo.database import Database


class NumberModifiedFiles:

    def __init__(self, database: Database):
        self.database = database

    def get_modified_files_on_commits(self):

        commits = self.database['commits'].find({'number_of_java_files': None})

        updated_shas = []

        for commit in commits:

            files = commit['files']

            if not files:
                continue

            count = 0
            for mf in files:
                if '.java' not in mf['filename']:
                    continue
                count += 1

            #self.database['commits'].aggregate([{'$group': {'_id':None, 'files': {'$avg': '$number_of_java_files'} }}])
            self.database['commits'].update_one({'sha': commit['sha']}, {"$set": {'number_of_java_files': count}})
            updated_shas.append(commit['sha'])

        return updated_shas
