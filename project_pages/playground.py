import os
import sqlite3
from hashlib import sha256
import jinja2
import pandas as pd
import streamlit as st
from st_pages import hide_pages
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page
from code_editor import code_editor

import google.generativeai as google_genai
import vertexai.language_models as vertexai_plam2
import vertexai.generative_models as vertexai_genai

import sys

sys.path.append('../utils')
from utils.sql_helper import get_prompt_details, get_all_projects, get_all_prompts
from utils.helper import load_codeEditor_buttons_config, load_codeEditor_config, load_codeEditor_infobar_config, get_input_variables
from utils.llm_helper import setup_gemini_model, setup_palm2_model

from dotenv import load_dotenv
load_dotenv()
### IMPORTS END ###

if 'config' not in st.session_state:
    switch_page("home")

## Setup the page
st.set_page_config(layout='wide')

# Set Connection to SQL Database and Create a cursor object
connection = sqlite3.connect(os.getenv('DB_PATH'))
cursor = connection.cursor()


## Local Variables
if 'MODEL_HASH' not in st.session_state:
    st.session_state['MODEL_HASH'] = None

if 'LLM_OUTPUT' not in st.session_state:
    st.session_state['LLM_OUTPUT'] = ''

if 'INPUT_TOKEN_COUNT' not in st.session_state:
    st.session_state['INPUT_TOKEN_COUNT'] = None

if 'OUTPUT_TOKEN_COUNT' not in st.session_state:
    st.session_state['OUTPUT_TOKEN_COUNT'] = None

if 'CURRENT_PROMPT_INFO' in st.session_state:
    st.session_state.pop('CURRENT_PROMPT_INFO')

if None not in st.session_state['config']['models']:
    st.session_state['config']['models'][None] = []

if 'INPUT_VARIABLES' not in st.session_state:
    st.session_state['INPUT_VARIABLES'] = []

if 'INPUT_VARIABLE_VALUES' not in st.session_state:
    st.session_state['INPUT_VARIABLE_VALUES'] = {}

if 'TEMPLATE_EDITOR_ID' not in st.session_state:
    st.session_state['TEMPLATE_EDITOR_ID'] = None

if 'ALL_PROJECTS' not in st.session_state:
    st.session_state['ALL_PROJECTS'] = get_all_projects(cursor, output_type='df')
    
    st.session_state['PROJECT_ID_LOOKUP'] = {
        st.session_state['ALL_PROJECTS']['name'][idx]: st.session_state['ALL_PROJECTS']['id'][idx] for idx in st.session_state['ALL_PROJECTS'].index
    }

if 'ALL_PROMPTS' not in st.session_state:
    st.session_state['ALL_PROMPTS'] = get_all_prompts(cursor, output_type='df')
    
    st.session_state['PROMPT_ID_LOOKUP'] = {
        (st.session_state['ALL_PROMPTS']['name'][idx], st.session_state['ALL_PROMPTS']['version'][idx]): st.session_state['ALL_PROMPTS']['id'][idx]
        for idx in st.session_state['ALL_PROMPTS'].index
    }

if 'PROMPT_TEMPLATE' not in st.session_state:
    st.session_state['PROMPT_TEMPLATE'] = ''

## Setup Required Variables
# Set Connection to SQL Database and Create a cursor object
connection = sqlite3.connect(os.getenv('DB_PATH'))
cursor = connection.cursor()

# Hide Internal Pages
hide_pages(st.session_state['config']['hidden_pages'])


## Helper Functions

