from os import listdir
from os.path import isfile, join

from pymongo.database import Database

from utils.csv_handler import CSVHandler
from utils.json_handler import JSONHandler
from utils.date import DateUtils

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

from utils.text_cleaning import TextCleaner


class TimeBetweenReplies:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database


    def mean_time_between_replies(self):
        """
        Collect the mean time between comments inside an issue or pull request
        """
        print('#### Mean Time Between Comments ####')

        database = self.database['comments']
        database_metrics = self.database['metrics']
        database_pulls = self.database['pull_requests']

        comments_by_issue = database.aggregate([{
                '$group': {
                    '_id': '$issue_number',
                    'comments': {
                        '$addToSet': {
                            'body': '$body',
                            'created_at': '$created_at'
                        }
                    }
                }
            },{
                '$sort': {
                    'created_at': -1
                }
            }
        ])

        for comments_obj in comments_by_issue:
            issue_number = comments_obj['_id']

            comments = comments_obj['comments']


            total = 0
            delta = 0
            for i in range(0, len(comments) - 1):
                delta = DateUtils().get_days_between_dates(comments[i]['created_at'], comments[i+1]['created_at'])

                if delta < 0:
                    delta = delta * -1
                total += delta

            mean_comments = 0

            if len(comments) > 0:
                mean_comments = total/len(comments)


            total_words = 0
            cleaning = TextCleaner()
            for comment in comments:
                body = comment['body']
                body = cleaning.clean(body)
                total_words += len(body)

            mean_words = 0
            if len(comments) > 0:
                mean_words = total_words/len(comments)

            if database_pulls.find_one({"number": issue_number}):
                database_pulls.update_one({"number": issue_number},
                                          {'$set':
                                               {'mean_time_between_comments': mean_comments,
                                                'mean_number_of_words': mean_words,
                                                'number_of_words': total_words}})
            else:
                database_pulls.insert_one({"number": issue_number,
                                           'mean_time_between_comments': mean_comments, 'mean_number_of_words': mean_words,
                                           'number_of_words': total_words})

            if database_metrics.find_one({"issue_number": issue_number}):
                database_metrics.update_one({"issue_number": issue_number},
                                          {'$set':
                                               {'mean_time_between_comments': mean_comments,
                                                'mean_number_of_words': mean_words,
                                                'number_of_words': total_words}})
            else:
                database_metrics.insert_one({"issue_number": issue_number,
                                           'mean_time_between_comments': mean_comments, 'mean_number_of_words': mean_words,
                                           'number_of_words': total_words})


    def mean_time_between_open_and_first_last_and_merge(self):
        """
        Collect the mean time between ------ inside an issue or pull request
        """
        print('#### Mean Time Between Open and First Comment ####')

        database = self.database['comments']
        database_metrics = self.database['metrics']
        database_pulls = self.database['pull_requests']

        comments_by_issue = database.aggregate([{
                '$group': {
                    '_id': '$issue_number',
                    'comments': {
                        '$addToSet': {
                            'body': '$body',
                            'created_at': '$created_at'
                        }
                    }
                }
            },{
                '$sort': {
                    'created_at': -1
                }
            }
        ])

        for comments_obj in comments_by_issue:
            issue_number = comments_obj['_id']

            pull = database_pulls.find_one({'number': issue_number})

            comments = comments_obj['comments']

            if not comments:
                continue

            first_comment = comments[0]

            last_comment = comments[-1]


            delta_first = DateUtils().get_days_between_dates(pull['created_at'], first_comment['created_at'])

            if delta_first < 0:
                delta_first = delta_first * -1

            merge = pull['merged_at']
            if not merge:
                merge = last_comment['created_at']
            delta_last = DateUtils().get_days_between_dates(last_comment['created_at'], merge)

            if delta_last < 0:
                delta_last = delta_last * -1


            if not database_metrics.find_one({'issue_number': issue_number}):
                database_metrics.insert_one({'issue_number': issue_number})

            database_metrics.update_one({'issue_number': issue_number}, {'$set':
                                                                             {
                                                                                'open_and_first': delta_first,
                                                                                'last_and_close': delta_last}
                                                                        })

