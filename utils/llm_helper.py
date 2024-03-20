import os
import google.generativeai as google_genai

import google.auth
import vertexai
import vertexai.generative_models as vertexai_genai
import vertexai.language_models as vertexai_plam2

from typing import List, Optional, Tuple, Union

from dotenv import load_dotenv
load_dotenv()

# Configure the API key
# google_genai.configure(api_key=os.getenv('GOOGLE_API_KEY'), transport="rest") ## Facing Issues with GRPC, hence `rest` is used
google_genai.configure(api_key=os.getenv('GOOGLE_API_KEY')) ## Issue solved - Issue was with WSL

# Setup VertexAI
credentials, project_id = google.auth.default()
LOCATION = os.getenv('GCP_LOCATION')
vertexai.init(project=os.getenv('GCP_PROJECT'), location=LOCATION, credentials=credentials)


# Setup Gemini Model
def setup_gemini_model(
    model_name:str,
    temperature:float=0,
    max_output_tokens:int=1024,
    top_p:float=1,
    top_k:int=40,
    stop_sequence:Optional[List[str]]=None,
    is_vertexai_model:bool=False,
) -> Union[google_genai.GenerativeModel, vertexai_genai.GenerativeModel]:
    
    if is_vertexai_model:
        from vertexai.generative_models import GenerativeModel, GenerationConfig, HarmCategory, HarmBlockThreshold
    else:
        from google.generativeai import GenerativeModel, GenerationConfig
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
    
    # Setup Safety Settings
    if is_vertexai_model:
        safety_settings = {
            # HarmCategory.HARM_CATEGORY_DANGEROUS: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            # HarmCategory.HARM_CATEGORY_DEROGATORY: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            # HarmCategory.HARM_CATEGORY_MEDICAL: HarmBlockThreshold.BLOCK_NONE,
            # HarmCategory.HARM_CATEGORY_SEXUAL: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            # HarmCategory.HARM_CATEGORY_TOXICITY: HarmBlockThreshold.BLOCK_NONE,
            # HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
            # HarmCategory.HARM_CATEGORY_VIOLENCE: HarmBlockThreshold.BLOCK_NONE,
        }
    else:
        safety_settings = {
            # HarmCategory.HARM_CATEGORY_DANGEROUS: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            # HarmCategory.HARM_CATEGORY_DEROGATORY: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            # HarmCategory.HARM_CATEGORY_MEDICAL: HarmBlockThreshold.BLOCK_NONE,
            # HarmCategory.HARM_CATEGORY_SEXUAL: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            # HarmCategory.HARM_CATEGORY_TOXICITY: HarmBlockThreshold.BLOCK_NONE,
            # HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
            # HarmCategory.HARM_CATEGORY_VIOLENCE: HarmBlockThreshold.BLOCK_NONE,
        }
    
    # Setup Model Config
    generation_config = GenerationConfig(
        candidate_count=1,
        stop_sequences=stop_sequence,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
    )
    
    # Create a new model
    gemini_model = GenerativeModel(
        model_name=model_name,
        safety_settings=safety_settings,
        generation_config=generation_config
        )

    return gemini_model


# Setup PaLM2 models
def setup_palm2_model(
    model_name:str,
    temperature:float=0,
    max_output_tokens:int=1024,
    top_p:float=1,
    top_k:int=40,
    stop_sequences:Optional[List[str]]=None,
) -> Tuple[vertexai_plam2.TextGenerationModel, dict]:
    
    if "@002" in model_name:
        max_output_tokens = min(max_output_tokens, 1024)
    top_k = min(top_k, 40)
    
    # Load the Model
    palm2_model = vertexai_plam2.TextGenerationModel.from_pretrained(model_name)
    
    # Set Parameters
    parameters = {
        'temperature': temperature,
        'max_output_tokens': max_output_tokens,
        'top_p': top_p,
        'top_k': top_k,
        'stop_sequences': stop_sequences,
    }
    
    return palm2_model, parameters
    