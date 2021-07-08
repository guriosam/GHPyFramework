import pymongo
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.behaviours.protocols import TimedBehaviour
from sys import argv

from api.api_collector import APICollector
from api.endpoint.issue import IssueAPI
from utils import json_handler as jh


class TemporalAPI(TimedBehaviour):

    def __init__(self, agent, type, time, myclient, project_name, project_owner, sender):
        super(TemporalAPI, self).__init__(agent, time)
        self.type = type
        self.database = myclient[project_owner + '-' + project_name][type]
        self.collector = APICollector(self.database)
        self.owner = project_owner
        self.name = project_name
        self.sender = sender

    def on_time(self):
        super(TemporalAPI, self).on_time()

        updated = False

        if 'issues' in self.type:
            updated = self.collector.collect_issues(self.owner, self.name)

        elif 'commits' in self.type:
            updated = self.collector.collect_commits(self.owner, self.name)

        elif 'comments' in self.type:
            updated = self.collector.collect_comments(self.owner, self.name)

        elif 'pull_requests' in self.type:
            updated = self.collector.collect_pulls(self.owner, self.name)

        if updated:
            message: ACLMessage = self.sender.message
            message.set_content(
                '{"owner": "' + self.owner + '", "project": "' + self.name + '", "type":"' + self.type + '"}')
            self.sender.send(message)
            updated = False

class AgentCheckAPI(Agent):
    def __init__(self, aid, myclient, name, owner, sender):
        super(AgentCheckAPI, self).__init__(aid=aid, debug=False)

        commit_temp = TemporalAPI(self, 'commits', 10.0, myclient, name, owner, sender)
        issue_temp = TemporalAPI(self, 'issues', 10.0, myclient, name, owner, sender)
        pull_temp = TemporalAPI(self, 'commit',10.0, myclient, name, owner, sender)
        comment_temp = TemporalAPI(self, 'comments', 10.0, myclient, name, owner, sender)

        self.behaviours.append(commit_temp)
        self.behaviours.append(issue_temp)
        self.behaviours.append(pull_temp)
        self.behaviours.append(comment_temp)
