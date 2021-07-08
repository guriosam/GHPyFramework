import json

import pymongo
from pade.acl.messages import ACLMessage
from pade.core.agent import Agent
from pydriller import Repository


class Receiver(Agent):

    def __init__(self, aid, project_owner, project_name):
        print("[GitAgent] initializing git agent")
        super(Receiver, self).__init__(aid=aid, debug=False)
        self.project_url = 'https://github.com/' + project_owner + '/' + project_name
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.database = myclient[project_owner + '-' + project_name]

    def on_start(self):
        print("[GitAgent] started. Trying to cloning temporary repository...")
        self.repository = Repository(self.project_url)

    def react(self, message: ACLMessage):
        json_message = json.loads(message.content)
        if 'goal' in json_message.keys():
            goal = json_message['goal']
            if 'fix_peril_merged_prs' in goal:
                self.fix_peril_merged_prs()

    def fix_peril_merged_prs(self):
        commits = self.repository.traverse_commits()

        for commit in commits:
            if self.database['commits'].find({'sha': commit.hash, 'from_pull': False}):
                self.database['commits'].update_one({'sha': commit.hash, 'merged': True})
            if self.database['commits'].find({'sha': commit.hash, 'merged': False}):
                self.database['commits'].update_one({'sha': commit.hash, 'merged': True})
