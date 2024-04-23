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
        if country != 'UNKNOWN OR NOT STATED':
            try:
                pycountry.countries.lookup(country)
            except:
                not_found_country[country] += 1
                not_found_row_num += 1
                df.at[i, 'MADE_IN_COUNTRY'] = None
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
        if not re.match(datetime_pattern, date):
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
def health_invalid(input_path, is_write_invalid_csv=False, invalid_csv_path=None):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_path)

    # Find invalid country
    not_found_country = find_invalid_country(df)
    # Find invalid date
    invalid_date = find_invalid_date(df)
    # Find invalid concentration
    invalid_concentration = find_invalid_date(df)

    if is_write_invalid_csv:
        # assign header columns
        headerList = ['column_name', 'value', 'frequency', 'category']

        # open CSV file and assign header
        with open(invalid_csv_path, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=headerList)
            writer.writeheader()

            # write invalid country to csv
            for key, val in not_found_country.items():
                row = {'column_name': 'MADE_IN_COUNTRY',
                       'value': key,
                       'frequency': val,
                       'category': 'Invalid'}
                writer.writerow(row)

            # write invalid date to csv
            for key, val in invalid_date.items():
                row = {'column_name': 'COLLECTION_DATE',
                       'value': key,
                       'frequency': val,
                       'category': 'Invalid'}
                writer.writerow(row)

            # write invalid concentration to csv
            for key, val in invalid_concentration.items():
                row = {'column_name': 'CONCENTRATION',
                       'value': key,
                       'frequency': val,
                       'category': 'Invalid'}
                writer.writerow(row)

    return df

if __name__ == "__main__":
    health_invalid('../dataset/Metal_Content_of_Consumer_Products_Tested_by_the_NYC_Health_Department_20240403.csv',
               True, 'result/health-invalid.csv')
