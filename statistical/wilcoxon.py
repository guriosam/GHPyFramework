from pymongo.database import Database
import pandas as pd
from scipy.stats import ranksums, stats


# Wilcoxon Rank-Sum Test
# TODO
# https://github.com/guriosam/revealing_social_aspects_of_design_decay/blob/master/wilcoxon_analysis.R
# https://stats.stackexchange.com/questions/235243/when-should-i-use-scipy-stats-wilcoxon-instead-of-scipy-stats-ranksums
class WilcoxonTest:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database

    @staticmethod
    def _distribute_samples(input_data, metric):
        return [], []

    @staticmethod
    def _run_wilcoxon(refactored, not_refactored):

        statistic, p = ranksums(x = refactored, y = not_refactored)
        statistic2, p2 = ranksums(x = refactored, y = not_refactored, alternative='greater')
        statistic3, p3 = ranksums(x = refactored, y = not_refactored, alternative='less')


        return []

    def _collect_metrics(self):
        metrics = pd.DataFrame()

        database = self.database['metrics']


        return metrics

    def run(self):

        metrics = self._collect_metrics()

        cols = metrics.columns

        for column_name in cols:
            refactored, not_refactored = self._distribute_samples(metrics, column_name)
            metric_data = self._run_wilcoxon(refactored, not_refactored)




