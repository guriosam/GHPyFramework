import json

from pymongo.database import Database

from utils.json_handler import JSONHandler


class SmellsReader:

    def __init__(self, smells_path: str, project_name: str, database: Database = None):
        self.path = smells_path
        self.project_name = project_name
        self.database = database

    def read_parsed_json(self):
        handler = JSONHandler(self.path)

        project_smells = handler.open_json(self.project_name + ".json")

        self._save_json_in_database(project_smells)

        self._save_smells_on_metrics()

    def _save_json_in_database(self, smells_json):

        if not smells_json:
            return

        database_smells = self.database['commits_smells']
        database_commits = self.database['commits']

        commits = database_commits.find({})

        for commit in commits:
            if not commit['sha'] in smells_json.keys():
                continue

            commit_smells = smells_json[commit['sha']]

            c_dc_density, m_dc_density, c_deg_density, m_deg_density = \
                self._check_density(commit_smells, 'diff_class_lvl', 'diff_method_lvl')

            c_dc_diversity, m_dc_diversity, c_deg_diversity, m_deg_diversity = \
                self._check_diversity(commit_smells, 'class_diff', 'method_diff')

            if not database_smells.find_one({'sha': commit['sha']}):
                database_smells.insert_one({'sha': commit['sha']})

            database_smells.update_one({'sha': commit['sha']},
                                       {'$set': {
                                           'num_class_lvl': commit_smells['num_class_lvl'],
                                           'diff_class_lvl': commit_smells['diff_class_lvl'],
                                           'num_method_lvl': commit_smells['num_method_lvl'],
                                           'diff_method_lvl': commit_smells['diff_method_lvl'],
                                           'class_diff': commit_smells['class_diff'],
                                           'method_diff': commit_smells['method_diff'],
                                           'class_design_change_density': c_dc_density,
                                           'method_design_change_density': m_dc_density,
                                           'class_degradation_density': c_deg_density,
                                           'method_degradation_density': m_deg_density,
                                           'class_design_change_diversity': c_dc_diversity,
                                           'method_design_change_diversity': m_dc_diversity,
                                           'class_degradation_diversity': c_deg_diversity,
                                           'method_degradation_diversity': m_deg_diversity
                                       }})

    @staticmethod
    def _check_density(commit_smells, class_level, method_level):
        design_change_class_level = False
        design_change_method_level = False
        degradation_class_level = False
        degradation_method_level = False

        if commit_smells[class_level] != 0:
            design_change_class_level = True

        if commit_smells[method_level] != 0:
            design_change_method_level = True

        if commit_smells[class_level] >= 0:
            degradation_class_level = True

        if commit_smells[method_level] >= 0:
            degradation_method_level = True

        return design_change_class_level, design_change_method_level, degradation_class_level, degradation_method_level

    @staticmethod
    def _check_diversity(commit_smells, class_diff, method_diff):
        design_change_class_level = False
        design_change_method_level = False
        degradation_class_level = False
        degradation_method_level = False

        total_class = 0
        for class_smells in commit_smells[class_diff].keys():
            total_class += commit_smells[class_diff][class_smells]

        total_method = 0
        for method_smells in commit_smells[method_diff].keys():
            total_method += commit_smells[method_diff][method_smells]

        if total_class != 0:
            design_change_class_level = True

        if total_method != 0:
            design_change_method_level = True

        if total_class >= 0:
            degradation_class_level = True

        if total_method >= 0:
            degradation_method_level = True

        return design_change_class_level, design_change_method_level, degradation_class_level, degradation_method_level

    def _save_smells_on_metrics(self):
        database_metrics = self.database['metrics']
        database_pulls = self.database['pull_requests']
        database_smells = self.database['commits_smells']

        smells = database_smells.find({})

        for smell in smells:
            sha = smell['sha']

            pulls = database_pulls.find({'merge_commit_sha': sha})

            for pull in pulls:
                issue_number = pull['number']

                if database_metrics.find_one({'issue_number': issue_number}):
                    database_metrics.insert_one({'issue_number': issue_number})

                database_metrics.update_one({'issue_number': issue_number},
                                       {'$set': {'num_class_lvl': smell['num_class_lvl'],
                                           'diff_class_lvl': smell['diff_class_lvl'],
                                           'num_method_lvl': smell['num_method_lvl'],
                                           'diff_method_lvl': smell['diff_method_lvl'],
                                           'class_diff': smell['class_diff'],
                                           'method_diff': smell['method_diff'],
                                           'class_design_change_density': smell['class_design_change_density'],
                                           'method_design_change_density': smell['method_design_change_density'],
                                           'class_degradation_density': smell['class_degradation_density'],
                                           'method_degradation_density': smell['method_degradation_density'],
                                           'class_design_change_diversity': smell['class_design_change_diversity'],
                                           'method_design_change_diversity': smell['method_design_change_diversity'],
                                           'class_degradation_diversity': smell['class_degradation_diversity'],
                                           'method_degradation_diversity': smell['method_degradation_diversity']}})




