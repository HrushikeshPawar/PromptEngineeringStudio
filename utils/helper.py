import os

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
    
    from langchain.prompts import PromptTemplate
    
    # Get input variables
    prompt_template = PromptTemplate.from_template(template=prompt_template_text, template_format='jinja2')
    return prompt_template.input_variables
