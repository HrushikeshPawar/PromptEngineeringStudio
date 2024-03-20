import os
import streamlit as st
import sqlite3
from time import sleep
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page

import sys

sys.path.append('../utils')
from utils.sql_helper import create_project, ProjectAlreadyExistsError

from dotenv import load_dotenv
load_dotenv()

if 'config' not in st.session_state:
    switch_page("home")

# Set Connection to SQL Database and Create a cursor object
connection = sqlite3.connect(os.getenv('DB_PATH'))
cursor = connection.cursor()

# Hide Internal Pages
hide_pages(st.session_state['config']['hidden_pages'])

st.session_state['create_project_card'] = None

st.title('Prompt Engineering Studio')
st.header('Projects', divider='rainbow')
st.subheader('Create New Project')

with st.form(key='create_project_form'):
    project_name = st.text_input('Name :red[*]', placeholder='Project Name')
    project_description = st.text_area('Description', placeholder='Short description of the project')
    submit_button = st.columns(3)[1].form_submit_button(label='Create Project', use_container_width=True)

if submit_button:
    
    if project_name.strip() == '':
        st.error('Project Name cannot be empty!')
    else:
        try:
            create_project(project_name, connection, cursor, project_description)
            st.success('Project Created Successfully!')
            sleep(1)
            switch_page("Projects")
            
        except ProjectAlreadyExistsError:
            st.error('Project with that name already exists!')

st.divider()
back_to_projects = st.columns(3)[1].button(':leftwards_arrow_with_hook: Back to Projects', use_container_width=True)

if back_to_projects:
    switch_page("Projects")

st.divider()
with st.expander('Session State'):
    st.json(st.session_state, expanded=True)