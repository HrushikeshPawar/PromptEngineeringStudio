import os
from langchain_core.prompts import PromptTemplate


class TemplateNameAlreadyExists(Exception):
    pass


class TemplateFormatTypeNotValid(Exception):
    pass


class TemplateInputVariablesNotValid(Exception):
    pass

class TemplateInputVariablesDontMatchGroup(Exception):
    pass


def create_project_config(project_fpath: str, project_name: str) -> None:
    import json

    with open(os.path.join(project_fpath, "config.json"), "w") as f:
        json.dump(
            {
                "project_name": project_name,
            },
            f,
        )


def load_project_config(project_fpath: str) -> dict:
    import json

    with open(os.path.join(project_fpath, "config.json"), "r") as f:
        config = json.load(f)
    return config


def update_project_config(project_fpath: str, config: dict) -> None:
    import json

    with open(os.path.join(project_fpath, "config.json"), "w") as f:
        json.dump(config, f)


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


def get_prompt_groups(project_fpath: str) -> list:
    import os

    dir_content = os.listdir(project_fpath)

    if dir_content is None:
        return []

    return [
        fname
        for fname in os.listdir(project_fpath)
        if os.path.isdir(os.path.join(project_fpath, fname))
    ]


def prompt_templates_from_group(project_fpath: str, group_name: str) -> list:
    import os

    try:
        dir_content = os.listdir(os.path.join(project_fpath, group_name))
    except FileNotFoundError:
        return []

    if dir_content is None:
        return []

    return [
        fname.split(".")[0]
        for fname in os.listdir(os.path.join(project_fpath, group_name))
        if ".txt" in fname
    ]


def create_new_prompt_template(
    project_fpath: str,
    group_name: str,
    template_name: str,
    template_text: str,
    variable_format: str,
    input_variables: list,
    template_format: str,
) -> None:
    import os
    
    # Load project config
    project_config = load_project_config(project_fpath)
    if "prompt_groups" not in project_config:
        project_config["prompt_groups"] = dict()

    if group_name not in project_config["prompt_groups"]:
        project_config["prompt_groups"][group_name] = dict()
        project_config["prompt_groups"][group_name]['input_variables'] = list(sorted(input_variables))
        project_config["prompt_groups"][group_name]['template_format'] = template_format
        project_config["prompt_groups"][group_name]['prompts'] = dict()

    if group_name not in get_prompt_groups(project_fpath):
        os.mkdir(os.path.join(project_fpath, group_name))
        dir_just_created = True
    else:
        dir_just_created = False

    # Check if template name already exists
    if template_name in prompt_templates_from_group(project_fpath, group_name):
        if dir_just_created:
            os.rmdir(os.path.join(project_fpath, group_name))
        raise TemplateNameAlreadyExists("Template name already exists")

    # Check if template text is valid
    try:
        prompt_template = PromptTemplate.from_template(
            template=template_text, template_format=variable_format
        )
    except Exception:
        if dir_just_created:
            os.rmdir(os.path.join(project_fpath, group_name))
        raise TemplateFormatTypeNotValid("Template format type is not valid")

    if sorted(prompt_template.input_variables) != sorted(input_variables):
        if dir_just_created:
            os.rmdir(os.path.join(project_fpath, group_name))
        raise TemplateInputVariablesNotValid("Template input variables are not valid")
    
    if project_config['prompt_groups'][group_name]['input_variables'] != sorted(input_variables):
        if dir_just_created:
            os.rmdir(os.path.join(project_fpath, group_name))
        raise TemplateInputVariablesDontMatchGroup("Template input variables don't match group input variables")

    template_fpath = os.path.join(project_fpath, group_name, f"{template_name}.txt")
    with open(template_fpath, "w") as f:
        f.write(template_text)

    project_config["prompt_groups"][group_name]['prompts'][template_name] = {
        "template_fpath": template_fpath,
        "variable_format": variable_format,
    }

    # Save project config
    print("Updating project config")
    update_project_config(project_fpath, project_config)


def delete_prompt(project_fpath: str, group_name: str, template_name: str) -> None:
    import os

    # Load project config
    project_config = load_project_config(project_fpath)

    # Delete template file
    os.remove(project_config["prompt_groups"][group_name]["prompts"][template_name]["template_fpath"])

    # Delete template from project config
    del project_config["prompt_groups"][group_name]["prompts"][template_name]

    # Save project config
    update_project_config(project_fpath, project_config)

# Get input variables from given prompt template
def get_input_variables(prompt_template_text:str) -> list:
    
    # Get input variables
    prompt_template = PromptTemplate.from_template(template=prompt_template_text, template_format='jinja2')
    return prompt_template.input_variables
