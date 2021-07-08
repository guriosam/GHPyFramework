import json

import pymongo
from github import Github
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from metrics.number_of_modified_files import NumberModifiedFiles


class Receiver(Agent):

    def __init__(self, aid):
        print("[RECEIVER] initializing receiver agent")
        super(Receiver, self).__init__(aid=aid, debug=False)

    def on_start(self):
        print("[RECEIVER] started receiver. no work need to be done.")

    def react(self, message: ACLMessage):
        print("[RECEIVER] react receiver")

        json_message = json.loads(message.content)

        g = Github("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")

        project_name = json_message['project']
        project_owner = json_message['owner']
        type = json_message['type']

        repo = g.get_repo(project_owner + '/' + project_name)

        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        database = myclient[project_owner + '-' + project_name]

        if 'commit' in type:
            print('Updating commit metrics for project: ' + project_name)

            modified_files = NumberModifiedFiles(database)
            shas = modified_files.get_modified_files_on_commits()

            for sha in shas:
                commit = database['commits'].find_one({'sha': sha})
                author = commit['commit']['author']['name']
                committer = commit['commit']['committer']['name']
                if 'GitHub' in committer:
                    committer = author


                commits_as_author = database['commits'].find({'commit.author.name': author}).count()
                commits_as_committer = database['commits'].find({'commit.committer.name': author}).count()
                database['commits'].aggregate([{'$group': {'_id':None, 'files': {'$avg': '$number_of_java_files'} }}])

                response = database['commits'].aggregate([{'$group':
                                                               {'_id': None, 'number_files':
                                                                   {'$avg': '$number_of_java_files'},
                                                                'avg_additions': {'$avg': '$stats.additions'},
                                                                'avg_deletions': {'$avg': '$stats.deletions'},
                                                                'len_message': {'$avg':
                                                                                    {'$strLenCP': '$commit.message'}}
                                                                }}])

                report = {
                    'Commit author': author,
                    'Commit committer': committer,
                    'Previous commits as author': commits_as_author,
                    'Previous commits as committer': commits_as_committer,
                    'Number of files in this commit': len(commit['files']),
                    'Number of additions in this commit': commit['stats']['additions'],
                    'Number of deletions in this commit': commit['stats']['deletions'],
                    'Length of commit message in this commit': len(commit['commit']['message'])
                }

                for resp in response:
                    if 'number_of_java_files' in resp.keys():
                        report['Average of files in previous commits'] = resp['number_of_java_files']
                    report['Average of additions in previous commits'] = resp['avg_additions']
                    report['Average of deletions in previous commits'] = resp['avg_deletions']
                    report['Average of commit message length in previous commits'] = resp['len_message']


                commit = repo.get_commit(sha=sha)
                message = ''
                for key in report.keys():
                    message += key + ': ' + str(report[key]) + '\n'
                commit.create_comment(message)

                #print(message)

        # display_message(self.aid.localname, '[RECEIVER] message received: ' + message.content)
