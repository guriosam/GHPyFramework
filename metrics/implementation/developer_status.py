from os import listdir
from os.path import isfile, join
from utils.csv_handler import CSVHandler
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class DeveloperStatus:

    def __init__(self, project):
        config = JSONHandler('../').open_json('config.json')
        self.project = project
        self.path = config['output_path']
        self.users_comments = self._get_users_labels_in_comments()
        self.users_issues = self._get_users_labels_in_issues_and_pulls()

    def number_of_users(self):
        """
        Collect the amount of users with author_association equals to NONE, FIRST_TIMER and FIRST_TIME_CONTRIBUTOR on the comments
        :return: list of amount of users with author_association equal to NONE, FIRST_TIMER and FIRST_TIME_CONTRIBUTOR per issue/pull request
        :rtype: list
        """
        print("#### Number of Users ####")

        users = [['id', 'count']]
        for k in self.users_comments.keys():
            count = 0
            if k in self.users_comments.keys():
                for association in self.users_comments[k]:
                    if association == 'NONE' or association == 'FIRST_TIMER' or association == 'FIRST_TIME_CONTRIBUTOR':
                        count += 1
            if k in self.users_issues.keys():
                for association in self.users_issues[k]:
                    if association == 'NONE' or association == 'FIRST_TIMER' or association == 'FIRST_TIME_CONTRIBUTOR':
                        count += 1
            users.append([k, count])

        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_number_of_users.csv',
                      users)

        return users

    def number_of_contributors(self):
        """
        Collect the amount of users with author_association equals to CONTRIBUTOR and COLLABORATOR on the comments
        :return: list of amount of users with author_association equal to CONTRIBUTOR and COLLABORATOR per issue/pull request
        :rtype: list
        """
        print("#### Number of Contributors ####")

        contributors = [['id', 'count']]
        for k in self.users_comments.keys():
            count = 0
            if k in self.users_comments.keys():
                for association in self.users_comments[k]:
                    if association == 'CONTRIBUTOR' or association == 'COLLABORATOR':
                        count += 1
            if k in self.users_issues.keys():
                for association in self.users_issues[k]:
                    if association == 'CONTRIBUTOR' or association == 'COLLABORATOR':
                        count += 1
            contributors.append([k, count])

        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_number_of_contributors.csv',
                      contributors)

        return contributors

    def number_of_core_devs(self):
        """
        Collect the amount of users with author_association equals to MEMBER and OWNER on the comments
        :return: list of amount of users with author_association equal to MEMBER and OWNER per issue/pull request
        :rtype: list
        """
        print("#### Number of Core Members ####")

        core = [['id', 'count']]
        for k in self.users_comments.keys():
            count = 0
            if k in self.users_comments.keys():
                for association in self.users_comments[k]:
                    if association == 'MEMBER' or association == 'OWNER':
                        count += 1
            if k in self.users_issues.keys():
                for association in self.users_issues[k]:
                    if association == 'MEMBER' or association == 'OWNER':
                        count += 1
            core.append([k, count])

        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_number_of_core_developers.csv',
                      core)

        return core

    def _get_users_labels_in_comments(self):
        """
        Collects the author_association of each comment on issue/pull requests
        :return: lists of author_associations per issue/pull requests
        :rtype: list
        """
        mypath = self.path + self.project + '/comments/individual/'
        json = JSONHandler(mypath)

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        users = {}
        hash = {}
        for file in onlyfiles:
            comments = json.open_json(file)
            for comment in comments:
                issue = comment['issue_url'].split('/')
                issue = issue[len(issue) - 1]

                if issue not in users.keys():
                    users[issue] = []

                if str(issue + comment['user']['login']) not in hash.keys():
                    hash[issue + comment['user']['login']] = 0
                    users[issue].append(comment['author_association'])

        return users

    def _get_users_labels_in_issues_and_pulls(self):
        """
        Collects the author_association of issue/pull requests (opened, closed or merged)
        :return: lists of author_associations per issue/pull requests
        :rtype: list
        """
        path = self.path + '/' + self.project
        json = JSONHandler(path + '/')
        issues = json.open_json(self.project + '_issues.json')
        pulls = json.open_json(self.project + '_pulls.json')

        # author_association = [['id', 'association', 'created_at']]
        author_association = {}
        for issue in issues:
            if issue['author_association']:
                # author_association.append([issue['issue_number'], issue['author_association'], issue['created_at']])
                author_association[issue['issue_number']] = issue['author_association']

        for pull in pulls:
            if pull['author_association']:
                author_association[pull['pull_request_number']] = pull['author_association']
                # author_association.append([pull['pull_request_number'], pull['author_association'], pull['created_at']])

        return author_association
        # csv = CSVHandler()
        # csv.write_csv(self.path + '/' + self.project + '/metrics/', 'author_association.csv', author_association)
