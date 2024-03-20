import os
import sqlite3
import streamlit as st
from st_pages import hide_pages
from streamlit_extras.card import card
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page

import sys

sys.path.append('../utils')
from utils.sql_helper import get_all_projects

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

st.title('Prompt Engineering Studio')
st.header('Projects', divider='rainbow')

## Helper functions
# Delete local variables from st.session_state
def clean_session_state():
    st.session_state.pop("create_project_card")
    
    for project_id in all_projects:
        st.session_state.pop(f"{all_projects[project_id]['name']}_project_card")

# Get all the Projects
all_projects = get_all_projects(cursor)

# Setup the Grid to display Project Cards
if len(all_projects) == 0:
    rows = 1
else:
    quotient, remainder = divmod(len(all_projects) + 1, 3)
    rows = quotient if remainder == 0 else quotient + 1
project_grid = grid(*[3 for _ in range(rows)])

# Universal Card Style
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
    },
    "text" : {
        "color" : "black",
        "font-family": "roboto",
    }
}


# Create New Project Card
with project_grid.container():
    card(
        title="➕",
        text="Create New Project",
        styles=card_styles,
        key="create_project_card"
    )

# Individual Project Cards
cards = []
card_ids = []
for project_id in all_projects:
    with project_grid.container():
        if all_projects[project_id]["description"]:
            if len(all_projects[project_id]["description"]) < 30:
                description = all_projects[project_id]["description"]
            else:
                description = all_projects[project_id]["description"][:30] + "..."
        else:
            description = ""
        
        cards.append(card(
            title=all_projects[project_id]["name"],
            text=description,
            styles=card_styles,
            key=f'{all_projects[project_id]["name"]}_project_card',
        ))
        card_ids.append(project_id)

# Switch to Create New Project Page
if st.session_state['create_project_card']:
    clean_session_state()
    switch_page("create_new_project")

# Check if the user clicked on any of the project cards
if True in cards:
    st.session_state['CURRENT_PROJECT_ID'] = card_ids[cards.index(True)]
    clean_session_state()
    switch_page("show_project")

with st.expander('Session State'):
    st.json(st.session_state, expanded=True)
