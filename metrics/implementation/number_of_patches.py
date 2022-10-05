import re
from os import listdir
from os.path import isfile, join

from pymongo.database import Database

from utils.csv_handler import CSVHandler
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class NumberSnippets:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database

    def get_snippet_metrics(self):
        """
        Collects the number, mean_size and size of snippets inside each comment of issues and pull requests.

        :return: list of the number of snippets per issue or pull request
        :rtype: list
        """
        print('#### Number of Snippets ####')

        database_comments = self.database['comments']

        comments = database_comments.find({'number_patches': {'$exists': False}})

        for comment in comments:
            patches = re.findall(r'```', comment['body'])

            if not patches:
                continue

            number_patches = len(patches)/2

            patch_size = 0

            patch_content = comment['body'].split('```')

            count = 1
            for patch in patch_content:
                if count % 2 == 0:
                    patch_size += len(patch.trim())
                count += 1

            patch_content_len = len(patch_content)
            if patch_content_len == 0:
                patch_content_len = 1

            mean_snippet = patch_size / (patch_content_len/2)

            database_comments.update_one({'id': comment['id']},
                                         {'$set': {'number_snippets': number_patches,
                                          'snippets_size': patch_size,
                                          'mean_snippets': mean_snippet}})

        comments = database_comments.aggregate([
            {
                '$group': {
                    '_id': '$issue_number',
                    'comments': {
                        '$push': {
                            'number_snippets': '$number_snippets',
                            'snippets_size': '$snippets_size',
                            'mean_snippets': '$mean_snippets'
                        }
                    }
                }
            }
        ])

        for comment in comments:
            issue_number = comment['_id']

            number_snippets = 0
            snippets_size = 0
            mean_snippets = 0
            for snippets in comment['comments']:
                number_snippets += snippets['number_snippets']
                snippets_size += snippets['snippets_size']
                mean_snippets += snippets['mean_snippets']

            if not self.database['pull_requests'].find_one({'number': issue_number}):
                self.database['pull_requests'].insert_one({'number': issue_number})

            self.database['pull_requests'].update_one({'number': issue_number}, {'$set':
                                        {'number_snippets': number_snippets,
                                          'snippets_size': snippets_size,
                                          'mean_snippets': mean_snippets}})

