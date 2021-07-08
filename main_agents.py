import pymongo
from pade.acl.aid import AID
from pade.misc.utility import start_loop

from agents.git_agent import Receiver as GitReceiver
from agents.receiver_agent import Receiver
from agents.sender_agent import Sender
from utils import json_handler as jh

from agents.update_database_from_api import AgentCheckAPI

if __name__ == '__main__':
    c = 0
    agents = list()

    port = int(2010)
    receiver_data = 'agent_receiver_{}@localhost:{}'.format(port + 2, port + 2)
    receiver_agent = Receiver(AID(name=receiver_data))
    agents.append(receiver_agent)

    sender_data = 'agent_sender_{}@localhost:{}'.format(port, port)
    sender_agent = Sender(AID(name=sender_data), receiver_data)
    agents.append(sender_agent)

    json_handler = jh.JSONHandler('./')
    config_api = json_handler.open_json('config.json')
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")

    projects = config_api['projects']
    for project in projects:
        project_name = project['repo']
        project_owner = project['owner']

        port = int(2000) + c
        agent_name = 'agent_check_api_{}@localhost:{}'.format(port, port)
        agent_api = AgentCheckAPI(AID(name=agent_name), myclient, project_name, project_owner, sender_agent)
        agents.append(agent_api)

        git_data = 'agent_git_{}@localhost:{}'.format(port + 30, port + 30)
        git_agent = GitReceiver(AID(name=git_data), project_owner, project_name)
        agents.append(git_agent)

        sender_git_data = 'agent_sender_git_{}@localhost:{}'.format(port + 50, port + 50)
        sender_git_agent = Sender(AID(name=sender_git_data), sender_git_data)
        agents.append(sender_git_agent)

        c += 1000

    start_loop(agents)