# Delete local variables from st.session_state
def clean_session_state():
    st.session_state.pop('MODEL_HASH')
    st.session_state.pop('LLM_OUTPUT')
    st.session_state.pop('INPUT_TOKEN_COUNT')
    st.session_state.pop('OUTPUT_TOKEN_COUNT')
    st.session_state.pop('ALL_PROJECTS')
    st.session_state.pop('PROJECT_ID_LOOKUP')
    st.session_state.pop('ALL_PROMPTS')
    st.session_state.pop('PROMPT_ID_LOOKUP')
    st.session_state.pop('PROMPT_TEMPLATE')
    st.session_state.pop('llm_providers')
    st.session_state.pop('model_selection')
    st.session_state.pop('temperature_slider')
    st.session_state.pop('temperature_number_input')
    st.session_state.pop('max_output_tokens_slider')
    st.session_state.pop('max_output_tokens_number_input')
    st.session_state.pop('top_p')
    st.session_state.pop('top_k')
    st.session_state.pop('stop_sequence')
    
    if 'LLM' in st.session_state:
        st.session_state.pop('LLM')

# Copy the value of one widget to another
def copy_widget_value(copy_from_key:str, copy_to_key:str):
    st.session_state[copy_to_key] = st.session_state[copy_from_key]

# Calculate the hash of the model using the model settings
def calculate_model_hash() -> str:
    
    model_name = st.session_state['model_selection']
    temperature = st.session_state['temperature_slider']
    max_output_tokens = st.session_state['max_output_tokens_slider']
    top_p = st.session_state['top_p']
    top_k = st.session_state['top_k']
    stop_sequence = st.session_state['stop_sequence']
    
    string_to_hash = f"{model_name}-{temperature}-{max_output_tokens}-{top_p}-{top_k}-{stop_sequence}"
    return sha256(string_to_hash.encode()).hexdigest()

# Load the Model
def load_model():
    
    if st.session_state['llm_providers'] == 'GoogleAI':
        st.session_state['LLM'] = setup_gemini_model(
            model_name=st.session_state['model_selection'],
            temperature=st.session_state['temperature_slider'],
            max_output_tokens=st.session_state['max_output_tokens_slider'],
            top_p=st.session_state['top_p'],
            top_k=st.session_state['top_k'],
            # stop_sequence=st.session_state['stop_sequence']
            is_vertexai_model=False,
        )
    elif st.session_state['llm_providers'] == 'VertexAI':
        if 'gemini' in st.session_state['model_selection']:
            st.session_state['LLM'] = setup_gemini_model(
                model_name=st.session_state['model_selection'],
                temperature=st.session_state['temperature_slider'],
                max_output_tokens=st.session_state['max_output_tokens_slider'],
                top_p=st.session_state['top_p'],
                top_k=st.session_state['top_k'],
                # stop_sequence=st.session_state['stop_sequence']
                is_vertexai_model=True,
            )
        else:
            st.session_state['LLM'], st.session_state['PARAMETERS'] = setup_palm2_model(
                model_name=st.session_state['model_selection'],
                temperature=st.session_state['temperature_slider'],
                max_output_tokens=st.session_state['max_output_tokens_slider'],
                top_p=st.session_state['top_p'],
                top_k=st.session_state['top_k'],
                # stop_sequence=st.session_state['stop_sequence']
            )

# Render Prompt
def render_prompt() -> str:
    
    # Setup the Jinja2 Environment
    env = jinja2.Environment()
    
    # Get the Prompt Template
    prompt_template = env.from_string(st.session_state['prompt_template_editor']['text'])
    
    # Render the Prompt
    rendered_prompt = prompt_template.render(**st.session_state['INPUT_VARIABLE_VALUES'])
    
    return rendered_prompt

