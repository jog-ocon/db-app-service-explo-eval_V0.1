import streamlit as st
import pandas as pd



def upload_eval():

    uploaded_file_eval = st.file_uploader(":pear: Drop EVAL file here", type='xlsx')
    if uploaded_file_eval is not None:

        # Can be used wherever a "file-like" object is accepted:
        # dataframe = pd.read_csv(uploaded_file)
        df_eval = pd.read_excel(uploaded_file_eval, sheet_name = 1, header = 2, dtype={'ID-DE': str})
        df_contributeurs_eval = pd.read_excel(uploaded_file_eval, sheet_name = 5, header = 2)
        df_eval['ID-DE'] = df_eval['ID-DE'].astype('object') #no se ve asi en streamlit pero si funciona
        sref_eval = pd.read_excel(uploaded_file_eval, sheet_name = 0)
        st.success("Excel uploaded successfully :tada:")
        return df_eval, df_contributeurs_eval, sref_eval
    else:
        return None, None, None
    

def upload_explo():
    uploaded_file_explo = st.file_uploader(":fish: Drop EXPLO file here", type='xlsx')
    if uploaded_file_explo is not None:

        # Can be used wherever a "file-like" object is accepted:
        # dataframe = pd.read_csv(uploaded_file)
        df_explo = pd.read_excel(uploaded_file_explo, sheet_name = 2, header = 2)
        df_contributeurs_explo = pd.read_excel(uploaded_file_explo, sheet_name = 6, header = 2)
        sref_explo = pd.read_excel(uploaded_file_explo, sheet_name = 0)
        st.success("OMG you should ask for a raise :clap:")
        return df_explo, df_contributeurs_explo, sref_explo
    else:
        return None, None, None