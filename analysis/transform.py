import pandas as pd
import streamlit as st
import numpy as np

import jellyfish
import re

from utility_functions import sort_alfanumeric, emphasize_numbers


def group_and_calculate_percentage(df, group_by_col, sum_col, col=None, percentage_col_name='Percentage'):
    # Define the aggregation dictionary
    agg_dict = {sum_col: 'sum'}
    
    # If col is provided, include it in the aggregation dictionary
    if col:
        agg_dict[col] = 'first'
    
    # Group by the specified columns and aggregate
    grouped_df = df.groupby(group_by_col).agg(agg_dict).reset_index()

    # Calculate the total sum for the percentage calculation
    total_sum = grouped_df[sum_col].sum()

    # Calculate the percentage and create a new column for it
    grouped_df[percentage_col_name] = round((grouped_df[sum_col] / total_sum) * 100,2)

    first_column_name = grouped_df.columns[0]


    grouped_df = sort_alfanumeric(grouped_df, first_column_name)

    return grouped_df

def group_and_get_filtered_max_value(df, group_by_col, sum_col, value_filter):
    """
    Groups the DataFrame by the specified column, sums another column,
    and returns the sum of the specified sum_col for the filtered group.

    Parameters:
    df (pd.DataFrame): The DataFrame to group and aggregate.
    group_by_col (str): The column to group by.
    sum_col (str): The column to sum.
    value_filter (str): The value to filter the group_by_col.

    Returns:
    float: The sum of the specified sum_col for the filtered group.
    """
    # Group by the specified column and sum the specified column
    grouped_df = df.groupby(group_by_col)[sum_col].sum().reset_index()

    # Sort alphanumerically
    grouped_df = sort_alfanumeric(grouped_df, group_by_col)
    # print(grouped_df)

    # Check if the value_filter exists in the grouped_df
    if value_filter not in grouped_df[group_by_col].values:
        return 0
    
    # Filter the group_by_col to return the value in sum_col
    filtered_value = grouped_df.loc[grouped_df[group_by_col] == value_filter, sum_col].values[0]

    # filtered_value = grouped_df[sum_col].values[0]

    return filtered_value

def group_and_get_filtered_min_value(df, column1, column2, sum_col, filter_value):
    """
    Groups the DataFrame by two columns, sums another column,
    and returns the minimum aggregated value of the sum_col for each unique value in column1.

    Parameters:
    df (pd.DataFrame): The DataFrame to group and aggregate.
    column1 (str): The first column to group by.
    column2 (str): The second column to group by.
    sum_col (str): The column to sum.
    filter_value (str): The value to filter column1 before grouping.

    Returns:
    float: The minimum aggregated value of the sum_col for the filtered group.
    """
    # Group by column1 and column2, and sum sum_col
    grouped_df = df.groupby([column1, column2])[sum_col].sum().reset_index()
    
    if filter_value not in grouped_df[column1].values:
        return 0

    # Filter the DataFrame by the filter_value
    filtered_group = grouped_df[grouped_df[column1] == filter_value]

    # Check if the filtered DataFrame is not empty
    if not filtered_group.empty:
        # Find the minimum value of the aggregated column (sum_col)
        min_value = filtered_group[sum_col].min()
        return min_value if min_value <= 0 else 0
    else:
        return 0


    
def group_and_calculate_percentage_with_names(df, group_by_col, sum_col, names_col1='Donnée environnementale (DE)', names_col2='Lot'):
    """
    Groups the DataFrame by the specified columns, sums another column,
    and calculates the percentage of the total for each group.

    Parameters:
    df (pd.DataFrame): The DataFrame to group and aggregate.
    group_by_col (str): The column to group by.
    sum_col (str): The column to sum.
    names_col (str): The column to include in the grouping.

    Returns:
    pd.DataFrame: A DataFrame with grouped columns, sum, and percentage of the total.
    """
    # Group by the specified columns and sum the specified column
    grouped_df = df.groupby([group_by_col, names_col1, names_col2])[sum_col].sum().reset_index()
    

    # Calculate the total sum for the percentage calculation
    total_sum = grouped_df[sum_col].sum()

    # Calculate the percentage and create a new column for it
    grouped_df['percentage_total'] = round((grouped_df[sum_col] / total_sum) * 100,2)

    first_column_name = grouped_df.columns[0]

    grouped_df = sort_alfanumeric(grouped_df, first_column_name)

    return grouped_df

