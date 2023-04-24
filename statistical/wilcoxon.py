from pymongo.database import Database
import pandas as pd
from scipy.stats import ranksums


# Wilcoxon Rank-Sum Test
class WilcoxonRankSumTest:

    def __init__(self, database: Database = None):
        self.database = database

    @staticmethod
    def wilcoxon_test(input_data, metric):
        degraded_dist = input_data[input_data["design_change"] is True][metric]
        clean_dist = input_data[input_data["design_change"] is False][metric]

        p_value = None

        if degraded_dist.size > 0 and clean_dist.size > 0:
            test_stat, p_value = ranksums(degraded_dist, clean_dist)

        if not p_value:
            p_value = float('nan')

        metric_data = pd.DataFrame({"metric": [metric], "pvalue": [p_value]})

        return metric_data

    def _collect_metrics(self):
        metrics = pd.DataFrame()

        database_metrics = self.database['metrics']

        all_metrics = database_metrics.find({})

        print(list(all_metrics))

        for metric in all_metrics:
            print(metric)
            metrics.append([])

        return metrics

    def run(self):

        metrics = self._collect_metrics()

        return

        cols = metrics.columns

        results = pd.DataFrame(columns=["metric", "p_value"])

        for metric in cols:
            metric_data = self.wilcoxon_test(metrics, metric)
            results_density = pd.concat([results, metric_data])

        results["significant"] = results["p_value"] <= 0.05

        #TODO save results on database
