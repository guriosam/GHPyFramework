import subprocess
from tkinter.font import families

from sklearn import metrics
from sklearn.metrics import confusion_matrix, classification_report
from statsmodels.genmod.families import Binomial
#pip install -r requirements.txt
try:
    import numpy as np
except ImportError:
    subprocess.call(['pip', 'install', 'numpy'])
finally:
    import numpy as np

try:
    from sklearn.svm import SVC
except ImportError:
    subprocess.call(['pip', 'install', 'scikit-learn'])
finally:
    from sklearn.svm import SVC

try:
    import pandas as pd
except ImportError:
    subprocess.call(['pip', 'install', 'pandas'])
finally:
    import pandas as pd

try:
    import statsmodels.formula.api as sm
except ImportError:
    subprocess.call(['pip', 'install', 'statsmodels'])
finally:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf


from scipy.stats import skew
from statsmodels.stats.outliers_influence import variance_inflation_factor


def deviance(X, y, model):
    return 2 * metrics.log_loss(y, model.predict_proba(X), normalize=False)


def glm_feats(project, type, input_data, features):
    # Subset by the measures
    input_data = input_data[features]

    # Get numeric and non-numeric feats
    num_input_data = input_data.select_dtypes(include=np.number)
    nnum_input_data = input_data.select_dtypes(exclude=np.number)

    num_input_data = num_input_data.dropna(axis=0)
    num_input_data = num_input_data.loc[:, num_input_data.isna().sum() == 0]

    # Remove highly correlated predictors (VIF >= 10 or cor >= 0.7)
    vif = [variance_inflation_factor(num_input_data.values, i) for i in range(num_input_data.shape[1])]
    highlyCor = np.array([i for i, v in enumerate(vif) if v >= 10])
    cor_matrix = num_input_data.corr()
    cor_highlyCor = np.array(np.where(np.abs(cor_matrix.iloc[highlyCor, highlyCor]) >= 0.7)).flatten()
    highlyCor = np.unique(np.concatenate((highlyCor, cor_highlyCor)))
    num_input_data = num_input_data.iloc[:, np.setdiff1d(np.arange(num_input_data.shape[1]), highlyCor)]

    # Merge numeric and non-numeric feats
    input_data = pd.concat([nnum_input_data, num_input_data], axis=1)

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
    input_data.loc[:, indexes] = (input_data.loc[:, indexes] - input_data.loc[:, indexes].mean()) / input_data.loc[:,
                                                                                                    indexes].std()

    input_data.columns = input_data.columns.str.strip()
    input_data = pd.get_dummies(input_data, columns=['opened_by'], drop_first=True)

    # Create the glm formula and model
    dec_pred = input_data.columns[0]
    preds = input_data.columns[1:]
    glm_formula = f"{dec_pred} ~ {' + '.join(preds)}"
    #glm_model = sm.glm(endog=input_data[dec_pred], exog=input_data[preds], family=sm.families.Binomial())
    glm_model = smf.glm(formula=glm_formula, data=input_data, family=sm.families.Binomial())

    results = glm_model.fit()
    print(results.summary())
    #predictions = results.predict()
    #print(predictions)

    # Model statistics and metrics
    # Calcular a deviance residual
    # residual_deviance = glm_model.null_deviance - glm_model.deviance
    #
    # # Calcular o D-squared
    # dsquared = residual_deviance / glm_model.null_deviance
    #
    # # Imprimir o resultado
    # print(f"Deviance Explained (D-squared): {dsquared}\n")
    #
    # output_df = pd.DataFrame(np.round(np.exp(pd.concat([glm_model.params, glm_model.conf_int()], axis=1)), 3),
    #                          columns=['odds.ratio', 'CI_lower', 'CI_upper'])
    # output_df['p_value'] = np.round(glm_model.pvalues, 3)
    # output_df['significant'] = np.where(output_df['p_value'] <= 0.001, '\u2713', '\u2717')
    #
    # output_path = f"output/{type}{project}.csv"
    # print(output_path)
    # output_df.to_csv




def bind_all_data(path):
    # Lista dos projetos GitHub
    projects = ["elasticsearch", "netty", "rxjava", "presto", "okhttp"]
    # DataFrame de saída e flag
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


import pandas as pd


def gen_mixed_models(project, type, path):
    import pandas as pd

    # Verifica se todos os projetos devem ser analisados
    if project == "all":
        # Junta todos os dados de entrada em um único dataframe
        input_data = bind_all_data(path)
    else:
        # Lê o arquivo de entrada específico para o projeto indicado
        input_path = f"{path}{project}.csv"
        input_data = pd.read_csv(input_path)

    # Exibe os dados de entrada
    print(input_data)

    # Converte o valor da coluna "degradation" para um valor numérico
    # (1 para "True" e 0 para "False") e transforma em uma variável categórica
    input_data["degradation"] = pd.factorize(input_data["degradation"])[0]

    # Transforma a coluna "opened_by" em uma variável categórica
    input_data["opened_by"] = pd.Categorical(input_data["opened_by"])

    # Exibe os dados de entrada após as transformações
    print("depois")
    print(input_data)

    # Exibe informações sobre as variáveis do conjunto de dados
    input_data.info()

    # Define quais variáveis serão utilizadas na análise
    paper_feats = [
        "degradation",
        "patch_size",
        "patch_churn",
        "diff_complexity",
        "diff_size",
        # Comunicação entre desenvolvedores
        "number_comments",
        "number_users",
        "number_contributors",
        "number_core_devs",
        "opened_by",
        "mean_time_between_replies",
        "discussion_length",
        # Conteúdo das discussões
        "number_of_patches",
        "words_in_discussion",
        "words_per_comment_in_discussion",
        "snippets_size",
    ]
    print(paper_feats)

    # Executa um modelo GLM
    glm_feats(project, type, input_data, paper_feats)






