import streamlit as st
import pandas as pd
from io import StringIO

#upload xlsx files
from app.projet_comparaison.upload_excel import upload_explo, upload_eval
#sidebar
from utility_functions import run_script, sort_alfanumeric
from app.sidebar_structure import test_choice
#analysis
from analysis.data_cleaning import clean_join_df, join_dataframes, group_and_aggregate
from analysis.transform import group_and_calculate_percentage, group_and_calculate_percentage_with_names, join_and_rename_columns, group_and_get_filtered_max_value, group_and_get_filtered_min_value, join_dataframes_jaro,filter_dataframes_jaro, get_combined_total_ges, sum_top_n_elements, find_sref_batiment_and_next, change_column_if_not_in_list
from analysis.data_viz import transform_and_plot_stacked_bar, transform_and_plot_stacked_bar_lot_et_slot, plot_butterfly_chart, plot_bar_chart_h
# run_script("sidebar/sidebar_structure.py")

choice = test_choice()


if choice == "Acceuil":
    run_script("app/acceuil.py")
elif choice == "Projets comparaison":
    tab1, tab2= st.tabs(["Upload two xlsx files from VIZCAB", "Results, key metrics and comparation of projets"])

    with tab1:

        # st.header("🤖")
        with st.container(border=True) :

            df_eval, df_eval_contributeurs, eval_sref = upload_eval()
            df_explo, df_explo_contributeurs, explo_sref = upload_explo()
            

        with st.container(border=True) :

            if df_eval is not None and df_explo is not None:

                eval_sref = find_sref_batiment_and_next(eval_sref, 5) #get sref from a df on a specifque place from df
                explo_sref = find_sref_batiment_and_next(explo_sref, 2) #get sref from a df
                df_eval = clean_join_df(df_eval, df_eval_contributeurs, eval_sref)
                df_explo = clean_join_df(df_explo, df_explo_contributeurs, explo_sref)

                info_checkbox = st.checkbox("💡 Here you can see and download the data we use from the xlsx you uploaded. As long as you uploaded the EVAL and the EXPLO files at the right place.")
                if info_checkbox:
                    st.write("EVAL csv")
                    st.write(df_eval)

                    st.write("EXPLO csv")
                    st.write(df_explo)
            else:
                st.write("Please upload both files to start the analyse ")

    with tab2:
        
        if df_eval is not None and df_explo is not None:

            with st.container(border=True):



                lots_eval = group_and_calculate_percentage(df_eval, 'Lot', 'GES_divided_by__SREF')
                lots_explo = group_and_calculate_percentage(df_explo, 'Lot', 'GES_divided_by__SREF')
                lots_eval_explo = join_and_rename_columns(lots_eval, lots_explo)

                #creation of the multiselec for filtering
                options = lots_eval_explo['Lot'].unique()
                default_options = [ 'Lot 1 Voirie et Réseaux divers','Lot 10 Réseaux énergie - courant fort', 'Lot 11 Réseaux de communication - courant faible', 'Contributeur Chantier']
                selected_options = st.multiselect('Selected lots to NOT show on stacked barplot',options, default=default_options)

                #filtering df with multiselect choice

                filtered_lots_eval_explo = lots_eval_explo[~lots_eval_explo['Lot'].isin(selected_options)]



                #Making the stacked barplot from the choices
                transform_and_plot_stacked_bar(filtered_lots_eval_explo, 'Lot', ['eval', 'explo'])

            jaro_join_df = group_and_aggregate(join_dataframes_jaro(df_eval, df_explo))


            #set number of top fiches
            with st.container(border=True) :
                select_top_fiches = [10, 15, 20, 25]
                # Set the initial option as a string value
                initial_option = select_top_fiches[0]
                # Create the select box with the initial option set by value
                selected_option_top_fiches_ = st.selectbox("Show number of top fiches that are equal or different between projets?", select_top_fiches, index=select_top_fiches.index(initial_option))

                temp1 = get_combined_total_ges(df_eval, df_explo)
                temp2 = sum_top_n_elements(jaro_join_df, 'GES_divided_by__SREF_eval', selected_option_top_fiches_)
                temp3 = temp2 = sum_top_n_elements(jaro_join_df, 'GES_divided_by__SREF_explo', selected_option_top_fiches_)
                pourcentage = round((temp3/temp1*100),2)

    
                st.write(f"The top {selected_option_top_fiches_} explain {pourcentage} % of the total of the same composants in both projets")
                st.write("We calculated it by summing total ic_composant on both proyects, and dividing by the sum of the Top n fiches that can be found on both projets")

            #BUTTERFLY CHART FOR TOP FICHES
              
            # top_fiches_alike = plot_butterfly_chart(jaro_join_df, top_n=selected_option_top_fiches_)
            info_checkbox_ = st.checkbox("💡 Table with the components in EVAL AND EXPLO")
            if info_checkbox_:
                st.write(jaro_join_df)


            #BAR CHART FOR TOP FICHES THAT ARE NOT THE SAME
            col1, col2 = st.columns(2)
            with col1:
                jaro_not_same_eval = filter_dataframes_jaro(df_eval, df_explo, key_col='Donnée environnementale (DE)')
                top_fiched_not_alike = plot_bar_chart_h(jaro_not_same_eval, column='GES_divided_by__SREF', lot_col='Lot', top_n=selected_option_top_fiches_, group_n_sorted = 'Donnée environnementale (DE)')
                info_checkbox_eval = st.checkbox("💡 Table with the components in EVAL but not in EXPLO")
                if info_checkbox_eval:
                    st.write(jaro_not_same_eval)
            with col2:
                jaro_not_same_explo = filter_dataframes_jaro(df_explo, df_eval, key_col='Donnée environnementale (DE)')
                top_fiched_not_alike = plot_bar_chart_h(jaro_not_same_explo, column='GES_divided_by__SREF', lot_col='Lot', top_n=selected_option_top_fiches_, group_n_sorted = 'Donnée environnementale (DE)')
                info_checkbox_explo = st.checkbox("💡 Table with the components in EXPLO but not in EVAL")
                if info_checkbox_explo:
                    st.write(jaro_not_same_explo)

            with st.container(border=True) :
            
                #LOT STACKED BARS ------------------------- Hacer esto un py file o muchas funciones para reutilizar en sous-lots
                #CODIGO COMPLICADO BECAUSE SELECT NEEDS AN INTEGER AS DEFAULT PARAMETER INSTEAD OF STRNGS LIKE MULTISELEC
                #creation of select for lot
                select_options = (df_explo['Lot'].unique())
                # Set the initial option as a string value
                initial_option = 'Lot 3 Superstructure - Maçonnerie'
                # Create the select box with the initial option set by value
                selected_option = st.selectbox("Select a Lot", select_options, index=select_options.tolist().index(initial_option))
                
                #
                sous_lot_eval = group_and_calculate_percentage(df_eval, 'Sous-lot', 'GES_divided_by__SREF', 'Lot')
                sous_lot_explo = group_and_calculate_percentage(df_explo, 'Sous-lot', 'GES_divided_by__SREF', 'Lot')
                sous_lots_eval_explo = join_and_rename_columns(sous_lot_eval, sous_lot_explo, 'Sous-lot')
                              
                #

                # Convert the selected option to a list
                selected_option_list = [selected_option]
                #getting max values of lots for the y axis scale
            

                # filtered_exploration_eval = df_eval[df_eval['Lot'].isin(selected_option_list)]
                # filtered_exploration_explo = df_explo[df_explo['Lot'].isin(selected_option_list)]

                #

                #
                    #
                

                
                # filtered_sous_lots_eval_explo = sous_lots_eval_explo[sous_lots_eval_explo['Lot_x'].isin(selected_option_list)]
                filtered_sous_lots_eval_explo = sous_lots_eval_explo[
                    (sous_lots_eval_explo['Lot_x'].isin(selected_option_list)) |
                    (sous_lots_eval_explo['Lot_y'].isin(selected_option_list))
                ]



                st.write(sous_lots_eval_explo)
                #Making the stacked barplot from the choices
                transform_and_plot_stacked_bar(filtered_sous_lots_eval_explo, 'Sous-lot', ['eval', 'explo'], color_palette='Vivid')
                
                # test = lots_eval_explo[~lots_eval_explo['Sous-lot'].isin(selected_options)]
                # st.write
                #
                #

                #

                # col1, col2 = st.columns(2)

                # with col1:
                #     st.write("EVAL exploration")

                #     exploration_lots_eval = group_and_calculate_percentage_with_names(filtered_exploration_eval, 'Sous-lot', 'GES_divided_by__SREF')
                    
                #     #Making the stacked barplot from the choices
                #     filtered_exploration_lots_eval = group_and_calculate_percentage(exploration_lots_eval, 'Sous-lot', 'GES_divided_by__SREF')
                #     transform_and_plot_stacked_bar_lot_et_slot(filtered_exploration_lots_eval, 'Sous-lot', ['GES_divided_by__SREF'], [0, y_axis_lots])


                



                # with col2:
                #     st.write("EXPLO exploration")
                #     exploration_lots_explo = group_and_calculate_percentage_with_names(filtered_exploration_explo, 'Sous-lot', 'GES_divided_by__SREF')
                    
                #     #Making the stacked barplot from the choices
                #     filtered_exploration_lots_explo = group_and_calculate_percentage(exploration_lots_explo, 'Sous-lot', 'GES_divided_by__SREF')
                #     transform_and_plot_stacked_bar_lot_et_slot(filtered_exploration_lots_explo, 'Sous-lot', ['GES_divided_by__SREF'], [0, y_axis_lots])
                
                #LOT STACKED BARS ------------------------- Hacer esto un py file o muchas funciones para reutilizar en sous-lots
                #creation of select for lot
                composants_select_options = (filtered_sous_lots_eval_explo['Sous-lot'].unique())
                # Set the initial option as a string value
                initial_option = composants_select_options[0]
                # Create the select box with the initial option set by value
                composants_selected_option = st.selectbox("Select a Sous-lot", composants_select_options, index=composants_select_options.tolist().index(initial_option))

                # Convert the selected option to a list
                composants_selected_option_list = [composants_selected_option]


                #
                # group_and_calculate_percentage_with_names(df, group_by_col, sum_col, names_col1='Donnée environnementale (DE)', names_col2='Lot')
                #
                composants_eval = group_and_calculate_percentage_with_names(df_eval, 'Donnée environnementale (DE)', 'GES_divided_by__SREF', 'Sous-lot')
                composants_explo = group_and_calculate_percentage_with_names(df_explo, 'Donnée environnementale (DE)', 'GES_divided_by__SREF', 'Sous-lot')
                composants_eval_explo = join_and_rename_columns(composants_eval, composants_explo, 'Donnée environnementale (DE)')
                              
                #

                #

                #
                    #
                

                # filtered_composants_eval_explo = composants_eval_explo[composants_eval_explo['Sous-lot_x'].isin(selected_option_list)]
                filtered_composants_eval_explo = composants_eval_explo[
                    (composants_eval_explo['Sous-lot_x'].isin(composants_selected_option_list)) |
                    (composants_eval_explo['Sous-lot_y'].isin(composants_selected_option_list))
                ]

                #Making the stacked barplot from the choices
                filtered_composants_eval_explo = change_column_if_not_in_list(filtered_composants_eval_explo, 'Sous-lot_x', composants_selected_option_list, 'eval')
                filtered_composants_eval_explo = change_column_if_not_in_list(filtered_composants_eval_explo, 'Sous-lot_y', composants_selected_option_list, 'explo')

                # st.write(filtered_composants_eval_explo)
                # st.write(test2)
                transform_and_plot_stacked_bar(filtered_composants_eval_explo, 'Donnée environnementale (DE)', ['eval', 'explo'], color_palette='Vivid')
                

                #



                #getting max values of lots for the y axis scale 

                # sous_lot_max_eval = group_and_get_filtered_max_value(df_eval, 'Sous-lot', 'GES_divided_by__SREF', sous_lot_selected_option)
                # sous_lot_max_explo = group_and_get_filtered_max_value(df_explo, 'Sous-lot', 'GES_divided_by__SREF', sous_lot_selected_option)
                # y_axis_sous_lots = round(max(sous_lot_max_eval, sous_lot_max_explo)*1.2,0)

                # #getting min values
                # # st.write(sous_lot_selected_option)
                # sous_lot_min_eval = group_and_get_filtered_min_value(df_eval, 'Sous-lot','Donnée environnementale (DE)', 'GES_divided_by__SREF', sous_lot_selected_option)
                # sous_lot_min_explo = group_and_get_filtered_min_value(df_explo, 'Sous-lot', 'Donnée environnementale (DE)','GES_divided_by__SREF', sous_lot_selected_option)
                # y_axis_min_sous_lots = round(min(sous_lot_min_eval, sous_lot_min_explo)*1.1,0)

                # sous_lot_filtered_exploration_eval = filtered_exploration_eval[filtered_exploration_eval['Sous-lot'].isin(sous_lot_selected_option_list)]
                # sous_lot_filtered_exploration_explo = filtered_exploration_explo[filtered_exploration_explo['Sous-lot'].isin(sous_lot_selected_option_list)]

                # col1, col2 = st.columns(2)

                # with col1:
                #     st.write("EVAL sous-lot exploration")
                #     exploration_sous_lots_eval = group_and_calculate_percentage_with_names(sous_lot_filtered_exploration_eval, 'Sous-lot', 'GES_divided_by__SREF')
                    
                #     #Making the stacked barplot from the choices
                #     sous_lot_filtered_exploration_eval = group_and_calculate_percentage(sous_lot_filtered_exploration_eval, 'Donnée environnementale (DE)', 'GES_divided_by__SREF')
                #     max_value = round(sous_lot_filtered_exploration_eval.GES_divided_by__SREF.sum(),2)
                #     transform_and_plot_stacked_bar_lot_et_slot(sous_lot_filtered_exploration_eval, 'Donnée environnementale (DE)', ['GES_divided_by__SREF'], [y_axis_min_sous_lots, y_axis_sous_lots])
                
                # with col2:
                #     st.write("EXPLO sous-lot  exploration")
                #     exploration_sous_lots_explo = group_and_calculate_percentage_with_names(sous_lot_filtered_exploration_explo, 'Sous-lot', 'GES_divided_by__SREF')
                    
                #     #Making the stacked barplot from the choices
                #     sous_lot_filtered_exploration_explo = group_and_calculate_percentage(sous_lot_filtered_exploration_explo, 'Donnée environnementale (DE)', 'GES_divided_by__SREF')
                #     max_value = round(sous_lot_filtered_exploration_explo.GES_divided_by__SREF.sum(),2)
                #     transform_and_plot_stacked_bar_lot_et_slot(sous_lot_filtered_exploration_explo, 'Donnée environnementale (DE)', ['GES_divided_by__SREF'], [y_axis_min_sous_lots, y_axis_sous_lots])


        else:
                st.write("Dont jump the line 😾💢 ! Please upload both files to start the analyse ")


        
        





    


