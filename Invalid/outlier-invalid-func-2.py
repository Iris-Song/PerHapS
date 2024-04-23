from pyod.models.ecod import ECOD
from pyod.models.knn import KNN
from pyod.models.iforest import IForest
from pyod.models.abod import ABOD
from pyod.models.hbos import HBOS
from pyod.models.feature_bagging import FeatureBagging
from pyod.utils.data import evaluate_print
import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import csv
import collections

def get_data(df_cleaned, row_cleaned_num, x_col, y_col, contamination):
    n_train = row_cleaned_num  # number of training points
    d_train = df_cleaned
    
    # Initialize the scaler
    scaler = StandardScaler()
    # Fit the scaler to the data
    scaler.fit(d_train)
    # Transform the data
    d_train_t = scaler.transform(d_train)
    # Convert back to DataFrame
    d_train = pd.DataFrame(d_train_t, columns=d_train.columns)

    X_train = d_train[[x_col,y_col]].values
    y_train = [0] * n_train
    return X_train, y_train


def evaluate_module(clf_name, y_train, y_train_scores, y_test, y_test_scores):
    # evaluate and print the results
    print("\nOn Training Data:")
    evaluate_print(clf_name, y_train, y_train_scores)
    print("\nOn Test Data:")
    evaluate_print(clf_name, y_test, y_test_scores)


def draw_subplot(clf_name, X_train, y_train, y_train_pred, x_col, y_col, i):
    plt.subplot(4, 2, i)
    # Plot the training data points
    plt.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap='coolwarm', label='Ground Truth')

    # Highlight the outliers
    outliers = X_train[y_train_pred == 1]
    plt.scatter(outliers[:, 0], outliers[:, 1], marker='x', color='red', label='Predicted Outliers')

    plt.title(clf_name)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.legend()


def get_outliers_dict(clf_name, df_cleaned, y_train_pred, outliers_dict):
    for i, x in enumerate(df_cleaned.values):
        if y_train_pred[i] == 1:
            outliers_dict[(x[0],x[1])].add(clf_name)


def get_outliers_cnt(df_cleaned, outliers_dict):
    outlier_cnt = collections.Counter()
    for num in df_cleaned.values:
        if (num[0],num[1]) in outliers_dict:
            outlier_cnt[(num[0],num[1])] += 1
    return outlier_cnt


def write_invalid_csv(invalid_csv_path, x_col, y_col, outliers_dict, outlier_cnt):
    headerList = ['column_name', 'value', 'frequency', 'category']
    with open(invalid_csv_path, 'a') as file:
        writer = csv.DictWriter(file, fieldnames=headerList)
        for key, value in outliers_dict.items():
            writer.writerow(
                {'column_name': x_col + ',' + y_col,
                 'value': key, 
                 'frequency': outlier_cnt[key], 
                 'category': "Outlier-" + ",".join(list(value))}
            )
 

def train_models(X_train, y_train, 
                x_col, y_col, 
                contamination, df_cleaned, 
                is_write_invalid_csv, invalid_csv_path):
    models = {
        'KNN_largest': KNN(contamination=contamination, n_neighbors=10, method='largest'),
        'KNN_mean': KNN(contamination=contamination, n_neighbors=10, method='mean'),
        'KNN_median': KNN(contamination=contamination, n_neighbors=10, method='median'),
        'IForest': IForest(contamination=contamination),
        'ABOD': ABOD(contamination=contamination),
        'HBOS': HBOS(contamination=contamination),
        'ECOD': ECOD(contamination=contamination),
        "Feature Bagging": FeatureBagging(contamination=contamination)
    }

    # train models
    i = 1
    outliers_dict = collections.defaultdict(set)
    plt.figure(figsize=(16, 12))
    for clf_name, clf in models.items():
        print(clf_name)
        clf.fit(X_train)
        y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
        y_train_scores = clf.decision_scores_  # raw outlier scores
        # evaluate_module(clf_name, y_train, y_train_scores, y_test, y_test_scores)
        draw_subplot(clf_name, X_train, y_train, y_train_pred, x_col, y_col, i)
        i += 1

        # get outliers
        get_outliers_dict(clf_name, df_cleaned, y_train_pred, outliers_dict)
    
    outlier_cnt = get_outliers_cnt(df_cleaned, outliers_dict)
    # write invalid data to CSV
    if is_write_invalid_csv:
        write_invalid_csv(invalid_csv_path, x_col, y_col, outliers_dict, outlier_cnt)

    plt.tight_layout()
    plt.show()


def outlier_invalid(input_path, x_col, y_col, is_write_invalid_csv=False, invalid_csv_path=None):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_path)
    df_cleaned = df[[x_col,y_col]].dropna()
    row_cleaned_num = df_cleaned.count()[0]

    contamination = 0.01
    X_train, y_train = get_data(df_cleaned, row_cleaned_num, 
                                x_col, y_col, contamination)

    train_models(X_train, y_train, 
                x_col, y_col, 
                contamination, df[[x_col,y_col]].dropna(),
                is_write_invalid_csv, invalid_csv_path)
     

if __name__ == "__main__":
    is_write_invalid_csv = True
    invalid_csv_path = 'result/outlier-invalid-2.csv'
    if is_write_invalid_csv:
        headerList = ['column_name', 'value', 'frequency', 'category']
        # open CSV file and assign header
        with open(invalid_csv_path, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=headerList)
            writer.writeheader()

    for x_col, y_col in [
        ('Concentration SARS-CoV-2 gene target (N1 Copies/L) ','Per capita SARS-CoV-2 load (N1 copies per day per population)'),
        ('Concentration SARS-CoV-2 gene target (N1 Copies/L) ','Population Served, estimated '),
        ('Population Served, estimated ','Per capita SARS-CoV-2 load (N1 copies per day per population)')]:
            outlier_invalid('../dataset/SARS-CoV-2_concentrations_measured_in_NYC_Wastewater_20240403.csv', 
                    x_col, y_col, True, invalid_csv_path)
                    