def join_and_rename_columns(df1, df2, lot='Lot'): #in case we want to deal with both eval or both explo change this function
    """
    Joins two DataFrames on the 'lot' column and renames the GES_divided_by__SREF columns to 'eval' and 'explo'.

    Parameters:
    df1 (pd.DataFrame): EVAL DataFrame containing 'lot' and 'GES_divided_by__SREF' columns.
    df2 (pd.DataFrame): EXPLO DataFrame containing 'lot' and 'GES_divided_by__SREF' columns.

    Returns:
    pd.DataFrame: The joined DataFrame with renamed columns.
    """
    # Rename columns for clarity before merging
    df1_renamed = df1.rename(columns={'GES_divided_by__SREF': 'eval'})
    df2_renamed = df2.rename(columns={'GES_divided_by__SREF': 'explo'})
    
    # Merge the DataFrames on the 'lot' column
    merged_df = pd.merge(df1_renamed, df2_renamed, on=lot, how='outer')
    
    return merged_df

def jaro_winkler_similarity_with_emphasis(s1, s2):
    """
    Calculates Jaro-Winkler similarity with emphasis on numbers.
    """
    s1_emphasized = emphasize_numbers(s1)
    s2_emphasized = emphasize_numbers(s2)
    return jellyfish.jaro_winkler_similarity(s1_emphasized, s2_emphasized)

def join_dataframes_jaro(df_eval, df_explo, key_col='Donnée environnementale (DE)', id_col='ID-DE', suffix_eval='_eval', suffix_explo='_explo', threshold=0.8):
    """
    Joins two DataFrames on the specified key column based on Jaro-Winkler similarity, keeping common rows,
    and renames specified columns with provided suffixes.

    Parameters:
    df_eval (pd.DataFrame): The first DataFrame.
    df_explo (pd.DataFrame): The second DataFrame.
    key_col (str): The column to join on. Default is 'Donnée environnementale (DE)'.
    id_col (str): The ID column to keep. Default is 'ID-DE'.
    suffix_eval (str): The suffix for columns from the first DataFrame. Default is '_eval'.
    suffix_explo (str): The suffix for columns from the second DataFrame. Default is '_explo'.
    threshold (float): The similarity threshold for considering rows as equal. Default is 0.8.

    Returns:
    pd.DataFrame: The joined DataFrame.
    """
    # Drop rows with None values in the key column
    df_eval = df_eval.dropna(subset=[key_col])
    df_explo = df_explo.dropna(subset=[key_col])

    # Select columns to keep
    cols_to_keep_eval = [id_col, 'Lot', key_col, 'Quantité', 'GES_divided_by__SREF']
    cols_to_keep_explo = [id_col, 'Lot', key_col, 'Quantité', 'GES_divided_by__SREF']

    # Prepare a list to hold the rows for the merged DataFrame
    merged_rows = []

    for _, row_eval in df_eval.iterrows():
        best_match = None
        best_score = 0

        for _, row_explo in df_explo.iterrows():
            similarity = jaro_winkler_similarity_with_emphasis(row_eval[key_col], row_explo[key_col])
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = row_explo

        if best_match is not None:
            merged_row = {
                f'{id_col}{suffix_eval}': row_eval[id_col],
                f'{id_col}{suffix_explo}': best_match[id_col],
                f'Lot{suffix_eval}': row_eval['Lot'],
                f'Lot{suffix_explo}': best_match['Lot'],
                f'{key_col}{suffix_eval}': row_eval[key_col],
                f'{key_col}{suffix_explo}': best_match[key_col],
                f'Quantité{suffix_eval}': row_eval['Quantité'],
                f'Quantité{suffix_explo}': best_match['Quantité'],
                f'GES_divided_by__SREF{suffix_eval}': row_eval['GES_divided_by__SREF'],
                f'GES_divided_by__SREF{suffix_explo}': best_match['GES_divided_by__SREF']
            }
            merged_rows.append(merged_row)

    merged_df = pd.DataFrame(merged_rows)
    return merged_df

