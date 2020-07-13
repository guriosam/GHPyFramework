from os import listdir
from os.path import isfile, join

from utils.csv_handler import CSVHandler
from utils.json_handler import JSONHandler
from utils.text_processing import TextProcessing

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class WordsInDiscussion:

    def __init__(self, project: str):
        config = JSONHandler('../').open_json('config.json')
        self.project = project
        self.path = config['output_path']

    def get_words_in_discussion(self):
        """
        Get number of words of all comments on an issue or pull request
        :return: sum of all words of all comments of an issue or pull request, per pull request or issue
        :rtype: list
        """
        print("#### Words in Discussions ####")

        _, words_in_discussion = self._get_comments_in_discussion()

        words_per_discussion = [['issue', 'number_words']]

        for key in words_in_discussion.keys():
            words_per_discussion.append([key, words_in_discussion[key]])

        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_words_in_discussion.csv',
                      words_per_discussion)

        return words_per_discussion

    def get_words_per_comment_in_discussion(self):
        """
        Get number of words of all comments on an issue or pull request
        :return: sum of all words of all comments of an issue or pull request, per pull request or issue
        :rtype: list
        """
        print("#### Words/Comments in Discussions ####")

        comments_in_discussion, words_in_discussion = self._get_comments_in_discussion()

        words_per_comments_in_discussion = [['issue', 'number_words_per_comment']]

        for key in comments_in_discussion.keys():
            # print(str(key) + ': ' + str(comments_per_issue[key]))
            words_per_comments_in_discussion.append([key, str(words_in_discussion[key] / comments_in_discussion[key])])
        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_words_per_comments_in_discussion.csv',
                      words_per_comments_in_discussion)

        return words_per_comments_in_discussion

    def _get_comments_in_discussion(self):
        """
        Collect comments of each issue and pull request and the number of words of each comment
        :return: two lists, one containing the comments in issues/pull requests and another with the words per issue/pull request.
        :rtype: list, list
        """
        mypath = self.path + self.project + '/comments/individual/'
        json = JSONHandler(mypath)
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        words_in_discussion = {}
        comments_in_discussion = {}

        for file in onlyfiles:
            comments = json.open_json(file)
            for comment in comments:
                if 'issue_url' in comment.keys():
                    issue = comment['issue_url'].split('/')
                    issue = issue[len(issue) - 1]

                    if issue not in words_in_discussion.keys():
                        words_in_discussion[issue] = 0
                    if issue not in comments_in_discussion.keys():
                        comments_in_discussion[issue] = 0

                    tp = TextProcessing()
                    processed = tp.pre_process_text(comment['body'])
                    comment_text = ''
                    for token in processed:
                        comment_text += token + ' '
                    words_in_discussion[issue] += len(comment_text.split(' '))
                    comments_in_discussion[issue] += 1

        return comments_in_discussion, words_in_discussion
