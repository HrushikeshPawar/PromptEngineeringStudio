import os
import sqlite3
import streamlit as st
from st_pages import hide_pages
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page

import sys

sys.path.append('../utils')
from utils.sql_helper import get_prompt_group_details, get_all_projects, get_all_prompt_versions

from dotenv import load_dotenv
load_dotenv()
### IMPORTS END ###

# Setup the page
st.set_page_config(layout='wide')

# Set Connection to SQL Database and Create a cursor object
connection = sqlite3.connect(os.getenv('DB_PATH'))
cursor = connection.cursor()

# Hide Internal Pages
hide_pages(st.session_state['config']['hidden_pages'])


## Local Variables
if "SWITCH_TO_PROMPT_TESTING" not in st.session_state:
    st.session_state["SWITCH_TO_PROMPT_TESTING"] = False

if 'ALL_PROJECTS' not in st.session_state:
    st.session_state['ALL_PROJECTS'] = get_all_projects(cursor)
    
if 'CURRENT_PROMPT_GROUP_DETAILS' not in st.session_state:
    st.session_state['CURRENT_PROMPT_GROUP_DETAILS'] = get_prompt_group_details(cursor, st.session_state['CURRENT_PROMPT_GROUP_ID'])

if 'ALL_PROMPTS' not in st.session_state:
    st.session_state['ALL_PROMPTS'] = get_all_prompt_versions(cursor, st.session_state['CURRENT_PROMPT_GROUP_ID'])


# Get the Current Prompt Group Details
prompt_name, prompt_description = st.session_state['CURRENT_PROMPT_GROUP_DETAILS']

## Helper Functions
def go_to_playground(prompt_id: str):
    st.session_state['CURRENT_PROMPT_ID'] = prompt_id
    st.session_state["SWITCH_TO_PROMPT_TESTING"] = True

# Delete local variables from session state
def clean_session_state():

    for idx in st.session_state['ALL_PROMPTS'].index:
        st.session_state.pop(f'notes_{idx}')
        st.session_state.pop(f'fav_checkbox_{idx}')
        st.session_state.pop(f'playground_button_{idx}')

    st.session_state.pop("SWITCH_TO_PROMPT_TESTING")
    st.session_state.pop("ALL_PROMPTS")
    st.session_state.pop("CURRENT_PROMPT_GROUP_DETAILS")
    st.session_state.pop("ALL_PROJECTS")


## HEADER
st.title('Prompt Engineering Studio')
st.header('Projects', divider='rainbow')


## SUB-HEADERs
subheader_cols = st.columns(2)
with subheader_cols[0]:
    st.subheader(st.session_state['ALL_PROJECTS'][st.session_state['CURRENT_PROJECT_ID']]['name'])
    st.write(st.session_state['ALL_PROJECTS'][st.session_state['CURRENT_PROJECT_ID']]['description'])

with subheader_cols[1]:
    st.subheader(prompt_name)
    st.write(prompt_description)
st.divider()

## PROMPT VERSIONS
with st.columns([0.2, 0.6, 0.2])[1]:

    prompt_version_grid = grid([0.1, 0.2, 0.4, 0.1, 0.2], 1, *[[0.1, 0.2, 0.4, 0.1, 0.2] for _ in range(len(st.session_state['ALL_PROMPTS']))])
    
    # Header
    prompt_version_grid.text("Version")
    prompt_version_grid.text("Input Variables")
    prompt_version_grid.text("Notes")
    prompt_version_grid.text("Favourite")
    prompt_version_grid.text("Show Prompt")
    prompt_version_grid.divider()

    # For each prompt version
    for idx in st.session_state['ALL_PROMPTS'].index:
        prompt_version_grid.text(st.session_state['ALL_PROMPTS'].version[idx])
        prompt_version_grid.text(st.session_state['ALL_PROMPTS'].input_variables[idx])
        prompt_version_grid.text_area(label=f'label_{idx}', value=st.session_state['ALL_PROMPTS'].notes[idx], label_visibility='collapsed', disabled=True, key=f'notes_{idx}')
        prompt_version_grid.checkbox(label='Favourite', value=st.session_state['ALL_PROMPTS'].favourite[idx], label_visibility='hidden', disabled=True, key=f'fav_checkbox_{idx}')
        prompt_version_grid.button('Playground', on_click=go_to_playground, args=(st.session_state['ALL_PROMPTS'].id[idx],), key=f'playground_button_{idx}')

# Switch if Playground is clicked
if st.session_state["SWITCH_TO_PROMPT_TESTING"]:
    clean_session_state()
    switch_page("prompt_version_testing")

st.divider()
button_cols = st.columns(5)
back_to_projects = button_cols[1].button(':leftwards_arrow_with_hook: Back to Projects', use_container_width=True)
update_project = button_cols[3].button(':pencil2: Update Project', use_container_width=True)

if back_to_projects:
    clean_session_state()
    switch_page("Projects")

if update_project:
    clean_session_state()
    switch_page("update_project")

st.divider()
with st.expander('Session State'):
    st.json(st.session_state, expanded=True)
