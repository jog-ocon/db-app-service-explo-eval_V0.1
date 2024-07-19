import pandas as pd
import streamlit as st
import numpy as np

import plotly.express as px
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import seaborn as sns
import plotly.graph_objs as go


from utility_functions import wrap_labels, count_repeated_elements

def transform_and_plot_stacked_bar(df, lot_col, value_cols, y_axis_range=None):
    """
    Transforms the DataFrame and creates stacked bar plots using Plotly.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    lot_col (str): The name of the lot column.
    value_cols (list): A list of column names to plot.
    y_axis_range (list, optional): A list containing the min and max values for the y-axis.
    """
    # Initialize an empty DataFrame for the transformed data
    transformed_data = {'type_prod': []}

    for value_col in value_cols:
        # Transform the DataFrame for each value column
        df_transformed = df[[lot_col, value_col]].set_index(lot_col).T
        df_transformed.insert(0, 'type_prod', value_col)
        
        # Append the transformed data to the main DataFrame
        transformed_data['type_prod'].append(value_col)
        for col in df_transformed.columns[1:]:
            if col not in transformed_data:
                transformed_data[col] = []
            transformed_data[col].append(df_transformed[col].values[0])

    df_transformed_final = pd.DataFrame(transformed_data)

    # Melt the DataFrame to long format for Plotly
    df_melted = df_transformed_final.melt(id_vars='type_prod', var_name='Lot', value_name='Value')


    # Create a stacked bar plot using Plotly
    fig = px.bar(df_melted, x='type_prod', y='Value', color='Lot', color_discrete_sequence=px.colors.qualitative.Antique,
                #  title='GES resultats comparaisons',
                 labels={'Value': 'kg éq. CO2/m²', 'type_prod': ''},
                 height=900)
    
   # Calculate totals for each type_prod
    totals = df_melted.groupby('type_prod')['Value'].sum().reset_index()
    totals['Value'] = totals['Value'].round(2)

    # Determine the maximum y value for adjusting annotation positions
    max_y_value = df_melted['Value'].max()
    y_offset = max_y_value * 0.07  # Adjust this multiplier as needed to avoid cutting

    # Add annotations for the totals with enhanced style
    for i in range(len(totals)):
        fig.add_annotation(
            x=totals['type_prod'][i],  # Annotation x-position
            y=totals['Value'][i] + y_offset,  # Annotation y-position above the bar to avoid cutting
            text=f"{totals['Value'][i]} kg éq. CO2/m²",  # Text with unit
            showarrow=False,  # No arrow
            font=dict(size=12, color='black'),  # Font size and color
            bgcolor='white',  # Background color
            bordercolor='white',  # Border color
            borderwidth=1,  # Border width
            borderpad=4,  # Padding around the text
            align='center'  # Center align text
        )
    
    # Update y-axis range if provided
    if y_axis_range:
        fig.update_yaxes(range=y_axis_range)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="left",
            x=0,
            itemsizing='constant'
        )  
    )

    fig.update_traces(marker_line_color='white', marker_line_width=0.5)


    # Display the plot in Streamlit
    st.plotly_chart(fig, theme="streamlit", use_container_width=True )


def transform_and_plot_stacked_bar_lot_et_slot(df, lot_col, value_cols, y_axis_range=None):
    """
    Transforms the DataFrame and creates stacked bar plots using Plotly.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    lot_col (str): The name of the lot column.
    value_cols (list): A list of column names to plot.
    y_axis_range (list, optional): A list containing the min and max values for the y-axis.
    """
    # Initialize an empty DataFrame for the transformed data
    transformed_data = {'type_prod': []}

    for value_col in value_cols:
        # Transform the DataFrame for each value column
        df_transformed = df[[lot_col, value_col]].set_index(lot_col).T
        df_transformed.insert(0, 'type_prod', value_col)
        
        # Append the transformed data to the main DataFrame
        transformed_data['type_prod'].append(value_col)
        for col in df_transformed.columns[1:]:
            if col not in transformed_data:
                transformed_data[col] = []
            transformed_data[col].append(df_transformed[col].values[0])

    df_transformed_final = pd.DataFrame(transformed_data)

    # Melt the DataFrame to long format for Plotly
    df_melted = df_transformed_final.melt(id_vars='type_prod', var_name='Lot', value_name='Value')


    # Create a stacked bar plot using Plotly
    fig = px.bar(df_melted, x='type_prod', y='Value', color='Lot', color_discrete_sequence=px.colors.qualitative.Vivid,
                #  title='GES resultats comparaisons',
                 labels={'Value': 'kg éq. CO2/m²', 'type_prod': ''},
                 height=600)
    
   # Calculate totals for each type_prod
    totals = df_melted.groupby('type_prod')['Value'].sum().reset_index()
    totals['Value'] = totals['Value'].round(2)

    # Determine the maximum y value for adjusting annotation positions
    max_y_value = df_melted['Value'].max()
    y_offset = max_y_value * 0.11  # Adjust this multiplier as needed to avoid cutting

    # Add annotations for the totals with enhanced style
    for i in range(len(totals)):
        fig.add_annotation(
            x=totals['type_prod'][i],  # Annotation x-position
            y=totals['Value'][i] + y_offset,  # Annotation y-position above the bar to avoid cutting
            text=f"{totals['Value'][i]} kg éq. CO2/m²",  # Text with unit
            showarrow=False,  # No arrow
            font=dict(size=12, color='black'),  # Font size and color
            bgcolor='white',  # Background color
            bordercolor='white',  # Border color
            borderwidth=1,  # Border width
            borderpad=4,  # Padding around the text
            align='center'  # Center align text
        )
    
    # Update y-axis range if provided
    if y_axis_range:
        fig.update_yaxes(range=y_axis_range)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="auto",
            y=-0.65,
            xanchor="left",
            x=0,
            itemsizing='constant'
        )  
    )

    fig.update_traces(marker_line_color='white', marker_line_width=0.3)


    # Display the plot in Streamlit
    st.plotly_chart(fig, theme="streamlit", use_container_width=True )

