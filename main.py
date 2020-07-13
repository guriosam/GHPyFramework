from utils.json_handler import JSONHandler


class Main:

    def __init__(self):
        self.config = JSONHandler('').open_json('config.json')
        self.projects = self.config['projects']

        for project in self.projects:
            self.project_name = project['repo']
            print(self.project_name)

            # self.collect_issues(project)
            # self.collect_pulls(project)
            # self.collect_commits(project)
            # self.collect_users(UserAPI(project['owner'], project['repo']), UserDAO())
            # self.collect_reviews(project)
            # self.collect_events(project)

            # self.collect_commits_on_pulls(project['owner'], project['repo'])
            # self.compose_commits_on_pulls(project['owner'], project['repo'])

            # self.collect_pulls_of_issues(project)

            # self.run_metrics(project)
            # self.compile_data(project)


main = Main()
