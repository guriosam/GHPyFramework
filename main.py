from api.api_collector import APICollector
from metrics.metrics_collector import MetricsCollector
from utils.json_handler import JSONHandler


class Main:

    def __init__(self):
        self.config = JSONHandler('').open_json('config.json')
        self.projects = self.config['projects']

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            collector = APICollector()

            collector.collect_issues(project_owner, project_name)
            collector.collect_pulls(project_owner, project_name)
            collector.collect_commits(project_owner, project_name)
            collector.collect_events(project_owner, project_name)
            collector.collect_comments(project_owner, project_name)

            metrics_collector = MetricsCollector(self.config['output_path'])
            metrics_collector.run_metrics()


main = Main()
