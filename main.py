import os
import json
import streamlit as st
from st_pages import Page, show_pages, hide_pages

from dotenv import load_dotenv
load_dotenv()
### IMPORTS END ###

# Setup the page
st.set_page_config(layout='centered')

# Import Config
with open(os.getenv('CONFIG_FPATH'), 'r') as f:
    st.session_state['config'] = json.load(f)

st.title('Prompt Engineering Studio')
st.header('Welcome to the Studio')

# add_page_title()

home_page = Page("main.py", "Home", icon="🏠")
project_page = Page("project_pages/projects.py", "Projects", icon="📁")
create_new_project_page = Page("project_pages/create_new_project.py", "create_new_project")
show_project_page = Page("project_pages/show_project.py", "show_project")
update_project_page = Page("project_pages/update_project.py", "update_project")
create_new_prompt_from_scratch_page = Page("project_pages/create_new_prompt_from_scratch.py", "create_new_prompt_from_scratch")
show_prompt_versions_page = Page("project_pages/NR_show_prompt_versions.py", "show_prompt_versions")
prompt_version_testing_page = Page("project_pages/prompt_version_testing.py", "prompt_version_testing")
create_new_prompt_version_page = Page("project_pages/create_new_prompt_version.py", "create_new_prompt_version")
create_new_prompt_from_current_page = Page("project_pages/create_new_prompt_from_current.py", "create_new_prompt_from_current")
edit_current_prompt_version_page = Page("project_pages/edit_current_prompt_version.py", "edit_current_prompt_version")
create_new_prompt_from_project_page = Page("project_pages/create_new_prompt_from_project.py", "create_new_prompt_from_project")

show_pages([
    home_page,
    project_page,
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
])

hide_pages(st.session_state['config']['hidden_pages'])

with st.expander('Session State'):
    st.json(st.session_state, expanded=True)