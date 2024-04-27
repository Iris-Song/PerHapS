from pyod.models.ecod import ECOD
from pyod.models.knn import KNN
from pyod.models.iforest import IForest
from pyod.models.abod import ABOD
from pyod.models.hbos import HBOS
from pyod.models.feature_bagging import FeatureBagging
import pandas as pd
import collections

def get_data(df, row_cleaned_num, x_col):
    n_train = row_cleaned_num  # number of training points
    df['tmpy'] = 0
    # Min-Max scaling normalization
    min_val = df[x_col].min()
    max_val = df[x_col].max()
    df[x_col] = (df[x_col] - min_val) / (max_val - min_val)
    d_train = df

    X_train = d_train[[x_col,'tmpy']].values
    y_train = [0] * n_train
    return X_train, y_train


def get_outliers_dict(clf_name, df_cleaned, y_train_pred, outliers_dict):
    for i, x in enumerate(df_cleaned.values):
        if y_train_pred[i] == 1:
            outliers_dict[x[0]].add(clf_name)


def get_outliers_cnt(df_cleaned, outliers_dict):
    outlier_cnt = collections.Counter()
    for num in df_cleaned.values:
        if num[0] in outliers_dict:
            outlier_cnt[num[0]] += 1
    return outlier_cnt


def write_invalid_data(invalid_data, x_col, outliers_dict, outlier_cnt):
    for key, value in outliers_dict.items():
        invalid_data['column_name'].append(x_col)
        invalid_data['value'].append(key)
        invalid_data['frequency'].append(outlier_cnt[key])
        invalid_data['category'].append("Outlier-" + ",".join(list(value)))
        
def update_org_df(org_df, x_col, outliers_dict, replace_symbol):
    for key, _ in outliers_dict.items():
        org_df.loc[org_df[x_col] == key, x_col] = replace_symbol

def train_models(X_train, y_train, 
                x_col, contamination, df_cleaned,
                invalid_data, org_df,
                replace_symbol):
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
    outliers_dict = collections.defaultdict(set)
    
    for clf_name, clf in models.items():
        # print(clf_name)
        clf.fit(X_train)
        y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
        y_train_scores = clf.decision_scores_  # raw outlier scores
        # evaluate_module(clf_name, y_train, y_train_scores, y_test, y_test_scores)
        

        # get outliers
        get_outliers_dict(clf_name, df_cleaned, y_train_pred, outliers_dict)

    outlier_cnt = get_outliers_cnt(df_cleaned, outliers_dict)

    # update invalid data
    write_invalid_data(invalid_data, x_col, outliers_dict, outlier_cnt)

    #update org_df
    update_org_df(org_df, x_col, outliers_dict, replace_symbol)



def outlier_invalid(df, x_col, invalid_data, org_df, replace_symbol):
    # Read the CSV file into a DataFrame
    df_cleaned = df[[x_col]].dropna()
    row_cleaned_num = df_cleaned.count()[0]

    contamination = 0.005
    X_train, y_train = get_data(df_cleaned, row_cleaned_num, 
                                x_col)

    train_models(X_train, y_train, 
                x_col, contamination, df[[x_col]].dropna(),
                invalid_data, org_df, replace_symbol)

    
def outlier_invalid_all(input_df, replace_symbol=None): 
    df = input_df

    invalid_data = {
        'column_name': [],
        'value': [],
        'frequency': [],
        'category': []
    }

    for col in ['Concentration SARS-CoV-2 gene target (N1 Copies/L) ',
                'Per capita SARS-CoV-2 load (N1 copies per day per population)',
                'Population Served, estimated ']:
                outlier_invalid(df, col, invalid_data, df, replace_symbol)

    invalid_df = pd.DataFrame(data=invalid_data)

    # print('Invalid data:', invalid_df)
    # print('Valid data:', df)
    return df, invalid_df
                
if __name__ == "__main__":
    input_path = '../dataset/SARS-CoV-2_concentrations_measured_in_NYC_Wastewater_20240403.csv'
    df = pd.read_csv(input_path)
    outlier_invalid_all(df)