# Run Model
def run_model():
    # Get the Input Text
    input_text = render_prompt()
    
    with st.spinner('Running LLM Model...'):
            
        if st.session_state['llm_providers'] == 'GoogleAI' and 'gemini' in st.session_state['model_selection']:
            llm:google_genai.GenerativeModel = st.session_state['LLM']
            
            print('Getting Input Token Count...')
            st.session_state['INPUT_TOKEN_COUNT'] = get_token_count(render_prompt())
            print('Running Model...')
            st.session_state['LLM_OUTPUT'] = llm.generate_content(input_text).text
            print('Getting Outpu Token Count...')
            st.session_state['OUTPUT_TOKEN_COUNT'] = get_token_count(st.session_state['LLM_OUTPUT'])
        
        elif st.session_state['llm_providers'] == 'VertexAI' and 'gemini' in st.session_state['model_selection']:
            llm:vertexai_genai.GenerativeModel = st.session_state['LLM']
            
            print('Getting LLM Output...')
            response = llm.generate_content(input_text)
            st.session_state['LLM_OUTPUT'] = response.text
            st.session_state['INPUT_TOKEN_COUNT'] = response.to_dict()['usage_metadata']['prompt_token_count']
            st.session_state['OUTPUT_TOKEN_COUNT'] = response.to_dict()['usage_metadata']['candidates_token_count']
        
        elif st.session_state['llm_providers'] == 'VertexAI' and 'text' in st.session_state['model_selection']:
            llm: vertexai_plam2.TextGenerationModel = st.session_state['LLM']

            print('Getting LLM Output...')
            st.session_state['LLM_OUTPUT'] = llm.predict(input_text, **st.session_state['PARAMETERS']).text
            st.session_state['INPUT_TOKEN_COUNT'] = None
            st.session_state['OUTPUT_TOKEN_COUNT'] = None

# Get token count
def get_token_count(text:str) -> int:

    # If model is Gemini
    if 'gemini' in st.session_state['model_selection']:
        llm:google_genai.GenerativeModel = st.session_state['LLM']
        response = llm.count_tokens(text)
        
        return response.total_tokens

# Turn on the flag
def turn_on_flag(flag:str):
    st.session_state[flag] = True

## HEADER
st.title('Prompt Engineering Studio')
st.header('Projects', divider='rainbow')


## SUB-HEADERs
subheader_cols = st.columns(2)
with subheader_cols[0]:
    st.subheader('Playground')
    st.write("Play with your prompts and test them with different Large Language Models.")

with subheader_cols[1]:
    st.subheader('Load Prompt Template')
    
    subheader_cols = st.columns([.05, .3, .3, .3, .05])
    
    subheader_cols[1].selectbox('Project:', options=['None'] + st.session_state['ALL_PROJECTS']['name'].unique().tolist(), key='project_selectbox')
    
    prompt_options = [] if st.session_state['project_selectbox'] == 'None' else st.session_state['ALL_PROMPTS'][st.session_state['ALL_PROMPTS']['project_id'] == st.session_state['PROJECT_ID_LOOKUP'][st.session_state['project_selectbox']]]['name'].unique().tolist()
    subheader_cols[2].selectbox('Prompt Name:', options=prompt_options, key='prompt_name_selectbox')
    
    version_options = [] if st.session_state['prompt_name_selectbox'] == 'None' else st.session_state['ALL_PROMPTS'][st.session_state['ALL_PROMPTS']['name'] == st.session_state['prompt_name_selectbox']]['version'].unique().tolist()
    subheader_cols[3].selectbox('Version:', options=version_options, key='version_selectbox')
    
    subheader_button_cols = st.columns(3)
    subheader_button_cols[1].button('Load', key='load_button', use_container_width=True, disabled=st.session_state['prompt_name_selectbox'] == 'None' or st.session_state['version_selectbox'] == 'None')
    
    if st.session_state['load_button']:
        st.session_state['PROMPT_TEMPLATE'] = get_prompt_details(cursor, st.session_state['PROMPT_ID_LOOKUP'][(st.session_state['prompt_name_selectbox'], st.session_state['version_selectbox'])])['prompt_template']
        st.rerun()
    
st.divider()

def update_input_variable_dict():
    for var in st.session_state['INPUT_VARIABLES']:
        if f"{var}_input" in st.session_state:
            st.session_state['INPUT_VARIABLE_VALUES'][var] = st.session_state[f"{var}_input"]


## Create or Load a Project
main_columns = st.columns([0.01, 0.75, 0.02, 0.21, 0.01])

