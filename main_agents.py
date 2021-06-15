import pymongo
from pade.acl.aid import AID
from pade.misc.utility import start_loop
from utils import json_handler as jh

from agents.update_database_from_api import AgentCheckAPI

if __name__ == '__main__':
    agents_per_process = 2
    c = 0
    agents = list()
    json_handler = jh.JSONHandler('./')
    config_api = json_handler.open_json('config.json')
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")

    projects = config_api['projects']

    for project in projects:
        project_name = project['repo']
        project_owner = project['owner']

        port = int(2000) + c
        agent_name = 'agent_check_api_{}@localhost:{}'.format(port, port)
        agent_api = AgentCheckAPI(AID(name=agent_name), myclient, project_name, project_owner)
        agents.append(agent_api)
        c += 1000

    start_loop(agents)
