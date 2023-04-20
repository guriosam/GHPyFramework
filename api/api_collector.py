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
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"


class APICollector(object):

    def __init__(self, database: Database):
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
        return self.collect_all(project, IssueAPI(owner, project, self.database), 'number')

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
        return self.collect_all(project, PullsAPI(owner, project, self.database), 'number')

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
        return self.collect_all(project, CommitAPI(owner, project, self.database), 'sha')

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
        self.collect_all(project, CommentAPI(owner, project, self.database), 'issue_url')

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

    def collect_all(self, project: str, collector: APIInterface, identifier: str):
        """
        :param project: project name
        :param collector: the collector to be called
        :param folder: output folder for the data
        :param identifier: information to collect the specific data for the api type
        """

        if 'review_comments_url' in identifier:
            elements = collector.collect_batch(review = True)
            return
        else:
            elements = collector.collect_batch()



        # mypath = self.config['output_path'] + project + '/' + folder + '/all/'
        # json = JSONHandler(mypath)
        # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        refs = []
        flag = False

        if elements:
            for element in elements:
                for el in element:
                    refs.append(el[identifier])
            flag = True

        # DAOs = []

        if flag:
            for ref in refs:

                obj = collector.collect_single(ref)
        else:
            collector.collect_batch()


            #if obj:
            #    flag = True
            # try:
            #    if type(obj) is list:
            #        for ob in obj:
            #            objectDAO.read_from_json(ob)
            #            DAOs.append(objectDAO.__dict__.copy())
            #    else:
            #        objectDAO.read_from_json(obj)
            #        DAOs.append(objectDAO.__dict__.copy())

            # except Exception as e:
            #    print('Something went wrong in: ' + str(ref) + ' on object ' + str(obj))
            #    print(e)

        # if flag:
        #     message = ACLMessage(ACLMessage.INFORM)
        #     message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        #     message.add_receiver(AID('agent_run_tool'))
        #     message.set_content({
        #         'project': project,
        #         'content': folder,
        #         'identifier': identifier,
        #         'message': 'updates on the database for ' + folder + "!"
        #     })
        #

        # json = JSONHandler(self.config['output_path'] + project + '/')
        # json.save_json(DAOs, project + '_' + folder.split('/')[0])

        # return DAOs

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

    def collect_users(self, owner: str, project: str, users: list):
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
        userapi = UsersAPI(owner, project, self.database)
        for user in users:
            userapi.collect_single(user)




