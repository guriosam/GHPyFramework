from pymongo import MongoClient


class BlauIndex:

    def __init__(self, projects):
        self.projects = projects
        self.mongo_connection = MongoClient("mongodb://localhost:27017/")

    def calc_blau_index(self):

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            database = self.mongo_connection[project_owner + '-' + project_name]

            metrics = list(database['metrics'].find({}))

            has_gender = {'gender': list(), 'count': list()}
            for metric in metrics:

                if 'number_males' in metric.keys():
                    has_gender['gender'].append('male')
                    has_gender['count'].append(metric['number_males'])
                    has_gender['gender'].append('female')
                    has_gender['count'].append(metric['number_females'])
                    # pd.concat([has_gender, {'gender': 'male', 'count': metric['number_males']}], ignore_index=True)
                    # has_gender.append({'gender': 'female', 'count': metric['number_females']}, ignore_index=True)

            gender = pd.DataFrame(has_gender)
            gender = gender.groupby('gender')['count'].apply(self.blaus_index).reset_index(name='Gender Diversity')

            print(project_name)
            print(gender)


    def blaus_index(self, arr):
        return 1 - sum((arr.value_counts() / len(arr)) ** 2)