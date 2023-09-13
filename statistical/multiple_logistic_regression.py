from numpy import nan
from pymongo.database import Database
from scipy.stats import skew
from sklearn import metrics
import subprocess
import numpy as np
import matplotlib.pyplot as plot
from sklearn.svm import SVC
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.generalized_linear_model import GLMResults
from statsmodels.iolib import SimpleTable
from statsmodels.stats import multitest
from statsmodels.stats.outliers_influence import variance_inflation_factor


class MultipleLogisticRegressionTest:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database
        self.class_density = pd.DataFrame()
        self.method_density = pd.DataFrame()

        self.class_density_all = pd.DataFrame()
        self.method_density_all = pd.DataFrame()

        self.class_density_community = {}
        self.method_density_community = {}


    def run(self, drop):
        self.collect_metrics()

        if drop:
            self._gen_mixed_models('class_density', self.class_density, drop)
            self._gen_mixed_models('method_density', self.method_density, drop)
        else:
            self.join_dataframes()

    def run_rq3(self):
        self._gen_mixed_models('class_density', self.class_density_all, None)
        self._gen_mixed_models('method_density', self.method_density_all, None)

    def run_rq4(self):
        self._gen_mixed_models('class_density', self.class_density_community[self.owner], None)
        self._gen_mixed_models('method_density', self.method_density_community[self.owner], None)

    def _glm_feats(self, smell_type, input_data):
        # Subset by the measures
        # input_data = input_data.drop(columns=[''])

        # Get numeric and non-numeric feats
        num_input_data = input_data.select_dtypes(include=np.number)
        non_num_input_data = input_data.select_dtypes(exclude=np.number)

        num_input_data = num_input_data.dropna(axis=0)
        num_input_data = num_input_data.loc[:, num_input_data.isna().sum() == 0]

        # Remove highly correlated predictors (VIF >= 10 or cor >= 0.7)
        vif = [variance_inflation_factor(num_input_data.values, i) for i in range(num_input_data.shape[1])]
        highly_cor = np.array([i for i, v in enumerate(vif) if v >= 10])
        cor_matrix = num_input_data.corr()
        cor_highly_cor = np.array(np.where(np.abs(cor_matrix.iloc[highly_cor, highly_cor]) >= 0.7)).flatten()
        highly_cor = np.unique(np.concatenate((highly_cor, cor_highly_cor)))
        num_input_data = num_input_data.iloc[:, np.setdiff1d(np.arange(num_input_data.shape[1]), highly_cor)]

        # Merge numeric and non-numeric feats
        input_data = pd.concat([non_num_input_data, num_input_data], axis=1)

        # Transform the features to their absolute values
        indexes = input_data.select_dtypes(include=np.number).columns
        input_data.loc[:, indexes] = input_data.loc[:, indexes].abs()


        # Log2 or cube transform the features
        for var_name in input_data.columns:
            if var_name in indexes:
                skewness_n = skew(input_data[var_name])
                if skewness_n > 0:
                    input_data[var_name] = np.log2(input_data[var_name] + 0.00001)
                elif skewness_n < 0:
                    input_data[var_name] = input_data[var_name] ** 3


        # Scale the data to 0 mean and 1 std
        indexes = input_data.select_dtypes(include=np.number).columns
        input_data.loc[:, indexes] = (input_data.loc[:, indexes] - input_data.loc[:, indexes].mean()) / input_data.loc[
                                                                                                        :,
                                                                                                        indexes].std()

        input_data.columns = input_data.columns.str.strip()

        # Create the glm formula and model
        dec_pred = input_data.columns[0]
        preds = input_data.columns[1:]

        glm_formula = f"{dec_pred} ~ {' + '.join(preds)}"

        glm_model = smf.glm(formula=glm_formula, data=input_data, family=sm.families.Binomial())

        results: GLMResults = glm_model.fit()

        # print(results.summary())

        # Model statistics and metrics

        # Calcular a deviance residual
        residual_deviance = results.null_deviance - results.deviance

        # # Calcular o D-squared
        dsquared = residual_deviance / results.null_deviance

        # # Imprimir o resultado
        # print(f"Deviance Explained (D-squared): {dsquared}\n")

        # Transforming results summary to DF
        output = results.summary().tables[1]
        output = pd.DataFrame(output.data)

        # Renaming columns to first row
        output.rename(columns=output.iloc[0], inplace=True)

        # Drop row of column names
        output.drop(output.index[0], inplace=True)

        # Drop Intercept
        output.drop(output.index[0], inplace=True)

        # Drop columns to used
        output.drop(columns=['std err', 'z', '[0.025', '0.975]'], inplace=True)

        # Renaming column to p value
        output.rename(columns={'P>|z|': 'p_value'}, inplace=True)
        output.rename(columns={'coef': 'odds_ratio'}, inplace=True)

        # p_values = multitest.multipletests(output['p_value'].apply(lambda x: float(x)), alpha=0.05,
        # method='bonferroni', is_sorted=False, returnsorted=False)

        output['significant'] = np.where(output['p_value'].apply(lambda x: float(x)) <= 0.001, '\u2713', '\u2717')

        output.drop(columns=['p_value'], inplace=True)

        output = self._swap_df_keys(output.transpose())

        output['odds_ratio'] = output['odds_ratio'].apply(lambda x: np.exp(float(x)))

        output = output.round(3)

        output = output.transpose().to_dict()

        database_results = self.database['results_regression']

        if not database_results.find_one({'smell_type': smell_type}):
            database_results.insert_one({'smell_type': smell_type})

        database_results.update_one({'smell_type': smell_type}, {'$set': output})

    def _bind_all_data(self, path):
        # Lista dos projetos GitHub
        # DataFrame de saída e flag
        projects = []
        output_data = pd.DataFrame()
        flag = True
        for project in projects:
            # Ler os dados de entrada
            input_path = f"{path}{project}.csv"
            input_data = pd.read_csv(input_path)
            # Juntar os dados se não for o primeiro projeto
            if flag:
                output_data = input_data
                flag = False
            else:
                output_data = pd.concat([output_data, input_data])
        # Retornar os dados juntados
        return output_data

    def _gen_mixed_models(self, smell_type, input_data, drop = None):

        # input_data = self._bind_all_data(path)
        if drop:
            input_data = self._drop_columns(input_data)

        input_data = input_data.mask(input_data == 0)
        pd.set_option('display.max_columns', None)
        print(input_data.describe())
        #metrics['discussion_duration'] = metrics['discussion_duration'] / metrics['discussion_duration'].max()
        #metrics['team_size'] = metrics['team_size'] / metrics['team_size'].max()
        #metrics['mean_time_between_comments'] = metrics['mean_time_between_comments'] / metrics['mean_time_between_comments'].max()
        #metrics['open_and_first'] = metrics['open_and_first'] / metrics['open_and_first'].max()

        p = input_data.boxplot(column=['open_and_first'])#, 'team_size', 'mean_time_between_comments',
                            #'open_and_first'])
        p.plot()
        plot.show()
        #exit()
        return

        # Converte o valor da coluna "degradation" para um valor numérico
        # (1 para "True" e 0 para "False") e transforma em uma variável categórica
        input_data.insert(0, 'degradation', input_data.pop('degradation'))
        input_data['degradation'] = input_data['degradation'] == True
        # input_data["degradation"] = pd.factorize(input_data["degradation"])[0]

        # Transforma as colunas true/false em variáveis categóricas
        input_data = self._transform_categorical(input_data)

        # Exibe informações sobre as variáveis do conjunto de dados
        # input_data.info()

        # Executa um modelo GLM
        self._glm_feats(smell_type, input_data)

    @staticmethod
    def _deviance(X, y, model):
        return 2 * metrics.log_loss(y, model.predict_proba(X), normalize=False)

    def collect_metrics(self):

        database_metrics = self.database['metrics']

        metrics_df = pd.DataFrame(list(database_metrics.find()))

        self.class_density = self._fill_na_and_drop_columns(metrics_df, 'class_degradation_density',
                                                            'class_degradation_diversity',
                                                            'method_degradation_density',
                                                            'method_degradation_diversity')

        self.method_density = self._fill_na_and_drop_columns(metrics_df, 'method_degradation_density',
                                                             'class_degradation_density',
                                                             'class_degradation_diversity',
                                                             'method_degradation_diversity')

    @staticmethod
    def _fill_na_and_drop_columns(metrics_df, rename_col, col1, col2, col3):
        metrics_df = metrics_df.fillna(0).drop(columns=['_id', 'issue_number',
                                                        'class_design_change_density',
                                                        'class_design_change_diversity',
                                                        'method_design_change_density',
                                                        'method_design_change_diversity',
                                                        'class_diff', 'method_diff', 'num_class_lvl',
                                                        'num_method_lvl',
                                                        'diff_method_lvl', 'diff_class_lvl',
                                                        col1,
                                                        col2,
                                                        col3])

        metrics_df.rename(columns={rename_col: 'degradation'}, inplace=True)

        return metrics_df

    @staticmethod
    def _transform_categorical(input_data):

        # input_data["opened_by"] = pd.Categorical(input_data["opened_by"])

        return input_data

    @staticmethod
    def _swap_df_keys(result):
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

        result.rename(columns=result.iloc[0], inplace=True)
        result.drop(result.index[0], inplace=True)
        result = result.rename(columns=names_key)

        return result.transpose()

    @staticmethod
    def _drop_columns(input_data):
        columns = ['core_developers', 'mean_number_of_words', 'mean_time_between_comments', 'last_and_close',
                   'open_and_first', 'density_design_keywords', 'density_refactoring_keywords',
                   'number_design_keywords', 'discussion_size', 'discussion_duration', 'contributors',
                   'number_of_words', 'number_refactoring_keywords', 'newbies', 'users_left_size']

        input_data.drop(columns=columns, inplace=True)

        return input_data

    def join_dataframes(self):
        if len(self.class_density_all.columns) == 0:
            self.class_density_all = self.class_density
        else:
            self.class_density_all = self.class_density_all.append(self.class_density, ignore_index=True)

        if len(self.method_density_all.columns) == 0:
            self.method_density_all = self.method_density
        else:
            self.method_density_all = self.method_density_all.append(self.method_density, ignore_index=True)

        if self.owner not in self.class_density_community.keys():
            self.class_density_community[self.owner] = pd.DataFrame()

        if len(self.class_density_community[self.owner].columns) == 0:
            self.class_density_community[self.owner] = self.class_density
        else:
            self.class_density_community[self.owner] = \
                self.class_density_community[self.owner].append(self.class_density, ignore_index=True)

        if self.owner not in self.method_density_community.keys():
            self.method_density_community[self.owner] = pd.DataFrame()

        if len(self.method_density_community[self.owner].columns) == 0:
            self.method_density_community[self.owner] = self.method_density
        else:
            self.method_density_community[self.owner] = \
                self.method_density_community[self.owner].append(self.method_density, ignore_index=True)



