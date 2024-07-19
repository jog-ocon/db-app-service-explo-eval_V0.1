import pandas as pd
import streamlit as st
import numpy as np

def clean_join_df(df_eval, df_contributeurs_eval, sref): #its called df_eval here but it can be explo or eval
    pd.set_option('future.no_silent_downcasting', True)
    
    df_eval['kg éq. CO2 / Unité (de la DE) / Durée de vie bâtiment.1'] = df_eval['kg éq. CO2 / Unité (de la DE) / Durée de vie bâtiment.1'].replace('-', 0)
    # 1. Dtypes management
    # Convert the specified column to numeric, coercing errors to NaN
    df_eval['kg éq. CO2 / Unité (de la DE) / Durée de vie bâtiment.1'] = pd.to_numeric(df_eval['kg éq. CO2 / Unité (de la DE) / Durée de vie bâtiment.1'], errors='coerce')
    # Ensure the column 'Lot Personnalisé' is of type object
    df_eval['Lot Personnalisé'] = df_eval['Lot Personnalisé'].astype('object')
    
    
    # 2. Rename columns and add GES
    # Rename the column
    df_eval.rename(columns={'kg éq. CO2 / Unité (de la DE) / Durée de vie bâtiment.1': 'GES dyn par unité'}, inplace=True)
    
    # ADD Calculate 'GES total par composant'
    df_eval['GES total par composant'] = df_eval['GES dyn par unité'] * df_eval['Quantité']

    # ADD GES divided by sref
    divisor = sref
    df_eval['GES_divided_by__SREF'] = df_eval['GES total par composant'] / divisor
    
    # 3. Filter the second DataFrame
    # Define the criteria for filtering
    criteria = ["Contributeur Chantier"]
    filtered_df = df_contributeurs_eval[df_contributeurs_eval['Localisation'].isin(criteria)]
    
    # 4. Add contributeur
    # Create a new row with NaN values
    new_row = pd.Series([np.nan] * df_eval.shape[1], index=df_eval.columns)
    new_row = new_row.astype('object') #to avoid working with None
    # Assign values from filtered_df to the appropriate columns in new_row
    new_row['Composant'] = str(filtered_df['Localisation'].values[0])
    new_row['Lot'] = str(filtered_df['Localisation'].values[0])
    new_row['Sous-lot'] = str(filtered_df['Localisation'].values[0])
    new_row['GES total par composant'] = float(filtered_df['Total cycle de vie'].values[0])
    new_row['GES_divided_by__SREF'] = float(filtered_df['Total cycle de vie'].values[0]) / divisor  #un poco a la babosa, pensar en refactorizar esta funcion
    
    new_row = new_row.to_frame().T

    # Match dtypes to df before concatenating
    for column in new_row.columns:
        if column in new_row.columns:
            new_row[column] = new_row[column].astype(df_eval[column].dtype, errors='ignore')
    
    # 5. Append the new row to df_eval
    new_row = new_row.astype(df_eval.dtypes.to_dict(), errors='ignore') # Ensure the types match for the new row DataFrame before concatenating
    df_eval = pd.concat([df_eval, new_row], ignore_index=True)

    #6 drop zeros in quantity
    df_eval = df_eval[df_eval['Quantité'] != 0]

    #replacing / from lot10 and lot11
    df_eval.loc[df_eval['Lot'].str.contains('Lot 10', na=False), 'Sous-lot'] = '10. Réseaux énergie - courant fort'
    df_eval.loc[df_eval['Lot'].str.contains('Lot 11', na=False), 'Sous-lot'] = '11 Réseaux de communication - courant faible'
    df_eval.loc[df_eval['Lot'].str.contains('Lot 12', na=False), 'Sous-lot'] = '12. Appareils élévateurs et autres équipements de transport intérieur'
    # df_eval.loc[df_eval['Lot'].str.contains('Lot 13', na=False), 'Sous-lot'] = '13. Réseaux énergie - courant fort'

    #7 or idk i lost the count : round all floats columns
    df_eval[df_eval.select_dtypes(include=['float']).columns] = df_eval.select_dtypes(include=['float']).round(2)
    


    
    return df_eval

def join_dataframes(df_eval, df_explo, key_col='ID-DE', suffix_eval='_eval', suffix_explo='_explo'):
    """
    Joins two DataFrames on the specified key column, keeping common rows, 
    and renames specified columns with provided suffixes.

    Parameters:
    df_eval (pd.DataFrame): The first DataFrame.
    df_explo (pd.DataFrame): The second DataFrame.
    key_col (str): The column to join on. Default is 'ID-DE'.
    suffix_eval (str): The suffix for columns from the first DataFrame. Default is '_eval'.
    suffix_explo (str): The suffix for columns from the second DataFrame. Default is '_explo'.

    Returns:
    pd.DataFrame: The joined DataFrame.
    """
    # Drop rows with None values in the key column
    df_eval = df_eval.dropna(subset=[key_col])
    df_explo = df_explo.dropna(subset=[key_col])

    # Select columns to keep
    cols_to_keep_eval = [key_col, 'Lot', 'Donnée environnementale (DE)', 'Quantité', 'GES_divided_by__SREF']
    cols_to_keep_explo = [key_col, 'Quantité', 'GES_divided_by__SREF']

    # Merge DataFrames on the key column
    merged_df = pd.merge(
        df_eval[cols_to_keep_eval], 
        df_explo[cols_to_keep_explo], 
        on=key_col, 
        suffixes=(suffix_eval, suffix_explo)
    )

    # Rename columns
    merged_df.rename(columns={
        f'Quantité{suffix_eval}': f'Quantité{suffix_eval}',
        f'Quantité{suffix_explo}': f'Quantité{suffix_explo}',
        f'GES_divided_by__SREF{suffix_eval}': f'GES_divided_by__SREF{suffix_eval}',
        f'GES_divided_by__SREF{suffix_explo}': f'GES_divided_by__SREF{suffix_explo}'
    }, inplace=True)

    return merged_df

