import pandas as pd
from scipy.stats import wilcoxon, ranksums


def wilcoxon_test(input_data, metric):
    degraded_dist = input_data[input_data["design_change"] == True][metric]
    clean_dist = input_data[input_data["design_change"] == False][metric]

    # Realizar o teste de Wilcoxon
    # Inicializar a variável pvalue com None
    pvalue = None

    # Realizar o teste de Wilcoxon apenas se as amostras tiverem tamanho suficiente
    if degraded_dist.size > 0 and clean_dist.size > 0:
        test_stat, pvalue =  ranksums(degraded_dist, clean_dist)

    # Verificar se pvalue foi atribuída com sucesso antes de criar o dataframe
    if pvalue is not None:
        # Retornar o resultado
        metric_data = pd.DataFrame({"metric": [metric], "pvalue": [pvalue]})
    else:
        # Retornar NaN se pvalue não foi atribuída
        metric_data = pd.DataFrame({"metric": [metric], "pvalue": [float('nan')]})



    return metric_data

# Definir os projetos e métricas
projects = ["elasticsearch", "presto", "netty", "okhttp", "RxJava"]
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
        current_metrics = pd.read_csv(path+".csv")


        # Realizar o teste de Wilcoxon para todas as métricas
        for metric in metrics:
            metric_data = wilcoxon_test(current_metrics, metric)
            output_data = pd.concat([output_data, metric_data])

        # Verificar a significância estatística
        output_data["significant"] = output_data["pvalue"] <= 0.05
        print("Project:", project)
        print(output_data)

