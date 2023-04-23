import pandas as pd
from scipy.stats import wilcoxon


# Função para realizar o teste de Wilcoxon
def wilcoxon_test(input_data, metric):
    # Separar as distribuições "degraded" e "clean"
    degraded_dist = input_data[input_data["degradation"] == "True"][metric]
    clean_dist = input_data[input_data["degradation"] == "False"][metric]

    # Realizar o teste de Wilcoxon
    test_stat, pvalue = wilcoxon(degraded_dist, clean_dist)

    # Retornar o resultado
    metric_data = pd.DataFrame({"metric": [metric], "pvalue": [pvalue]})
    return metric_data


# Definir os projetos e métricas
projects = ["elasticsearch", "presto", "netty", "okhttp", "RxJava", "all"]
metrics = ["number_comments", "number_users", "number_contributors", "number_core_devs", "number_of_patches",
           "words_in_discussion", "words_per_comment_in_discussion", "snippets_size",
           "mean_time_between_replies", "discussion_length"]

input_types = ["design_changed/design_change_on_density_high_level_smells/",
               "design_changed/design_change_on_density_low_level_smells/",
               "design_changed/design_change_on_diversity_high_level_smells/",
               "design_changed/design_change_on_diversity_low_level_smells/"
               ]

for input_type in input_types:
    for project in projects:
        # Criar o dataframe de saída
        output_data = pd.DataFrame(columns=["metric", "pvalue"])

        path = input_type + project

        # Carregar o conjunto atual de métricas
        current_metrics = pd.read_csv(path + ".csv")

        # Realizar o teste de Wilcoxon para todas as métricas
        for metric in metrics:
            metric_data = wilcoxon_test(current_metrics, metric)
            output_data = output_data.append(metric_data)

        # Verificar a significância estatística
        output_data["significant"] = output_data["pvalue"] <= 0.05
        print("Project:", project)
        print(output_data)
