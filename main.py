import json

from api.api_collector import APICollector
from database_manager.io_mongo import IOMongo
from metrics.metrics_collector import MetricsCollector
from utils.json_handler import JSONHandler
import pymongo


class Main:

    def __init__(self):


        json_handler = JSONHandler('./')
        self.config = json_handler.open_json('config.json')
        self.projects = self.config['projects']

    def run(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = myclient[project_owner + '-' + project_name]

            collector = APICollector(database)

            collector.collect_issues(project_owner, project_name)
            collector.collect_pulls(project_owner, project_name)
            collector.collect_commits(project_owner, project_name)
            collector.collect_events(project_owner, project_name)
            collector.collect_comments(project_owner, project_name)

    # def run_io_mongo(self):
    #     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    #
    #     for project in self.projects:
    #         project_name = project['repo']
    #         project_owner = project['owner']
    #
    #         print(project)
    #
    #         database = myclient[project_owner + '-' + project_name]
    #
    #         io = IOMongo(database, project_name)
    #
    #         io.insert_issues()
    #         io.insert_pulls()
    #
    #         io.insert_events()
    #         io.insert_comments()
    #         io.insert_commits()
    #         io.insert_commits_from_pulls()


main = Main()
main.run()
#main.run_io_mongo()
