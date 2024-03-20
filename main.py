import os
import json
import streamlit as st
from st_pages import Page, show_pages, hide_pages
from streamlit_extras.grid import grid
from streamlit_extras.card import card
from streamlit_extras.switch_page_button import switch_page

from dotenv import load_dotenv
load_dotenv()
### IMPORTS END ###

# Setup the page
st.set_page_config(layout='centered')

# Import Config
with open(os.getenv('CONFIG_FPATH'), 'r') as f:
    st.session_state['config'] = json.load(f)

st.title('Prompt Engineering Studio')
st.header('Welcome to the Studio', divider='rainbow')

# add_page_title()

home_page = Page("main.py", "Home", icon="🏠")
project_page = Page("project_pages/projects.py", "Projects", icon="📁")
playground_page = Page("project_pages/playground.py", "Playground", icon="🎮")
create_new_project_page = Page("project_pages/create_new_project.py", "create_new_project")
show_project_page = Page("project_pages/show_project.py", "show_project")
update_project_page = Page("project_pages/update_project.py", "update_project")
create_new_prompt_from_scratch_page = Page("project_pages/create_new_prompt_from_scratch.py", "create_new_prompt_from_scratch")
show_prompt_versions_page = Page("project_pages/show_prompt_versions.py", "show_prompt_versions")
prompt_version_testing_page = Page("project_pages/prompt_version_testing.py", "prompt_version_testing")
create_new_prompt_version_page = Page("project_pages/create_new_prompt_version.py", "create_new_prompt_version")
create_new_prompt_from_current_page = Page("project_pages/create_new_prompt_from_current.py", "create_new_prompt_from_current")
edit_current_prompt_version_page = Page("project_pages/edit_current_prompt_version.py", "edit_current_prompt_version")
create_new_prompt_from_project_page = Page("project_pages/create_new_prompt_from_project.py", "create_new_prompt_from_project")
project_level_prompt_lineage_page = Page("project_pages/project_level_prompt_lineage.py", "project_level_prompt_lineage")

show_pages([
    home_page,
    project_page,
    playground_page,
    create_new_project_page,
    show_project_page,
    update_project_page,
    create_new_prompt_from_scratch_page,
    show_prompt_versions_page,
    prompt_version_testing_page,
    create_new_prompt_version_page,
    create_new_prompt_from_current_page,
    edit_current_prompt_version_page,
    create_new_prompt_from_project_page,
    project_level_prompt_lineage_page,
])

hide_pages(st.session_state['config']['hidden_pages'])

st.write('A tool to manage and version control your prompts and play with them in a playground.')

main_grid = grid(2)
with main_grid.container():
    card('📁', 'Projects', styles=st.session_state['config']['card_style'], key='project_card')

with main_grid.container():
    card('🎮', 'Playground', styles=st.session_state['config']['card_style'], key='playground_card')

def clean_session_state():
    st.session_state.pop("project_card")
    st.session_state.pop("playground_card")

if st.session_state['project_card']:
    clean_session_state()
    switch_page('Projects')

if st.session_state['playground_card']:
    clean_session_state()
    switch_page('Playground')

st.divider()
with st.expander('Session State'):
    st.json(st.session_state, expanded=True)