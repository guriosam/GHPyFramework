import pandas as pd
from pymongo import MongoClient

from statistical.multiple_logistic_regression import MultipleLogisticRegressionTest
from statistical.wilcoxon import WilcoxonRankSumTest
from utils.json_handler import JSONHandler


class MainStatistical:

    def __init__(self):
        json_handler = JSONHandler('../')
        self.config = json_handler.open_json('config_dev.json')
        self.projects = self.config['projects']
        self.mongo_connection = MongoClient("mongodb://localhost:27017/")

    def run_wilcoxon(self):
        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            print(project_name)

            database = self.mongo_connection[project_owner + '-' + project_name]

            wilcoxon = WilcoxonRankSumTest(database)
            wilcoxon.run()

    def compile_results_rq1(self):
        smells_types = ['class_density', 'method_density']

        for smell_type in smells_types:
            print(smell_type)
            results = []
            for project in self.projects:
                project_name = project['repo']
                project_owner = project['owner']

                # print(project_name)
                database = self.mongo_connection[project_owner + '-' + project_name]

                database_results = database['results_wilcoxon']

                result = database_results.find_one({'smell_type': smell_type})

                result = self._swap_dict_keys(result)

                for key in result.keys():
                    if '_id' in key:
                        continue

                    if 'smell' in key:
                        continue

                    metric = result[key]
                    if metric['significant']:
                        metric['p_value'] = '\cellcolor[HTML]{C0C0C0} ' + str(metric['p_value'])

                    result[key] = metric

                result = pd.DataFrame(result)
                result = result.drop(columns=['_id', 'smell_type'])
                result = result.transpose()
                result = result.drop(columns=['significant'])
                result.rename(columns={'p_value': project_name}, inplace=True)

                result = result.transpose()
                results.append(result)

            df = pd.concat(results)

            print(df.transpose().to_latex(escape=False))

    def compile_results_rq2(self):
        smells_types = ['class_density', 'method_density']

        for smell_type in smells_types:
            results = []
            for project in self.projects:
                project_name = project['repo']
                project_owner = project['owner']

                # print(project_name)
                database = self.mongo_connection[project_owner + '-' + project_name]

                database_results = database['results_regression']

                result = database_results.find_one({'smell_type': smell_type})

                result = self._swap_dict_keys(result)

                for key in result.keys():
                    if '_id' in key:
                        continue

                    if 'smell' in key:
                        continue

                    metric = result[key]
                    if '✓' in metric['significant']:
                        arrow = "$\downarrow$"
                        if float(metric['odds_ratio']) > 1:
                            arrow = "$\\uparrow$"

                        metric['odds_ratio'] = '\cellcolor[HTML]{C0C0C0} ' + str(metric['odds_ratio']) + ' ' + arrow

                    result[key] = metric

                try:
                    result = pd.DataFrame(result)
                    result = result.drop(columns=['_id', 'smell_type'])
                    result = result.transpose()
                    result = result.drop(columns=['significant'])
                    result.rename(columns={'odds_ratio': project_name}, inplace=True)

                    result = result.transpose()
                    results.append(result)
                except:
                    pass

            df = pd.concat(results)

            print(df.to_latex(escape=False).replace('NaN', ' '))

    def run_regression(self, drop):

        mlr = MultipleLogisticRegressionTest(None, None, None)

        owners = set()

        for project in self.projects:
            project_name = project['repo']
            project_owner = project['owner']

            owners.add(project_owner)

            print(project_name)

            database = self.mongo_connection[project_owner + '-' + project_name]

            mlr.database = database
            mlr.owner = project_owner
            mlr.repo = project_name

            database['results_regression'].drop()

            mlr.run(drop)

        if not drop:
            database = self.mongo_connection['all_projects']
            mlr.database = database
            mlr.owner = 'all'
            mlr.repo = 'projects'
            mlr.run_rq3()

            for owner in owners:
                database = self.mongo_connection[owner]
                mlr.database = database
                mlr.owner = owner
                mlr.run_rq4()

    def compile_results_rq3(self):
        smells_types = ['class_density', 'method_density']

        for smell_type in smells_types:
            results = []

            # print(project_name)
            database = self.mongo_connection['all_projects']

            database_results = database['results_regression']

            result = database_results.find_one({'smell_type': smell_type})

            result = self._swap_dict_keys(result)

            for key in result.keys():
                if '_id' in key:
                    continue

                if 'smell' in key:
                    continue

                metric = result[key]
                if '✓' in metric['significant']:
                    arrow = "$\downarrow$"
                    if float(metric['odds_ratio']) > 1:
                        arrow = "$\\uparrow$"

                    metric['odds_ratio'] = '\cellcolor[HTML]{C0C0C0} ' + str(metric['odds_ratio']) + ' ' + arrow

                result[key] = metric

            try:
                result = pd.DataFrame(result)
                result = result.drop(columns=['_id', 'smell_type'])
                result = result.transpose()
                result = result.drop(columns=['significant'])
                result.rename(columns={'odds_ratio': 'all'}, inplace=True)

                # result = result.transpose()
                results.append(result)
            except:
                pass

            df = pd.concat(results)

            print(df.to_latex(escape=False).replace('NaN', ' '))

    def compile_results_rq4(self):
        smells_types = ['class_density', 'method_density']

        owners = set()
        for project in self.projects:
            project_owner = project['owner']
            owners.add(project_owner)

        for smell_type in smells_types:
            results = []
            for owner in owners:
                print(owner)
                database = self.mongo_connection[owner]

                database_results = database['results_regression']

                result = database_results.find_one({'smell_type': smell_type})

                result = self._swap_dict_keys(result)

                for key in result.keys():
                    if '_id' in key:
                        continue

                    if 'smell' in key:
                        continue

                    metric = result[key]
                    if '✓' in metric['significant']:
                        arrow = "$\downarrow$"
                        if float(metric['odds_ratio']) > 1:
                            arrow = "$\\uparrow$"

                        metric['odds_ratio'] = '\cellcolor[HTML]{C0C0C0} ' + str(metric['odds_ratio']) + ' ' + arrow

                    result[key] = metric

                try:
                    result = pd.DataFrame(result)
                    result = result.drop(columns=['_id', 'smell_type'])
                    result = result.transpose()
                    result = result.drop(columns=['significant'])
                    result.rename(columns={'odds_ratio': owner}, inplace=True)
                    print(result.to_latex(escape=False).replace('NaN', ' '))
                    # result = result.transpose()
                    # results.append(result)
                except:
                    pass

                # df = pd.concat(results)

                # print(df.to_latex(escape=False).replace('NaN', ' '))

    @staticmethod
    def _swap_dict_keys(result):
        names_key = {'core_developers': '\\# Core Devs',
                     'contributors': '\\# Contributors',
                     'discussion_duration': 'Discussion Duration',
                     'discussion_size': 'Discussion Size',
                     'last_and_close': 'TBLC',
                     'mean_number_of_words': 'MNWD',
                     'newbies': '\\# Newbies',
                     'newcomers_size': '\\# New Devs',
                     'number_of_words': '\\# Words',
                     'open_and_first': 'TBOF',
                     'team_size': 'Team Size',
                     'users_left_size': '\\# Devs Left',
                     'density_design_keywords': 'DDK',
                     'density_refactoring_keywords': 'DRK',
                     'number_design_keywords': '\\# Design Keywords',
                     'number_refactoring_keywords': '\\# Refact Keywords',
                     'mean_time_between_comments': 'MTBC',
                     'number_females': '\\# Females',
                     'number_males': '\\# Males'
                     }

        for row in list(result.keys()):
            for k, v in names_key.items():
                if k == row:
                    result[v] = result.pop(row)

        if 'number_of_comments' in result.keys():
            result.pop('number_of_comments')

        return result

    def run(self):
        #self.run_wilcoxon()
        #self.compile_results_rq1()
        #self.run_regression(drop=True)
        #self.compile_results_rq2()
        self.run_regression(drop=False)
        #self.compile_results_rq3()
        #self.compile_results_rq4()

MainStatistical().run()