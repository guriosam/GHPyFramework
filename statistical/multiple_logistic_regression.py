from pymongo.database import Database


#https://github.com/guriosam/revealing_social_aspects_of_design_decay/blob/master/multiple_regression_R.rar
#https://towardsdatascience.com/building-a-logistic-regression-in-python-step-by-step-becd4d56c9c8
class MultipleLogisticRegressionTest:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database

    def run(self):
        pass