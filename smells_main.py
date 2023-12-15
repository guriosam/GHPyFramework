from pymongo import MongoClient

from smells.smells_reader import SmellsReader
from smells.summarize_organic import OrganicSummarize
from utils.json_handler import JSONHandler


class SmellsMain:

    def __init__(self):
        json_handler = JSONHandler('./')
        self.config = json_handler.open_json('config_dev.json')
        self.projects = self.config['projects']
        self.mongo_connection = MongoClient("mongodb://localhost:27017/")

    def run(self):

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            print('Project: ' + project_name)

            database = self.mongo_connection[project_owner + '-' + project_name]

            #project_path = './data/git_repositories/' + project_name + '/'
            #summarizer = OrganicSummarize()
            #summarizer.run(project_path + project_name + '.txt', './data/smells_organic/' + project_name + '.zip',
            #               './data/smells_summary/')

            smells_reader = SmellsReader('./data/smells_summary/', project_name, database)

            smells_reader.read_parsed_json()

