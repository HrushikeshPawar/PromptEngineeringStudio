import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
from typing import Optional, Tuple

class ProjectAlreadyExistsError(Exception):
    pass

class ProjectNotFoundError(Exception):
    pass

class PromptAlreadyExistsError(Exception):
    pass


# Add New Project
def create_project(project_name:str, connection:sqlite3.Connection, cursor:sqlite3.Cursor, description=None):
    # Check if project name already exists (case-insensitive)
    cursor.execute("SELECT COUNT(*) FROM projects WHERE LOWER(name) = LOWER(?)", (project_name,))
    count = cursor.fetchone()[0]
    if count > 0:
        raise ProjectAlreadyExistsError

    # Generate unique ID using hashlib's sha
    project_id = hashlib.sha256(project_name.encode()).hexdigest()
    
    # Get the current date and time in YYYY-MM-DD HH:MM:SS format
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert new record into the project table
    if description is None:
        cursor.execute(
            "INSERT INTO projects (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (project_id, project_name, current_date_time, current_date_time)
        )
    else:
        cursor.execute(
            "INSERT INTO projects (id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (project_id, project_name, description, current_date_time, current_date_time)
        )
    connection.commit()


# Get all projects
def get_all_projects(cursor: sqlite3.Cursor, output_type:str='dict') -> dict:
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()
    
    if output_type == "dict":
        project_dict = {}
        for project in projects:
            project_id, project_name, project_description, created_at, updated_at = project
            project_dict[project_id] = {
                "name": project_name,
                "description": project_description,
                "created_at": created_at,
                "updated_at": updated_at
            }
        return project_dict

    if output_type == "df":
        project_df = pd.DataFrame(projects, columns = ['id', 'name', 'description', 'created_at', 'updated_at'])
        return project_df


# Update Project Details
def update_project(project_id:str, project_name:str, description:str, connection:sqlite3.Connection, cursor:sqlite3.Cursor):
    # Get the current date and time in YYYY-MM-DD HH:MM:SS format
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("UPDATE projects SET name = ?, description = ?, updated_at = ? WHERE id = ?", (project_name, description, current_date_time, project_id))
    connection.commit()


# Create a new prompt template
def create_prompt(
    project_id:str,
    prompt_name:str,
    parent_prompt_id:Optional[str],
    prompt_description:Optional[str],
    version:int,
    prompt_template:str,
    input_variables:str,
    favourite:bool,
    notes:Optional[str],
    connection:sqlite3.Connection,
    cursor:sqlite3.Cursor) -> Tuple[str, str]:
    
    # Check if project ID exists
    cursor.execute("SELECT COUNT(*) FROM projects WHERE id = ?", (project_id,))
    count = cursor.fetchone()[0]
    if count == 0:
        raise ProjectNotFoundError

    # Check if prompt name and version already exists within the project (case-insensitive)
    cursor.execute("SELECT COUNT(*) FROM prompts WHERE LOWER(name) = LOWER(?) AND version = ? AND project_id = ?", (prompt_name, version, project_id))
    count = cursor.fetchone()[0]
    if count > 0:
        raise PromptAlreadyExistsError
    
    # Generate unique ID using hashlib's sha
    id = hashlib.sha256((project_id + prompt_name + str(version)).encode()).hexdigest()
    prompt_group_id = hashlib.sha256((project_id + prompt_name).encode()).hexdigest()
    
    # Get the current date and time in YYYY-MM-DD HH:MM:SS format
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Insert new record into the prompt table
    cursor.execute(
        "INSERT INTO prompts (id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (id, prompt_group_id, project_id, parent_prompt_id, prompt_name, prompt_description, version, prompt_template, input_variables, int(favourite), notes, current_date_time, current_date_time)
    )
    connection.commit()
    
    return id, prompt_group_id


# Update Prompt Template
def update_prompt(
    id:str,
    prompt_name:str,
    prompt_description:Optional[str],
    version:int,
    prompt_template:str,
    input_variables:str,
    favourite:bool,
    notes:Optional[str],
    connection:sqlite3.Connection,
    cursor:sqlite3.Cursor):
    
    # Get the current date and time in YYYY-MM-DD HH:MM:SS format
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update the record in the prompt table
    cursor.execute(
        "UPDATE prompts SET name = ?, description = ?, version = ?, prompt_template = ?, input_variables = ?, favourite = ?, notes = ?, updated_at = ? WHERE id = ?",
        (prompt_name, prompt_description, version, prompt_template, input_variables, int(favourite), notes, current_date_time, id)
    )
    connection.commit()


