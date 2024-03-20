import os
import pandas as pd
from graphviz import Digraph
import re

def load_codeEditor_config(
    fpath: str = os.path.join("utils", "codeEditorOptions.json"),
) -> dict:
    import json

    with open(fpath, "r") as f:
        config = json.load(f)
    return config


def load_codeEditor_infobar_config(
    fpath: str = os.path.join("utils", "codeEditorInfoBar.json"),
) -> dict:
    import json

    with open(fpath, "r") as f:
        config = json.load(f)
    return config


def load_codeEditor_buttons_config(
    fpath: str = os.path.join("utils", "codeEditorButtons.json"),
) -> dict:
    import json

    with open(fpath, "r") as f:
        config = json.load(f)
    return config

# Get input variables from given prompt template
def get_input_variables(prompt_template_text:str) -> list:
    
    from jinja2 import Environment, meta
    
    # Initialize Jinja2 environment
    env = Environment()
    
    # Find variable names
    input_variables = list(meta.find_undeclared_variables(env.parse(prompt_template_text)))

    return input_variables


# Replace a space with a newline after every couple of words
# Used in the project_level_prompt_lineage function
def replace_space_with_newline(text):
    return re.sub(r'(\w+\s+\w+)\s+', r'\1\n', text)



# Create Project Level Prompt Lineage Graph
def project_level_prompt_lineage(prompts:pd.DataFrame) -> Digraph:
    
    # Initiate a Digraph
    g = Digraph('G')
    
    # Create clusters by prompt_group_id
    for cluster_idx, prompt_group_id in enumerate(prompts.prompt_group_id.unique()):
        
        # Different versions of the same prompt act as Nodes in the cluster
        subprompts:pd.DataFrame = prompts[prompts.prompt_group_id == prompt_group_id].copy(deep=True)
        subgraph_name:str = subprompts.name.values[0]
        
        if len(subgraph_name.split()) > 2:
            subgraph_name = replace_space_with_newline(subgraph_name)

        with g.subgraph(name=f'cluster_{cluster_idx}') as c:
            c.attr(label=subgraph_name)

            for prompt_idx, prompt in subprompts.iterrows():
                c.node(name=prompt.id, label=f'v{str(prompt.version)}')
    
    # Create edges between prompts
    for prompt_idx, prompt in prompts.iterrows():
        if prompt.parent_prompt_id:
            for parent_idx in prompt.parent_prompt_id.split(','):
                g.edge(parent_idx, prompt.id)
    
    return g
