import pandas as pd
import numpy as np

from nullChecker import nullChecker  # Ensure this function is correctly imported

# Obtain the tuple from the function, assuming the DataFrame is its first item
#results_tuple = nullChecker('../dataset/Metal_Content_of_Consumer_Products_Tested_by_the_NYC_Health_Department_20240403.csv')
results_tuple = nullChecker('../dataset/SARS-CoV-2_concentrations_measured_in_NYC_Wastewater_20240403.csv')
algorithm_results_raw = results_tuple[0]

null_counts_per_column = algorithm_results_raw.isnull().sum()
print(null_counts_per_column)
print(results_tuple[1])
# Identify null values in the DataFrame
algorithm_results = algorithm_results_raw.isnull()

#true_labels = pd.read_csv('../dataset/Labeled_Null_Metal.csv')
true_labels = pd.read_csv('../dataset/Labeled_Null_SARS.csv')


TP = np.sum((algorithm_results == True) & (true_labels == True))
FP = np.sum((algorithm_results == True) & (true_labels == False))
FN = np.sum((algorithm_results == False) & (true_labels == True))


# Calculate precision and recall
TP_sum = TP.sum(axis=0)
FP_sum = FP.sum(axis=0)
FN_sum = FN.sum(axis=0)

precision = TP_sum / (TP_sum + FP_sum) if (TP_sum + FP_sum) > 0 else 0
recall = TP_sum / (TP_sum + FN_sum) if (TP_sum + FN_sum) > 0 else 0

print(f"Precision: {precision}")
print(f"Recall: {recall}")
