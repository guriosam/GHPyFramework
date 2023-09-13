import numpy as np
from pymongo.database import Database
import matplotlib.pyplot as plot
import pandas as pd
from scipy.stats import ranksums


# Wilcoxon Rank-Sum Test
class WilcoxonRankSumTest:

    def __init__(self, database: Database = None):
        self.database = database
        self.class_density = pd.DataFrame()
        self.class_diversity = pd.DataFrame()
        self.method_density = pd.DataFrame()
        self.method_diversity = pd.DataFrame()

    @staticmethod
    def wilcoxon_test(input_data, metric):

        degraded_dist = input_data[input_data["design_change"] == True][metric]
        clean_dist = input_data[input_data["design_change"] == False][metric]

        p_value = None

        if degraded_dist.size > 0 and clean_dist.size > 0:
            test_stat, p_value = ranksums(degraded_dist, clean_dist)

        if not p_value:
            p_value = float('nan')

        metric_data = pd.DataFrame({"metric": [metric], "p_value": [p_value]})

        return metric_data

    def _collect_metrics(self):

        database_metrics = self.database['metrics']

        metrics = pd.DataFrame(list(database_metrics.find()))

        self.class_density = self._fill_na_and_drop_columns(metrics, 'class_design_change_density',
                                                            'class_design_change_diversity',
                                                            'method_design_change_density',
                                                            'method_design_change_diversity')

        self.class_diversity = self._fill_na_and_drop_columns(metrics, 'class_design_change_diversity',
                                                              'method_design_change_density',
                                                              'class_design_change_density',
                                                              'method_design_change_diversity')

        self.method_density = self._fill_na_and_drop_columns(metrics, 'method_design_change_density',
                                                             'class_design_change_diversity',
                                                             'class_design_change_density',
                                                             'method_design_change_diversity')

        self.method_diversity = self._fill_na_and_drop_columns(metrics, 'method_design_change_diversity',
                                                               'class_design_change_diversity',
                                                               'class_design_change_density',
                                                               'method_design_change_density')

    def run_wilcoxon(self, metrics, smell_type):
        results = pd.DataFrame(columns=["metric", "p_value"])

        cols = metrics.columns

        cols = cols.drop('design_change')

        for metric in cols:
            metric_data = self.wilcoxon_test(metrics, metric)
            results = pd.concat([results, metric_data])

        results["significant"] = results["p_value"] <= 0.05

        results_database = self.database['results_wilcoxon']

        results = results.round(3)

        results_json = results_database.find_one({'smell_type': smell_type})

        if not results_json:
            results_json = {'smell_type': smell_type}
            results_database.insert_one(results_json)

        for index, row in results.iterrows():
            results_json[row['metric']] = {
                'p_value': row['p_value'],
                'significant': row['significant']
            }

        results_database.update_one({'smell_type': smell_type}, {'$set': results_json})

    def run(self):
        self._collect_metrics()

        self.run_wilcoxon(self.class_density, 'class_density')
        self.run_wilcoxon(self.class_diversity, 'class_diversity')
        self.run_wilcoxon(self.method_density, 'method_density')
        self.run_wilcoxon(self.method_diversity, 'method_diversity')

    @staticmethod
    def _fill_na_and_drop_columns(metrics, rename_col, col1, col2, col3):
        metrics = metrics.fillna(0).drop(columns=['_id', 'issue_number',
                                                  'class_degradation_density',
                                                  'class_degradation_diversity',
                                                  'method_degradation_density',
                                                  'method_degradation_diversity',
                                                  'class_diff', 'method_diff', 'num_class_lvl',
                                                  'num_method_lvl',
                                                  'diff_method_lvl', 'diff_class_lvl',
                                                  col1,
                                                  col2,
                                                  col3])

        metrics.rename(columns={rename_col: 'design_change'}, inplace=True)

        return metrics
