import streamlit as st
from app.content import sidebar_choices

# Sidebar for navigation


def test_choice():
    st.sidebar.title("Sommaire")
    choice = sidebar_choices
    sidebar_choice = st.sidebar.radio("Aller vers la page", choice)

    return sidebar_choice




