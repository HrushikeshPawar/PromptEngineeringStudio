import os
import sqlite3
import streamlit as st
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page
from code_editor import code_editor
from time import sleep

import sys
sys.path.append('../utils')

from utils.sql_helper import get_all_projects, create_prompt, get_prompt_details
from utils.helper import load_codeEditor_buttons_config, load_codeEditor_config, load_codeEditor_infobar_config, get_input_variables

from dotenv import load_dotenv
load_dotenv()

### IMPORTS END ###

## Setup the page
st.set_page_config(layout='wide')

# Set Connection to SQL Database and Create a cursor object
connection = sqlite3.connect(os.getenv('DB_PATH'))
cursor = connection.cursor()

# Hide Internal Pages
hide_pages(st.session_state['config']['hidden_pages'])


## Local Variables
if 'TEMPLATE_EDITOR_ID' not in st.session_state:
    st.session_state['TEMPLATE_EDITOR_ID'] = None

if 'INPUT_VARIABLES' not in st.session_state:
    st.session_state['INPUT_VARIABLES'] = []

if 'ALL_PROJECTS' not in st.session_state:
    st.session_state['ALL_PROJECTS'] = get_all_projects(cursor)

if 'OLD_PROMPT_INFO' not in st.session_state:
    st.session_state['OLD_PROMPT_INFO'] = get_prompt_details(cursor, st.session_state['CURRENT_PROMPT_ID'])


## Helper functions
# Delete local variables from st.session_state
def clean_session_state():
    st.session_state.pop('version')
    st.session_state.pop('parent')
    st.session_state.pop('input_variables')
    st.session_state.pop('add_to_favorites')
    st.session_state.pop('notes')
    st.session_state.pop('commit_button')
    st.session_state.pop('prompt_template_editor')
    st.session_state.pop('TEMPLATE_EDITOR_ID')
    st.session_state.pop('INPUT_VARIABLES')
    st.session_state.pop('OLD_PROMPT_INFO')
    st.session_state.pop('ALL_PROJECTS')


## HEADER
st.title('Prompt Engineering Studio')
st.header('', divider='rainbow')


## SUB-HEADERs
subheader_cols = st.columns(2)
with subheader_cols[0]:
    st.subheader(st.session_state['ALL_PROJECTS'][st.session_state['CURRENT_PROJECT_ID']]['name'])
    st.write(st.session_state['ALL_PROJECTS'][st.session_state['CURRENT_PROJECT_ID']]['description'])

with subheader_cols[1]:
    st.subheader(f'{st.session_state["OLD_PROMPT_INFO"]["name"]}')
    st.write(st.session_state['OLD_PROMPT_INFO']['description'] if st.session_state['OLD_PROMPT_INFO']['description'] is not None else '')
st.divider()


## Create or Load a Project
main_columns = st.columns([0.01, 0.64, 0.02, 0.33, 0.01])

# Prompt Setting Area
with main_columns[3]:

    # Version
    st.write('Version')
    st.number_input(
        label='Version',
        value=st.session_state['OLD_PROMPT_INFO']['version'] + 1,
        key='version',
        label_visibility='collapsed',
        disabled=True,
    )

    # Parent
    st.write('Parent')
    st.text_input(
        label='Parent',
        key='parent',
        value=st.session_state['OLD_PROMPT_INFO']['id'],
        placeholder='Enter a new parent',
        label_visibility='collapsed',
        disabled=True,
    )

    # Input Variables
    st.write('Input Variables')
    st.text_input(
        label='Input Variables',
        key='input_variables',
        placeholder='Enter input variables',
        label_visibility='collapsed',
        value=", ".join(st.session_state['INPUT_VARIABLES']),
        disabled=True,
    )

    # Add to favorites
    st.columns(3)[1].toggle('Add to favorites', key='add_to_favorites')

    # Notes
    st.write('Notes')
    st.text_area(
        label='Notes',
        key='notes',
        placeholder='Any notes related to this prompt',
        height=100,
        label_visibility='collapsed',
    )

    # Commit Button
    st.columns([0.1, 0.8, 0.1])[1].button(':green[Commit]', key='commit_button', use_container_width=True)

# Prompt Template Editor
with main_columns[1]:
    # The prompt template editor
    options = load_codeEditor_config()
    button_config = load_codeEditor_buttons_config()
    info_bar_options = load_codeEditor_infobar_config()
    
    info_bar_options['info'][0]['name'] = f"Prompt Template Editor | {st.session_state['ALL_PROJECTS'][st.session_state['CURRENT_PROJECT_ID']]['name']} | {st.session_state['OLD_PROMPT_INFO']['name']} | v{st.session_state['version']} |"

    st.warning('Once done with editing the template, click on the "Run" button on lower right corner of editor before "Create" button', icon='⚠️')
    st.info('Use :blue[Double Curly Braces] to insert input variables in the template - {{ variable }}', icon='ℹ️')
    prompt_template_editor = code_editor(
        code=st.session_state['OLD_PROMPT_INFO']['prompt_template'],
        options=options,
        height=[10, 100],
        lang='text',
        info=info_bar_options,
        buttons=button_config,
        allow_reset=True,
        key='prompt_template_editor',
    )

    if st.session_state['prompt_template_editor'] is not None:
        if 'id' in st.session_state['prompt_template_editor']:
            if st.session_state['TEMPLATE_EDITOR_ID'] != st.session_state['prompt_template_editor']['id']:
                st.session_state['INPUT_VARIABLES'] = get_input_variables(st.session_state['prompt_template_editor']['text'])
                st.session_state['TEMPLATE_EDITOR_ID'] = st.session_state['prompt_template_editor']['id']
                st.rerun()

# Commit Button
if st.session_state['commit_button']:
    create_prompt(
        project_id=st.session_state['CURRENT_PROJECT_ID'],
        prompt_name=st.session_state['OLD_PROMPT_INFO']["name"],
        parent_prompt_id=st.session_state['OLD_PROMPT_INFO']['id'],
        prompt_description=st.session_state['OLD_PROMPT_INFO']['description'] if len(st.session_state['OLD_PROMPT_INFO']['description'].strip()) > 0 else None,
        version=st.session_state['version'],
        prompt_template=st.session_state['prompt_template_editor']['text'],
        input_variables=", ".join(st.session_state['INPUT_VARIABLES']) if len(st.session_state['INPUT_VARIABLES']) > 0 else None,
        favourite=st.session_state['add_to_favorites'],
        notes=st.session_state['notes'] if len(st.session_state['notes'].strip()) > 0 else None,
        connection=connection,
        cursor=cursor,
    )
    st.success('New prompt version created successfully!')
    st.session_state['CURRENT_PROMPT_GROUP_ID'] = st.session_state['OLD_PROMPT_INFO']['prompt_group_id']
    sleep(1)
    clean_session_state()
    switch_page("show_prompt_versions")

st.divider()
button_cols = st.columns(5)
back_to_projects = button_cols[1].button(':leftwards_arrow_with_hook: Back to Projects', use_container_width=True)
back_to_current_project = button_cols[3].button(':leftwards_arrow_with_hook: Back to Current Project', use_container_width=True)


if back_to_projects:
    clean_session_state()
    switch_page("Projects")

if back_to_current_project:
    clean_session_state()
    switch_page("show_project")

st.divider()
with st.expander('Session State'):
    st.json(st.session_state, expanded=True)