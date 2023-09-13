#!/usr/bin/env python

"""
This class is responsible for running all the api collection methods for the implemented types.
"""

from os import listdir
from os.path import isfile, join

from pymongo.database import Database

from api.dao.commentDAO import CommentDAO
from api.dao.commitDAO import CommitDAO
from api.dao.dao_interface import DAOInterface
from api.dao.eventDAO import EventDAO
from api.dao.issueDAO import IssueDAO
from api.dao.pullrequestDAO import PullRequestDAO
from api.endpoint.api_interface import APIInterface
from api.endpoint.comment import CommentAPI
from api.endpoint.commit import CommitAPI
from api.endpoint.issue import IssueAPI
from api.endpoint.prototypeAPI import PrototypeAPI
from api.endpoint.pullrequest import PullsAPI
from api.endpoint.users import UsersAPI
from utils.common_mongo_queries import CommonQueries
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"


class APICollector(object):

    def __init__(self, project_name: str, database: Database):
        self.project_name = project_name
        self.database = database

    def collect_issues(self, owner: str, project: str):
        """
        Collect Issues from the GitHub API
        :param owner: repository owner
        :type owner: str
        :param project: project name
        :type project: str
        :return: list of issues
        :rtype: list
        """
        print('Collecting Issues')
        return self.collect_all('Issue', IssueAPI(owner, project, self.database), 'number')

    def collect_pulls(self, owner: str, project: str):
        """
        Collect Pull Requests from the GitHub API
        :param owner: repository owner
        :type owner: str
        :param project: project name
        :type project: str
        :return: list of pull requests
        :rtype: list
        """
        print('Collecting Pulls')
        return self.collect_all('Pull Request', PullsAPI(owner, project, self.database), 'number')

    def collect_commits(self, owner: str, project: str):
        """
        Collect Commits from the GitHub API
        :param owner: repository owner
        :type owner: str
        :param project: project name
        :type project: str
        :return: list of commits
        :rtype: list
        """
        print('Collecting Commits')
        return self.collect_all('Commit', CommitAPI(owner, project, self.database), 'sha')

    def collect_comments(self, owner: str, project: str):
        """
        Collect Comments from the GitHub API
        :param owner: repository owner
        :type owner: str
        :param project: project name
        :type project: str
        :return: list of comment
        :rtype: list
        """
        print('Collecting Issues Comments')
        self.collect_all('Comment', CommentAPI(owner, project, self.database), 'issue_url')

    # def collect_events(self, owner: str, project: str):
    #     """
    #     Collect Events from the GitHub API
    #     :param owner: repository owner
    #     :type owner: str
    #     :param project: project name
    #     :type project: str
    #     :return: list of events
    #     :rtype: list
    #     """
    #     print('Collecting Issues Events')
    #     return self.collect_all(project, PrototypeAPI(owner, project, '/events/', '/issues/events', self.database),
    #                             'events', 'id',
    #                             EventDAO())

    def collect_all(self, endpoint,  collector: APIInterface, identifier: str):
        """
        :param collector: the collector to be called
        :param identifier: information to collect the specific data for the api type
        """

        if 'review_comments_url' in identifier:
            elements = collector.collect_batch(review=True)
            return
        else:
            elements = collector.collect_batch()

        refs = []
        flag = False

        if elements:
            for el in elements:
                    refs.append(el[identifier])
            flag = True

        if flag:
            size = len(refs)
            count = 0
            for ref in refs:
                print(endpoint + ': ' + str(count) + '/' + str(size) + ' for project ' + self.project_name)
                obj, end = collector.collect_single(ref)
                count += 1
                if end:
                    break
        else:
            collector.collect_batch()


    def collect_commits_on_pulls(self, owner: str, project: str):
        """
        Collect Commits from Pull Requests from the GitHub API
        :param owner: repository owner
        :type owner: str
        :param project: project name
        :type project: str
        :return: list of commits from pull requests
        :rtype: list
        """
        print('Collecting Pull Requests Commits')

        pulls = []
        mypath = self.config['output_path'] + project + '/pulls/all/'
        json = JSONHandler(mypath)
        commits_json = JSONHandler(self.config['output_path'] + project + '/pulls_commits/commits/')
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        for file in onlyfiles:
            batch = json.open_json(file)
            for pull in batch:
                pulls.append(pull['number'])

        hashs = []

        for pull in pulls:
            if JSONHandler.file_exists(
                    self.config['output_path'] + project + '/pulls_commits/commits/' + str(pull) + '.json'):
                commits_pull = commits_json.open_json(
                    str(pull) + '.json')
                for commit_pull in commits_pull:
                    for commit in commit_pull:
                        hashs.append(commit['sha'])
                continue

            pullsEndpoint = PrototypeAPI(owner, project, '/pulls_commits/', '/pulls/' + str(pull) + '/commits')
            files = pullsEndpoint.collect_batch(False)
            commits_json.save_json(files, str(pull))

        commitsEndpoint = PrototypeAPI(owner, project, '/pulls_commits/', '/commits')
        aux = 1
        for hash in hashs:
            if not hash:
                continue
            commitsEndpoint.collect_single(hash)
            print(str(aux * 100 / len(hashs)) + "%")
            aux = aux + 1

        return hashs

    def collect_comments_pulls(self, owner: str, project: str):
        print('Collecting Pulls Comments')
        self.collect_all(project, CommentAPI(owner, project, self.database), 'review_comments_url')

    def collect_users(self, owner: str, project: str):
        """
        Collect Users from the GitHub API
        :param owner: repository owner
        :type owner: str
        :param project: project name
        :type project: str
        :param users: list of users
        :type users: list
        :return: list of users
        :rtype: list
        """
        print('Collecting Users')
        user_api = UsersAPI(owner, project, self.database)

        users = set()

        prs_by_user = CommonQueries.get_user_interactions(self.database['pull_requests'], 'user_pulls', 'pr_number',
                                                          '$number')
        comments_by_user = CommonQueries.get_user_interactions(self.database['comments'], 'user_comments', 'comment_id',
                                                               '$id')
        commits_by_user = CommonQueries.get_user_interactions(self.database['commits'], 'user_commits', 'commit',
                                                              '$sha')

        for user in prs_by_user:
            users.add(user['_id'])

        for user in comments_by_user:
            users.add(user['_id'])

        for user in commits_by_user:
            users.add(user['_id'])

        for user in users:
            if not user:
                continue
            user_api.collect_single(user)
