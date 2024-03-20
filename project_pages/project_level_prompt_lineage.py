import os
import sqlite3
import streamlit as st
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page

import sys

sys.path.append('../utils')
from utils.sql_helper import get_all_prompts, get_all_projects
from utils.helper import project_level_prompt_lineage

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

## Helper functions
# Delete local variables from st.session_state
def clean_session_state():
    st.session_state.pop('PROJECTS')
    st.session_state.pop('PROMPTS')

if 'PROJECTS' not in st.session_state:
    st.session_state['PROJECTS'] = get_all_projects(cursor)

if 'PROMPTS' not in st.session_state:
    st.session_state['PROMPTS'] = get_all_prompts(cursor, st.session_state['CURRENT_PROJECT_ID'], output_type='df')


## HEADER
st.title('Prompt Engineering Studio')
st.header('Projects', divider='rainbow')
st.subheader(st.session_state['PROJECTS'][st.session_state['CURRENT_PROJECT_ID']]['name'])
st.write(st.session_state['PROJECTS'][st.session_state['CURRENT_PROJECT_ID']]['description'])
st.divider()

cols = st.columns([.2, .6, .2])
with cols[1]:
    
    # Create Lineage Graph
    with st.spinner('Creating Lineage Graph...'):
        lineage_graph = project_level_prompt_lineage(st.session_state['PROMPTS'])
    
    # Render Lineage Graph
    st.graphviz_chart(lineage_graph, use_container_width=True)
    

## FOOTER
st.divider()
button_cols = st.columns(3)
back_to_projects = button_cols[0].button(':leftwards_arrow_with_hook: Back to Projects', use_container_width=True)
back_to_current_project = button_cols[2].button(':leftwards_arrow_with_hook: Back to Current Project', use_container_width=True)

if back_to_projects:
    clean_session_state()
    switch_page("Projects")

if back_to_current_project:
    clean_session_state()
    switch_page("show_project")

st.divider()
with st.expander('Session State'):
    st.json(st.session_state, expanded=True)