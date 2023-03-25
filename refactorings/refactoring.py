import json
import os.path

from pymongo.database import Database


class RefactoringManager:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database

    @staticmethod
    def _read_from_refactoring_files(path):

        if not os.path.isfile(path):
            return {}

        with open(path, 'r') as f:
            return json.load(f)

    def _save_on_mongo(self, refactorings):

        database_commits = self.database['commits']
        for refactoring in refactorings:
            hash_commit = refactoring['hash_commit']

            if not database_commits.find_one({'sha': hash_commit}):
                continue

            database_commits.update_one({'sha': hash_commit},
                                        {
                                         '$set':
                                            {
                                                'number_refactorings': refactoring['num_refactorings'],
                                                'list_refactorings': refactoring['list_refactorings'],
                                                'refactored': True
                                            }
                                        })


    def run(self):
        refactorings = self._read_from_refactoring_files('data/refactoring-summary/' + self.repo + '.json')
        self._assert_empty_fields_on_mongo()
        self._save_on_mongo(refactorings)
        pass

    def _assert_empty_fields_on_mongo(self):
        database_commits = self.database['commits']

        commits = database_commits.find({})

        for commit in commits:
            if 'refactored' in commit.keys():
                continue

            hash_commit = commit['sha']

            database_commits.update_one({'sha': hash_commit},
                                        {
                                            '$set':
                                                {
                                                    'number_refactorings': 0,
                                                    'list_refactorings': [],
                                                    'refactored': False
                                                }
                                        })