# LLM Setting Area
with main_columns[3]:

    st.subheader('LLM Settings')

    with st.expander('Drop Down', expanded=False):
        # LLM Provider
        st.selectbox(
                label='LLM Provider',
                options=st.session_state['config']['llm_providers'],
                key='llm_providers',
                placeholder='Select an LLM provider',
                index=None,
            )

        # Model Selection
        st.selectbox(
                label='Model Selection',
                options=st.session_state['config']['models'][st.session_state['llm_providers']],
                key='model_selection',
                placeholder='Select an LLM model',
                index=None,
            )

        # Temperature
        model_temp_cols = st.columns([0.75, 0.25])
        model_temp_cols[0].slider(
            label='Temperature',
            min_value=0.0,
            max_value=1.0,
            key='temperature_slider',
            help='Controls randomness. Lowering results in less random completions. As the temperature approaches zero, the model will become deterministic and repetitive. Higher temperature results in more random completions.',
            on_change=copy_widget_value,
            args=('temperature_slider', 'temperature_number_input'),
            # label_visibility='collapsed',
        )
        model_temp_cols[1].number_input(
            label='Temperature',
            min_value=0.0,
            max_value=1.0,
            key='temperature_number_input',
            on_change=copy_widget_value,
            args=('temperature_number_input', 'temperature_slider'),
            label_visibility='hidden',
        )

        # Max Output Tokens
        model_max_output_tokens_cols = st.columns([0.75, 0.25])
        model_max_output_tokens_cols[0].slider(
            label='Max Output Tokens',
            min_value=1,
            max_value=2048,
            step=1,
            value=1024,
            key='max_output_tokens_slider',
            help='Controls the number of tokens to generate.',
            on_change=copy_widget_value,
            args=('max_output_tokens_slider', 'max_output_tokens_number_input'),
            # label_visibility='collapsed',
        )
        model_max_output_tokens_cols[1].number_input(
            label='Max Output Tokens',
            min_value=1,
            max_value=2048,
            step=1,
            value=1024,
            key='max_output_tokens_number_input',
            on_change=copy_widget_value,
            args=('max_output_tokens_number_input', 'max_output_tokens_slider'),
            label_visibility='hidden',
        )

        # Top P and Top K
        _, topP_col, _, topK_cols, _ = st.columns([0.1, 0.35, 0.05, 0.35, 0.1])
        with topP_col:
            # st.write('Top P')
            st.number_input(
                label='Top P',
                min_value=0.0,
                max_value=1.0,
                value=1.0,
                key='top_p',
                # label_visibility='collapsed',
                disabled=True,
            )
        with topK_cols:
            # st.write('Top K')
            st.number_input(
                label='Top K',
                min_value=0,
                max_value=100,
                value=40,
                key='top_k',
                # label_visibility='collapsed',
                disabled=True,
            )

        # Stop Sequence
        st.text_input(
            label='Stop Sequence',
            key='stop_sequence',
            placeholder='Enter a stop sequence',
            # label_visibility='collapsed',
            disabled=True,
        )
        
        # Check if the model hash has changed
        if st.session_state['llm_providers'] and st.session_state['model_selection']:
            if st.session_state['MODEL_HASH'] != calculate_model_hash():
                st.session_state['MODEL_HASH'] = calculate_model_hash()
                st.warning('Setting changed. Please load model again!', icon="❗")
                
                # Load Model Button
                st.columns([0.1, 0.8, 0.1])[1].button(':green[Load Model]', key='load_model', use_container_width=True, on_click=load_model)


