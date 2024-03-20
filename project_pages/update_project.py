import os
import streamlit as st
import sqlite3
from time import sleep
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page

import sys

sys.path.append('../utils')
from utils.sql_helper import get_all_projects, update_project

from dotenv import load_dotenv
load_dotenv()
### IMPORTS END ###

if 'config' not in st.session_state:
    switch_page("home")

# Setup the page
st.set_page_config(layout='centered')

# Set Connection to SQL Database and Create a cursor object
connection = sqlite3.connect(os.getenv('DB_PATH'))
cursor = connection.cursor()

# Hide Internal Pages
hide_pages(st.session_state['config']['hidden_pages'])

# Get the Current Project Details
all_projects = get_all_projects(cursor)

st.title('Prompt Engineering Studio')
st.header('Projects', divider='rainbow')
st.subheader('Update Project')

with st.form(key='create_project_form'):
    project_name = st.text_input('Name :red[*]', placeholder='Project Name', value=all_projects[st.session_state['CURRENT_PROJECT_ID']]['name'])
    project_description = st.text_area('Description', placeholder='Short description of the project', value=all_projects[st.session_state['CURRENT_PROJECT_ID']]['description'])
    submit_button = st.columns(3)[1].form_submit_button(label='Update Project', use_container_width=True)

if submit_button:
    
    if project_name.strip() == '':
        st.error('Project Name cannot be empty!')
    else:
        update_project(st.session_state['CURRENT_PROJECT_ID'], project_name, project_description, connection, cursor)
        st.success('Project Updated Successfully!')
        sleep(1)
        switch_page("show_project")

st.divider()
button_cols = st.columns(3)
back_to_projects = button_cols[0].button(':leftwards_arrow_with_hook: Back to Projects', use_container_width=True)
back_to_current_project = button_cols[2].button(':leftwards_arrow_with_hook: Back to Current Project', use_container_width=True)

if back_to_projects:
    switch_page("Projects")

if back_to_current_project:
    switch_page("show_project")

st.divider()
with st.expander('Session State'):
    st.json(st.session_state, expanded=True)