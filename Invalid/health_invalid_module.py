# wrap function in health-invalid.ipynb
import pandas as pd
import pycountry
import re
import collections
import csv


# find invalid country and replace it with None
def find_invalid_country(df):
    # find Invalid country
    country_col = df['MADE_IN_COUNTRY']
    not_found_row_num = 0
    not_found_country = collections.Counter()
    for i, country in enumerate(country_col):
        if country and country != 'UNKNOWN OR NOT STATED':
            try:
                pycountry.countries.lookup(country)
            except:
                not_found_country[country] += 1
                not_found_row_num += 1
    print('Number of rows with unknown country:', not_found_row_num)
    print('Unknown countries:', not_found_country)
    return not_found_country


# find invalid date and replace it with None
def find_invalid_date(df):
    datetime_pattern = re.compile(
        r'\b\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} (?:AM|PM)\b')

    collection_date_col = df['COLLECTION_DATE']
    invalid_date_num = 0
    invalid_date = collections.Counter()
    for i, date in enumerate(collection_date_col):
        if date and not re.match(datetime_pattern, date):
            invalid_date[date] += 1
            invalid_date_num += 1
            df.at[i, 'COLLECTION_DATE'] = None

    print('Number of rows with invalid collection date:', invalid_date_num)
    print('Invalid dates:', invalid_date)
    return invalid_date


# find invalid concentration and replace it with None
def find_invalid_date(df):
    concentration_col = df['CONCENTRATION']
    invalid_concentration_num = 0
    invalid_concentration = collections.Counter()
    for i, concentration in enumerate(concentration_col):
        try:
            float(concentration)
        except:
            invalid_concentration[concentration] += 1
            invalid_concentration_num += 1
            df.at[i, 'CONCENTRATION'] = None

    print('Number of rows with invalid concentration:', invalid_concentration_num)
    print('Invalid concentration:', invalid_concentration)
    return invalid_concentration


# input_path: path to the dataset
# is_write_invalid_csv: write invalid data to csv or not
# return: dataframe of valid data
def health_invalid(input_df, replace_symbol=None):
    # Read the df from input_df
    df = input_df

    # Find invalid country
    not_found_country = find_invalid_country(df)
    # Find invalid date
    invalid_date = find_invalid_date(df)
    # Find invalid concentration
    invalid_concentration = find_invalid_date(df)

    # write invalid df
    invalid_data = {
        'column_name': [],
        'value': [],
        'frequency': [],
        'category': []
    }
    for key, val in not_found_country.items():
        invalid_data['column_name'].append('MADE_IN_COUNTRY')
        invalid_data['value'].append(key)
        invalid_data['frequency'].append(val)
        invalid_data['category'].append('Invalid')
        df['MADE_IN_COUNTRY'] = df['MADE_IN_COUNTRY'].replace(key, replace_symbol)
    
    for key, val in invalid_date.items():
        invalid_data['column_name'].append('COLLECTION_DATE')
        invalid_data['value'].append(key)
        invalid_data['frequency'].append(val)
        invalid_data['category'].append('Invalid')
        df['COLLECTION_DATE'] = df['COLLECTION_DATE'].replace(key, replace_symbol)

    for key, val in invalid_concentration.items():
        invalid_data['column_name'].append('CONCENTRATION')
        invalid_data['value'].append(key)
        invalid_data['frequency'].append(val)
        invalid_data['category'].append('Invalid')
        df['CONCENTRATION'] = df['CONCENTRATION'].replace(key, replace_symbol)
    
    invalid_df = pd.DataFrame(data=invalid_data)

    # print('Invalid data:', invalid_df)
    return df, invalid_df