# Prompt Template Editor
with main_columns[1]:
    st.subheader('Prompt Template')
    # The prompt template editor
    prompt_template_display_options = load_codeEditor_config()
    # prompt_template_display_options['readOnly'] = True
    
    prompt_template_display_settings_cols = st.columns(3)
    prompt_template_display_options['wrap'] = prompt_template_display_settings_cols[0].toggle('Wrap Lines', value=True, key='prompt_template_display_wrap_lines')
    prompt_template_display_options['maxLines'] = 10
    prompt_template_display_options['maxLines'] = prompt_template_display_settings_cols[1].slider('Max Lines', min_value=10, max_value=100, value=10, key='prompt_template_display_max_lines')
    
    prompt_template_display_button_config = load_codeEditor_buttons_config()
    # prompt_template_display_button_config.pop(1)
    
    prompt_template_display_info_bar_options = load_codeEditor_infobar_config()
    prompt_template_display_info_bar_options['info'][0]['name'] = "Prompt Template"
    prompt_template_editor = code_editor(
        code=st.session_state['PROMPT_TEMPLATE'],
        options=prompt_template_display_options,
        lang='text',
        info=prompt_template_display_info_bar_options,
        buttons=prompt_template_display_button_config,
        allow_reset=True,
        key='prompt_template_editor',
    )
    if st.session_state['prompt_template_editor'] is not None:
        if 'id' in st.session_state['prompt_template_editor']:
            if st.session_state['TEMPLATE_EDITOR_ID'] != st.session_state['prompt_template_editor']['id']:
                st.session_state['INPUT_VARIABLES'] = get_input_variables(st.session_state['prompt_template_editor']['text'])
                st.session_state['TEMPLATE_EDITOR_ID'] = st.session_state['prompt_template_editor']['id']
                
                update_input_variable_dict()
                st.rerun()

st.divider()


## Examples
st.subheader('Examples')
example_cols = st.columns([.05, .4, .05, .55, .05])

with example_cols[1]:
    # demo_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    demo_list = st.session_state['INPUT_VARIABLES']
    
    if len(demo_list) > 3:
        quotient, remainder = divmod(len(demo_list), 3)
        if remainder > 0:
            rows = quotient + 1
        else:
            rows = quotient

        example_input_grid = grid(*[3 for _ in range(rows)])
    else:
        example_input_grid = grid(len(demo_list))
    
    for var in demo_list:
        with example_input_grid.container():
            st.text_area(
                label=var,
                key=f"{var}_input",
                placeholder=f'Enter a value for `{var}`',
                help=f'Enter a value for `{var}`',
                on_change=update_input_variable_dict,
                value=st.session_state['INPUT_VARIABLE_VALUES'][var] if var in st.session_state['INPUT_VARIABLE_VALUES'] else '',
            )
    # Button should be disabled if any of the input variables are empty or the model is not selected
    run_button_disabled = any([len(st.session_state[f"{var}_input"].strip()) == 0 for var in demo_list]) or (st.session_state['model_selection'] is None)
    st.columns(3)[1].button('⚙️ :green[Run]', key='run_button', use_container_width=True, disabled=run_button_disabled)


with example_cols[3]:
    
    if st.session_state['run_button']:
        update_input_variable_dict()
        with st.empty():
            run_model()
    
    if not run_button_disabled:
        input_text = render_prompt()
        expander_test = f"Input Text - `{st.session_state['INPUT_TOKEN_COUNT']}` Tokens" if st.session_state['INPUT_TOKEN_COUNT'] else "Input Text"
        with st.expander(expander_test):
            st.code(render_prompt(), language='txt', line_numbers=True)
        
    # The prompt template editor
    options = load_codeEditor_config()
    options['readOnly'] = True
    options['wrap'] = st.toggle('Wrap Lines', value=True)
    
    button_config = load_codeEditor_buttons_config()
    button_config.pop(1)
    
    info_bar_options = load_codeEditor_infobar_config()
    info_bar_options['info'][0]['name'] = f"LLM Output | {st.session_state['model_selection'] if st.session_state['model_selection'] else 'Select Model'}{' | ' + str(st.session_state['OUTPUT_TOKEN_COUNT']) + ' Tokens' if st.session_state['OUTPUT_TOKEN_COUNT'] else ''}"
    code_editor(
        code=st.session_state['LLM_OUTPUT'],
        options=options,
        height=[10, 100],
        lang='text',
        info=info_bar_options,
        buttons=button_config,
        allow_reset=True,
    )


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