# Get all prompts for a project or all prompts
def get_all_prompts(cursor: sqlite3.Cursor, project_id: Optional[str] = None, output_type:str='dict') -> dict:
    
    # Prompt Table Schema
    # id TEXT PRIMARY KEY | prompt_group_id TEXT NOT NULL | project_id TEXT NOT NULL | description TEXT | parent_prompt_id TEXT | name TEXT NOT NULL | version INTEGER NOT NULL |
    # prompt_template TEXT NOT NULL | input_variables TEXT | favourite INTEGER NOT NULL | notes TEXT | created_at TEXT NOT NULL | updated_at TEXT NOT NULL |
    # FOREIGN KEY (project_id) REFERENCES projects (id) |
    
    # Execute SQL Query
    if project_id:
        cursor.execute("""
            SELECT id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at 
            FROM prompts 
            WHERE project_id = ?
            """, (project_id,))
    else:
        cursor.execute("""
            SELECT id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at 
            FROM prompts
            """)
    
    # Fetch the data
    prompts = cursor.fetchall()
    
    if output_type == 'dict':
        # Convert to dictionary
        prompt_dict = {}
        for prompt in prompts:
            id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at = prompt
            prompt_dict[id] = {
                "prompt_group_id": prompt_group_id,
                "project_id": project_id,
                "parent_prompt_id": parent_prompt_id,
                "name": name,
                "description": description,
                "version": version,
                "prompt_template": prompt_template,
                "input_variables": input_variables,
                "favourite": favourite,
                "notes": notes,
                "created_at": created_at,
                "updated_at": updated_at
        }
        
        return prompt_dict

    if output_type == 'df':
        # Convert to dataframe
        prompt_df = pd.DataFrame(prompts, columns = ['id', 'prompt_group_id', 'project_id', 'parent_prompt_id', 'name', 'description', 'version', 'prompt_template', 'input_variables', 'favourite', 'notes', 'created_at', 'updated_at'])
        return prompt_df


# Get all prompt groups for a project or all prompt groups
def get_all_prompt_groups(cursor: sqlite3.Cursor, project_id: Optional[str] = None) -> dict:

        # Execute SQL Query
        if project_id:
            cursor.execute("""
                SELECT id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at 
                FROM prompts 
                WHERE project_id = ?
                """, (project_id,))
        else:
            cursor.execute("""
                SELECT id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at 
                FROM prompts
                """)
        
        # Fetch the data
        prompts = cursor.fetchall()
        
        # Convert to dictionary
        prompt_dict = {}
        for prompt in prompts:
            id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at = prompt
            prompt_dict[prompt_group_id] = {
                "project_id": project_id,
                "parent_prompt_id": parent_prompt_id,
                "name": name,
                "description": description,
                "version": version,
                "prompt_template": prompt_template,
                "input_variables": input_variables,
                "favourite": favourite,
                "notes": notes,
                "created_at": created_at,
                "updated_at": updated_at
            }
            
        return prompt_dict


# Get prompt group details
def get_prompt_group_details(cursor: sqlite3.Cursor, prompt_group_id: str) -> Tuple[str, str, str]:
    cursor.execute("SELECT id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at FROM prompts WHERE prompt_group_id = ?", (prompt_group_id,))
    prompt = cursor.fetchone()
    id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at = prompt
    return name, description


# Get all prompt versions
def get_all_prompt_versions(cursor: sqlite3.Cursor, prompt_group_id: str) -> pd.DataFrame:
    cursor.execute("SELECT id, version, input_variables, notes, favourite FROM prompts WHERE prompt_group_id = ?", (prompt_group_id,))
    versions = cursor.fetchall()
    
    data = {
        "id": [],
        "version": [],
        "input_variables": [],
        "notes": [],
        "favourite": []
    }
    
    for version in versions:
        id, version, input_variables, notes, favourite = version
        data["id"].append(id)
        data["version"].append(version)
        data["input_variables"].append(input_variables)
        data["notes"].append(notes)
        data["favourite"].append(bool(favourite))
    
    # Create a DataFrame
    prompt_version_df = pd.DataFrame(data)
    
    # Sort the DataFrame by version in descending order
    prompt_version_df = prompt_version_df.sort_values(by="version", ascending=False)
    
    return prompt_version_df


# Get all details about a prompt
def get_prompt_details(cursor: sqlite3.Cursor, id: str) -> dict:
    cursor.execute("SELECT id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at FROM prompts WHERE id = ?", (id,))
    prompt = cursor.fetchone()
    id, prompt_group_id, project_id, parent_prompt_id, name, description, version, prompt_template, input_variables, favourite, notes, created_at, updated_at = prompt
    return {
        "id": id,
        "prompt_group_id": prompt_group_id,
        "project_id": project_id,
        "parent_prompt_id": parent_prompt_id,
        "name": name,
        "description": description,
        "version": version,
        "prompt_template": prompt_template,
        "input_variables": [var.strip() for var in input_variables.split(",")] if input_variables else [],
        "favourite": bool(favourite),
        "notes": notes,
        "created_at": created_at,
        "updated_at": updated_at
    }


# Delete a Prompt by ID
def delete_prompt(id:str, connection:sqlite3.Connection, cursor:sqlite3.Cursor):
    cursor.execute("DELETE FROM prompts WHERE id = ?", (id,))
    connection.commit()