def plot_butterfly_chart(df, lot_eval_col='Lot_eval', lot_explo_col='Lot_explo', top_n=10):
    """
    Plots a butterfly chart from the given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data.
    lot_eval_col (str): Column name for lot_eval.
    lot_explo_col (str): Column name for lot_explo.
    top_n (int): Number of top items to display. Default is 10.
    """
# Handle NaN and infinite values
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['GES_divided_by__SREF_eval', 'GES_divided_by__SREF_explo'])

    # Sort and select top_n items based on GES_divided_by__SREF_eval + GES_divided_by__SREF_explo
    df['Impact'] = df['GES_divided_by__SREF_eval'] + df['GES_divided_by__SREF_explo']
    df = df.sort_values(by='Impact', ascending=False).head(top_n)

    # Prepare data for butterfly chart
    y = df['Donnée environnementale (DE)_eval']
    x1 = df['GES_divided_by__SREF_eval']
    x2 = -df['GES_divided_by__SREF_explo'].apply(lambda x: abs(x) if x > 0 else x)

    # Determine tick values
    max_x = 1 #max(max(x1), max(abs(x2)))
    tickvals = list(range(-int(max_x // 15) * 15, int(max_x // 15) * 15 + 11, 15))
    tickvals = sorted(list(set(tickvals + [-max_x, 0, max_x])))

    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=y,
        x=x1,
        name='Eval',
        orientation='h',
        marker=dict(color='rgb(55, 83, 109)'),
        hovertemplate='%{x}<br>%{y}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        y=y,
        x=x2,
        name='Explo',
        orientation='h',
        marker=dict(color='rgb(26, 118, 255)'),
        hovertemplate='%{customdata}<br>%{y}<extra></extra>',
        customdata=df['GES_divided_by__SREF_explo']
    ))

    # Update layout
    fig.update_layout(
        xaxis=dict(
            title='GES divided by SREF',
            titlefont_size=16,
            tickfont_size=14,
            # tickvals=[-max(abs(x2)), 0, max(x1)],
            # ticktext=[f'{max(abs(x2))}', '0', f'{max(x1)}'],
            tickvals=tickvals,
            ticktext=[str(abs(t)) for t in tickvals],
            showgrid=True, gridcolor='lightgrey'
        ),
        yaxis=dict(
            title='Donnée environnementale (DE)',
            titlefont_size=16,
            tickfont_size=14,
            showticklabels=False 
        ),
        barmode='overlay',
        bargap=0.15,
        bargroupgap=0.1,
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        )
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="left",
            x=0,
            itemsizing='constant'
        )  
    )

    fig.update_traces(marker_line_color='white', marker_line_width=0.5)

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def plot_bar_chart_h(df, column='GES_divided_by__SREF_eval', lot_col='Lot_eval', top_n=10, group_n_sorted = 'Donnée environnementale (DE)_eval'):
    # Aggregate values based on 'Donnée environnementale (DE)_eval'
    df_aggregated = df.groupby([group_n_sorted, lot_col])[column].sum().reset_index()
    #this is to correctly sort stacked barplots by eliminating repeated lots
    # num_repeated_elements = count_repeated_elements(df, group_n_sorted, lot_col)
    
    # Sort and select top_n items
    df_sorted = df_aggregated.sort_values(by=column, ascending=False).head(top_n).reset_index(drop=True)
    df_temp = df_sorted.drop_duplicates(subset='Donnée environnementale (DE)', keep='first')
    category_orders = {group_n_sorted: df_temp[group_n_sorted].tolist()}

    # Create figure
    fig = px.bar(
        df_sorted,
        x=column,
        y=group_n_sorted,
        color=lot_col,
        orientation='h',
        labels={column: 'kg éq. CO2/m²Sref', group_n_sorted: ''},
        height=600,
        category_orders=category_orders
    )

    fig.update_layout(
        title='',
        xaxis_title='kg éq. CO2/m²Sref',
        yaxis_title='',
        yaxis=dict(showticklabels=False),
        xaxis=dict(showgrid=True, gridcolor='lightgrey'),
        showlegend=True,
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.55,
            xanchor="left",
            x=0,
            itemsizing='constant'
        )  
    )

    fig.update_traces(marker_line_color='white', marker_line_width=0.5)

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)