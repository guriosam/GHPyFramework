#!/usr/bin/env python

"""
This class is responsible for running all the api collection methods for the implemented types.
"""

from os import listdir
from os.path import isfile, join

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
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class APICollector(object):

    def __init__(self):
        self.config = JSONHandler('../').open_json('config.json')
        self.projects = self.config['projects']

    def collect_issues(self, owner: str, project: str):
        """

        :param owner:
        :type owner:
        :param project:
        :type project:
        :return:
        :rtype:
        """
        print('Collecting Issues')
        return self.collect_all(project, IssueAPI(owner, project), 'issues', 'number', IssueDAO())

    def collect_pulls(self, owner: str, project: str):
        """

        :param owner:
        :type owner:
        :param project:
        :type project:
        :return:
        :rtype:
        """
        print('Collecting Pulls')
        return self.collect_all(project, PullsAPI(owner, project), 'pulls', 'number', PullRequestDAO())

    def collect_commits(self, owner: str, project: str):
        """

        :param owner:
        :type owner:
        :param project:
        :type project:
        :return:
        :rtype:
        """
        print('Collecting Commits')
        return self.collect_all(project, CommitAPI(owner, project), 'commits', 'sha', CommitDAO())

    def collect_comments(self, owner: str, project: str):
        """

        :param owner:
        :type owner:
        :param project:
        :type project:
        """
        print('Collecting Issues Comments')
        self.collect_all(project, CommentAPI(owner, project), 'comments/issues/', 'issue_url', CommentDAO())

    def collect_events(self, owner: str, project: str):
        """

        :param owner:
        :type owner:
        :param project:
        :type project:
        :return:
        :rtype:
        """
        print('Collecting Issues Events')
        return self.collect_all(project, PrototypeAPI(owner, project, '/events/', '/issues/events'), 'events', 'id', EventDAO())

    def collect_all(self, project: str, collector: APIInterface, folder: str, identifier: str, objectDAO: DAOInterface):
        """
        :param project:
        :param collector:
        :param folder:
        :param identifier:
        :param objectDAO:
        """
        collector.collect_batch()
        mypath = self.config['output_path'] + project + '/' + folder + '/all/'
        json = JSONHandler(mypath)
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        refs = []
        for file in onlyfiles:
            json_objects = json.open_json(file)
            for object in json_objects:
                if object[identifier] not in refs:
                    refs.append(object[identifier])

        DAOs = []

        for ref in refs:

            obj = collector.collect_single(ref)
            try:
                if type(obj) is list:
                    for ob in obj:
                        objectDAO.read_from_json(ob)
                        DAOs.append(objectDAO.__dict__.copy())
                else:
                    objectDAO.read_from_json(obj)
                    DAOs.append(objectDAO.__dict__.copy())

            except Exception as e:
                print('Something went wrong in: ' + str(ref) + ' on object ' + str(obj))
                print(e)

        json = JSONHandler(self.config['output_path'] + project + '/')
        json.save_json(DAOs, project + '_' + folder.split('/')[0])

        return DAOs

    def collect_commits_on_pulls(self, owner: str, repo: str):
        """

        :param owner:
        :type owner:
        :param repo:
        :type repo:
        :return:
        :rtype:
        """
        print('Collecting Pull Requests Commits')

        pulls = []
        mypath = self.config['output_path'] + repo + '/pulls/all/'
        json = JSONHandler(mypath)
        commits_json = JSONHandler(self.config['output_path'] + repo + '/pulls_commits/commits/')
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        for file in onlyfiles:
            batch = json.open_json(file)
            for pull in batch:
                pulls.append(pull['number'])

        hashs = []

        for pull in pulls:
            if JSONHandler.file_exists(
                    self.config['output_path'] + repo + '/pulls_commits/commits/' + str(pull) + '.json'):
                commits_pull = commits_json.open_json(
                    str(pull) + '.json')
                for commit_pull in commits_pull:
                    for commit in commit_pull:
                        hashs.append(commit['sha'])
                continue

            pullsEndpoint = PrototypeAPI(owner, repo, '/pulls_commits/', '/pulls/' + str(pull) + '/commits')
            files = pullsEndpoint.collect_batch(False)
            commits_json.save_json(files, str(pull))

        commitsEndpoint = PrototypeAPI(owner, repo, '/pulls_commits/', '/commits')
        aux = 1
        for hash in hashs:
            if not hash:
                continue
            commitsEndpoint.collect_single(hash)
            print(str(aux*100 / len(hashs)) + "%")
            aux = aux + 1

        return hashs
