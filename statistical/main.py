import Regressão_multipla_ultils as a

# !/usr/bin/env Rscript

# Title     : Evaluate the metrics through logistic regression models
# Objective : Use the odds ratio of logistic regression models to evaluate the social metrics

# Import the logistic regression necessary functions (logistic_regression_utils.R)

input_types = ["degradation_on_density_high_level_smells/",
               "degradation_on_density_low_level_smells/",
               "degradation_on_diversity_high_level_smells/",
               "degradation_on_diversity_low_level_smells/"
               ]

for input_type in input_types:
    path = f"metrics_with_decay/{input_type}"

    a.gen_mixed_models("elasticsearch", input_type, path)
    a.gen_mixed_models("netty", input_type, path)
    a.gen_mixed_models("okhttp", input_type, path)
    a.gen_mixed_models("rxjava", input_type, path)
    a.gen_mixed_models("presto", input_type, path)
    a.gen_mixed_models("all", input_type, path)
