import os
import ctypes
from ctypes import c_char_p
import pandas as pd
from io import StringIO
import numpy as np

def find_regular_nulls_in_csv(df):
    null_stats = []
    null_indicators = ['NULL', 'UNKNOWN',"N/A", "missing"]  
    for column in df.columns:
        count_null = df[column].isnull().sum()
        if count_null > 0:
            if np.issubdtype(df[column].dtype, np.datetime64):
                null_type = "NaT"
            elif np.issubdtype(df[column].dtype, np.number):
                null_type = "NaN"
            else:
                null_type = "None"
            append_null_stats(null_stats, column, null_type, count_null)  
        
        if df[column].dtype == 'object':
            for indicator in null_indicators:
                mask = df[column].str.contains(indicator, case=False, na=False)
                unique_nulls = df[column][mask].unique() 

                for unique_null in unique_nulls:
                    count = (df[column] == unique_null).sum() 
                    append_null_stats(null_stats, column, unique_null, count)

    null_df = pd.DataFrame(null_stats)
    return null_df

def append_null_stats(null_stats, column, null_type, count):
    null_stats.append({
        "Column Name": column,
        "Value": null_type,
        "Frequency": count,
        "Category": "NULL Value"
    })


def replace_missing_values(df, missing_values_df):
    for index, row in missing_values_df.iterrows():
        column_name = row['Column Name']
        value_to_replace = row['Value']
        
        if pd.api.types.is_numeric_dtype(df[column_name].dtype):
            try:
                value_to_replace = df[column_name].dtype.type(value_to_replace)
            except ValueError:
                print(f"Warning: Cannot convert {value_to_replace} to {df[column_name].dtype} for column {column_name}")
                continue
        
        # 替换值
        df[column_name] = df[column_name].replace(value_to_replace, np.nan)
    
    return df

def fahes_executor(tName, tool=4):

    # Determine the path to the shared library (libFahes.so)
    libfile = os.path.join(os.path.dirname(__file__), "src", "FAHES.so")


    # Load and configure the shared library
    Fahes = ctypes.CDLL(libfile)
    Fahes.start.restype = ctypes.c_char_p 
    Fahes.start.argtypes = [ctypes.c_char_p, ctypes.c_int]

    # Execute the FAHES tool with the specified parameters
    csv_string = Fahes.start(c_char_p(tName.encode('utf-8')),tool).decode('utf-8')
    dataframe = pd.read_csv(StringIO(csv_string))

    return dataframe


def nullChecker(path):
    # Convert the input file path to an absolute path
    tName = os.path.abspath(path)
    df = pd.read_csv(tName)

    fahes_DMV = fahes_executor(tName, tool=4)
    regular_null = find_regular_nulls_in_csv(df)

    final_null  = pd.concat([fahes_DMV, regular_null], ignore_index=True).drop_duplicates(keep='first')
    print( regular_null )
    output_df = replace_missing_values(df,final_null)

    return df, final_null



