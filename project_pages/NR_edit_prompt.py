import os
import sqlite3
import streamlit as st
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page
from code_editor import code_editor
from time import sleep

import sys

sys.path.append('../utils')
from utils.sql_helper import get_all_projects, get_all_prompts, update_prompt
from utils.helper import load_codeEditor_buttons_config, load_codeEditor_config, load_codeEditor_infobar_config, get_input_variables

from dotenv import load_dotenv
load_dotenv()
### IMPORTS END ###

# Setup the page
st.set_page_config(layout='wide')

# Set Connection to SQL Database and Create a cursor object
connection = sqlite3.connect(os.getenv('DB_PATH'))
cursor = connection.cursor()

# # Hide Internal Pages
hide_pages(st.session_state['config']['hidden_pages'])

all_projects = get_all_projects(cursor)
all_prompts = get_all_prompts(cursor, st.session_state['CURRENT_PROJECT_ID'])
st.title('Prompt Engineering Studio')
st.header('', divider='rainbow')

subheader_cols = st.columns(2)
with subheader_cols[0]:
    st.subheader(all_projects[st.session_state['CURRENT_PROJECT_ID']]['name'])
    st.write(all_projects[st.session_state['CURRENT_PROJECT_ID']]['description'])

with subheader_cols[1]:
    st.subheader(f"{all_prompts[st.session_state['current_prompt_id']]['name']} `v{all_prompts[st.session_state['current_prompt_id']]['version']}`")
    st.write(all_prompts[st.session_state['current_prompt_id']]['description'])

st.divider()

## Create or Load a Project
main_columns = st.columns([0.01, 0.64, 0.02, 0.33, 0.01])

# Prompt Setting Area
with main_columns[3]:

    # Parent
    st.write('Parent')
    st.text_input(
        label='Parent',
        key='parent',
        placeholder='Enter a new parent',
        label_visibility='collapsed',
        disabled=True,
        value=all_prompts[st.session_state['current_prompt_id']]['parent_prompt_id'],
    )

    # Input Variables
    st.write('Input Variables')
    st.text_input(
        label='Input Variables',
        key='input_variables',
        placeholder='Enter input variables',
        label_visibility='collapsed',
        value=all_prompts[st.session_state['current_prompt_id']]['input_variables'],
        disabled=True,
    )

    # # Add to favorites
    # st.columns(3)[1].toggle('Add to favorites', key='add_to_favorites')

    # Notes
    st.write('Notes')
    st.text_area(
        label='Notes',
        key='notes',
        value=all_prompts[st.session_state['current_prompt_id']]['notes'],
        placeholder='Any notes related to this prompt',
        height=100,
        label_visibility='collapsed',
    )

    # Update Notes Button
    st.columns([0.1, 0.8, 0.1])[1].button(':green[Update Notes]', key='update_notes_button', use_container_width=True)
    if st.session_state['update_notes_button']:
        update_prompt(
            prompt_id=st.session_state['current_prompt_id'],
            prompt_name=all_prompts[st.session_state['current_prompt_id']]['name'],
            prompt_description=all_prompts[st.session_state['current_prompt_id']]['description'],
            version=all_prompts[st.session_state['current_prompt_id']]['version'],
            prompt_template=all_prompts[st.session_state['current_prompt_id']]['prompt_template'],
            input_variables=all_prompts[st.session_state['current_prompt_id']]['input_variables'],
            favourite=all_prompts[st.session_state['current_prompt_id']]['favourite'],
            notes=st.session_state['notes'] if len(st.session_state['notes'].strip()) > 0 else None,
            connection=connection,
            cursor=cursor,
        )
        st.success('Prompt Created Successfully!')
        sleep(1)
        st.rerun()

# Prompt Template Editor
with main_columns[1]:
    # The prompt template editor
    options = load_codeEditor_config()
    options['readOnly'] = True
    
    button_config = load_codeEditor_buttons_config()
    button_config.pop(-1)
    
    info_bar_options = load_codeEditor_infobar_config()
    info_bar_options['info'][0]['name'] = f"Prompt Template Editor | {all_projects[st.session_state['CURRENT_PROJECT_ID']]['name']} | v{all_prompts[st.session_state['current_prompt_id']]['version']} | {all_prompts[st.session_state['current_prompt_id']]['name']}"

    # st.warning('Once done with editing the template, click on the "Run" button on lower right corner of editor before "Create" button', icon='⚠️')
    # st.info('Use :blue[Double Curly Braces] to insert input variables in the template - {{ variable }}', icon='ℹ️')
    prompt_template_editor = code_editor(
        code=all_prompts[st.session_state['current_prompt_id']]['prompt_template'],
        options=options,
        height=[10, 100],
        lang='text',
        info=info_bar_options,
        buttons=button_config,
        allow_reset=True,
        key='prompt_template_editor',
    )

st.divider()
button_cols = st.columns(5)
back_to_projects = button_cols[1].button(':leftwards_arrow_with_hook: Back to Projects', use_container_width=True)
back_to_current_project = button_cols[3].button(':leftwards_arrow_with_hook: Back to Current Project', use_container_width=True)

# Delete local variables from st.session_state
def clean_session_state():
    st.session_state.pop('prompt_name')
    st.session_state.pop('version')
    st.session_state.pop('description')
    st.session_state.pop('parent')
    st.session_state.pop('input_variables')
    st.session_state.pop('add_to_favorites')
    st.session_state.pop('notes')
    st.session_state.pop('commit_button')
    st.session_state.pop('prompt_template_editor')
    st.session_state.pop('TEMPLATE_EDITOR_ID')
    st.session_state.pop('INPUT_VARIABLES')

# if back_to_projects:
#     clean_session_state()
#     switch_page("Projects")

# if back_to_current_project:
#     clean_session_state()
#     switch_page("show_project")

st.divider()
with st.expander('Session State'):
    st.json(st.session_state, expanded=True)