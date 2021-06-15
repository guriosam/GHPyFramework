import pymongo
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.behaviours.protocols import TimedBehaviour
from sys import argv

from api.api_collector import APICollector
from api.endpoint.issue import IssueAPI
from utils import json_handler as jh


class TemporalAPI(TimedBehaviour):

    def __init__(self, agent, type, time, myclient, project_name, project_owner):
        super(TemporalAPI, self).__init__(agent, time)
        self.type = type
        self.database = myclient[project_owner + '-' + project_name][type]
        self.collector = APICollector(self.database)
        self.owner = project_owner
        self.name = project_name


    def on_time(self):
        super(TemporalAPI, self).on_time()

        if 'issues' in self.type:
            issues = self.database.find()
            if len(list(issues)) == 0:
                display_message(self.agent.aid.localname, 'No issues on the database.')
                return

            self.collector.collect_issues(self.owner, self.name)

        elif 'commits' in self.type:
            commits = self.database.find({})
            #if len(list(commits)) == 0:
            #    display_message(self.agent.aid.localname, 'No commits on the database.')
            #    return

            self.collector.collect_commits(self.owner, self.name)

        elif 'comments' in self.type:
            comments = self.database.find({})
            #if len(list(comments)) == 0:
            #    display_message(self.agent.aid.localname, 'No comments on the database.')
            #    return
            #self.collector.collect_comments(self.owner, self.name)
        elif 'pull_requests' in self.type:
            pull_requests = self.database.find({})

            if len(list(pull_requests)) == 0:
                display_message(self.agent.aid.localname, 'No pull_requests on the database.')
                return

            self.collector.collect_pulls(self.owner, self.name)


class AgentCheckAPI(Agent):
    def __init__(self, aid, myclient, name, owner):
        super(AgentCheckAPI, self).__init__(aid=aid, debug=False)

        commit_temp = TemporalAPI(self, 'commits', 10.0, myclient, name, owner)
        issue_temp = TemporalAPI(self, 'issues', 10.0, myclient, name, owner)
        #pull_temp = TemporalAPI(self, 'commit',10.0)
        #comment_temp = TemporalAPI(self, 'comments', 10.0, myclient, name, owner)
        self.behaviours.append(commit_temp)
        self.behaviours.append(issue_temp)
        #self.behaviours.append(pull_temp)
        #self.behaviours.append(comment_temp)