def filter_dataframes_jaro(base_df, eliminate_df, key_col='Donnée environnementale (DE)', threshold=0.8):
    """
    Filters the base DataFrame by removing rows that have a similar match in the eliminate DataFrame
    based on Jaro-Winkler similarity.

    Parameters:
    base_df (pd.DataFrame): The base DataFrame.
    eliminate_df (pd.DataFrame): The DataFrame with elements to eliminate.
    key_col (str): The column to compare on. Default is 'Donnée environnementale (DE)'.
    threshold (float): The similarity threshold for considering rows as a match. Default is 0.8.

    Returns:
    pd.DataFrame: The filtered base DataFrame.
    """
    # Drop rows with None values in the key column
    base_df = base_df.dropna(subset=[key_col])
    eliminate_df = eliminate_df.dropna(subset=[key_col])

    # List to store indices to drop
    indices_to_drop = []

    for idx_base, row_base in base_df.iterrows():
        match_found = False
        for _, row_elim in eliminate_df.iterrows():
            similarity = jaro_winkler_similarity_with_emphasis(row_base[key_col], row_elim[key_col])
            if similarity >= threshold:
                match_found = True
                break

        if match_found:
            indices_to_drop.append(idx_base)

    # Drop rows that matched the eliminate criteria
    filtered_df = base_df.drop(indices_to_drop).reset_index(drop=True)

    return filtered_df

def get_combined_total_ges(df1, df2, key_col='Donnée environnementale (DE)', ges_column='GES_divided_by__SREF'):
    """
    Calculate the total sum of the GES_divided_by__SREF column for each DataFrame, 
    excluding rows where Donnée environnementale (DE) is null, and return the combined total sum.

    Parameters:
    df1 (pd.DataFrame): The first DataFrame.
    df2 (pd.DataFrame): The second DataFrame.
    key_col (str): The column name to check for null values. Default is 'Donnée environnementale (DE)'.
    ges_column (str): The column name to sum. Default is 'GES_divided_by__SREF'.

    Returns:
    float: The combined total sum of the specified column for both DataFrames.
    """
    # Filter out rows where the key column is null
    df1_filtered = df1.dropna(subset=[key_col])
    df2_filtered = df2.dropna(subset=[key_col])

    # Sum the GES column for both filtered dataframes
    total_ges_df1 = df1_filtered[ges_column].sum()
    total_ges_df2 = df2_filtered[ges_column].sum()

    combined_total_ges = round(total_ges_df1 + total_ges_df2,2)

    return combined_total_ges

def sum_top_n_elements(df, column, n):
    """
    Sums the top n elements in the specified column of the DataFrame after sorting.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    column (str): The column to sort and sum.
    n (int): The number of top elements to sum.

    Returns:
    float: The total sum of the top n elements in the specified column.
    """
    # Sort the DataFrame by the specified column in descending order
    df_sorted = df.sort_values(by=column, ascending=False)
    
    # Sum the top n elements in the sorted column
    total_sum = df_sorted[column].head(n).sum()
    
    return total_sum

def find_sref_batiment_and_next(df, n_col):
    """
    Finds the 'Sref bâtiment' or 'Surface de référence - Sref' value in the specified column of the DataFrame 
    and returns the next value as a float for 'Sref bâtiment' or the value three rows below as a float for 
    'Surface de référence - Sref'. If the key value is not found, prints an urgent message.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to search.
    n_col (int): The index of the column to search.
    
    Returns:
    float: The value following 'Sref bâtiment' as a float or the value three rows below 'Surface de référence - Sref' as a float.
    """
    column = df.columns[n_col]
    found = False
    for i in range(len(df[column]) - 3):  # Adjusted to -3 to prevent out of range error
        if df[column].iloc[i] == 'Sref bâtiment':
            found = True
            next_value = df[column].iloc[i + 1]
            try:
                return float(next_value)
            except ValueError:
                print('The value after sref_batiment cannot be converted to a float.')
                return None
        elif df[column].iloc[i] == 'Surface de référence - Sref':
            found = True
            next_value = df[column].iloc[i + 3]
            try:
                return float(next_value)
            except ValueError:
                print('The value three rows below Surface de référence - Sref cannot be converted to a float.')
                return None
    
    if not found:
        print('There is a very serious mistake, contact Jorge by slack urgently')
        return None
    

def change_column_if_not_in_list(df, check_col, allowed_values, change_col):
    """
    Changes the values in `change_col` to None if the corresponding value in `check_col` is not in `allowed_values`.

    Parameters:
    df (pd.DataFrame): The DataFrame to process.
    check_col (str): The column to check against `allowed_values`.
    allowed_values (list): The list of allowed values for `check_col`.
    change_col (str): The column to change to None if the check fails.

    Returns:
    pd.DataFrame: The modified DataFrame.
    """
    df.loc[~df[check_col].isin(allowed_values), change_col] = None
    return df