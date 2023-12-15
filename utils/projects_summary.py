
class ProjectsSummary:

    def __init__(self, projects):
        self.mongo_connection = None
        self.projects = projects

    def projects_info(self):
        total_prs = 0

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            prs_merged = database['pull_requests'].find({'merged': True})
            commits = database['commits'].find({})
            commits_date = list(database['commits'].aggregate([
                {
                    '$group': {
                        '_id': '$sha',
                        'date': {
                            '$push': {
                                'date': '$commit.author.date'
                            }
                        }
                    }
                }, {
                    '$sort': {
                        'date': 1
                    }
                }
            ]))

            # print(project_name)
            # print('PRS Merged: ' + str(len(list(prs_merged))))
            # total_prs += len(list(prs_merged))
            # print('Commits: ' + str(len(list(commits))))
            # print('Timespan: ' + str(commits_date[0]['date'][0]['date'].split('-')[0]) + ' - ' +
            #      str(commits_date[-1]['date'][0]['date'].split('-')[0]))

