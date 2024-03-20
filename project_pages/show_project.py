import os
import sqlite3
import streamlit as st
from st_pages import hide_pages
from streamlit_extras.card import card
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page

import sys

sys.path.append('../utils')
from utils.sql_helper import get_all_prompt_groups, get_all_projects

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
    st.session_state.pop("create_prompt_from_scratch_card")
    st.session_state.pop("create_prompt_from_db_card")
    
    for idx in range(len(all_prompts)):
        st.session_state.pop(f"prompt_card_{idx}")


# Get the Current Project Details
all_projects = get_all_projects(cursor)

st.title('Prompt Engineering Studio')
st.header('Projects', divider='rainbow')
st.subheader(all_projects[st.session_state['CURRENT_PROJECT_ID']]['name'])
st.write(all_projects[st.session_state['CURRENT_PROJECT_ID']]['description'])
st.divider()

all_prompts = get_all_prompt_groups(cursor, st.session_state['CURRENT_PROJECT_ID'])
all_prompts = {k: v for k, v in sorted(all_prompts.items(), key=lambda item: item[1]['name'])}
COL_NUM = 3
if len(all_prompts) == 0:
    rows = 1
else:
    quotient, remainder = divmod(len(all_prompts) + 2, COL_NUM)
    rows = quotient if remainder == 0 else quotient + 1

project_grid = grid(*[COL_NUM for _ in range(rows)])

card_styles = {
    "card": {
        "width": "180px",
        "height": "180px",
        "border-radius": "20px",
        "background-color": "rgb(255, 255, 255)",
        
    },
    "title" : {
        "color" : "black",
        "font-family": "roboto",
        "font-size": "25px",
    },
    "text" : {
        "color" : "black",
        "font-family": "roboto",
    }
}

# Cell to create new prompt template from scratch
with project_grid.container():
    card(
        title="➕",
        text="Create New Prompt Template from Scratch",
        styles=card_styles,
        key="create_prompt_from_scratch_card"
    )

# Cell to create new prompt template from database
with project_grid.container():
    card(
        title="🔍",
        text="Create New Prompt Template from Database",
        styles=card_styles,
        key="create_prompt_from_db_card"
    )

# Individual Prompt Cards
cards = []
card_ids = []
for idx, prompt_group_id in enumerate(all_prompts):
    with project_grid.container():
        if all_prompts[prompt_group_id]["description"]:
            if len(all_prompts[prompt_group_id]["description"]) < 30:
                description = all_prompts[prompt_group_id]["description"]
            else:
                description = all_prompts[prompt_group_id]["description"][:30] + "..."
        else:
            description = ""

        cards.append(card(
            title=all_prompts[prompt_group_id]['name'],
            text=[description],
            styles=card_styles,
            key=f"prompt_card_{idx}"
        ))
        card_ids.append(prompt_group_id)

# Switch to Create New Prompt Page
if st.session_state['create_prompt_from_scratch_card']:
    clean_session_state()
    switch_page("create_new_prompt_from_scratch")

# Switch to Create New Prompt from a Project Prompt Page
if st.session_state['create_prompt_from_db_card']:
    clean_session_state()
    switch_page("create_new_prompt_from_project")

# Check if the user clicked on any of the project cards
if True in cards:
    st.session_state['CURRENT_PROMPT_GROUP_ID'] = card_ids[cards.index(True)]
    clean_session_state()
    switch_page("show_prompt_versions")

st.divider()
button_cols = st.columns(3)
back_to_projects = button_cols[0].button(':leftwards_arrow_with_hook: Back to Projects', use_container_width=True)
update_project = button_cols[1].button(':pencil2: Update Project', use_container_width=True)
lineage_graph = button_cols[2].button(':bar_chart: Lineage Graph', use_container_width=True)

if back_to_projects:
    clean_session_state()
    switch_page("Projects")

if update_project:
    clean_session_state()
    switch_page("update_project")

if lineage_graph:
    clean_session_state()
    switch_page("project_level_prompt_lineage")

st.divider()
with st.expander('Session State'):
    st.json(st.session_state, expanded=True)
