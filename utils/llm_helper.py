import os
import google.generativeai as google_genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

# Configure the API key
# google_genai.configure(api_key=os.getenv('GOOGLE_API_KEY'), transport="rest") ## Facing Issues with GRPC, hence `rest` is used
google_genai.configure(api_key=os.getenv('GOOGLE_API_KEY')) ## Issue solved - Issue was with WSL


# Setup Gemini Model
def setup_gemini_model(
    model_name:str,
    temperature:float,
    max_output_tokens:int,
    top_p:float,
    top_k:int,
    stop_sequence:Optional[List[str]]=None,
) -> google_genai.GenerativeModel:
    
    # Setup Safety Settings
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
    generation_config = google_genai.GenerationConfig(
        candidate_count=1,
        stop_sequences=stop_sequence,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
    )
    
    # Create a new model
    gemini_model = google_genai.GenerativeModel(
        model_name=model_name,
        safety_settings=safety_settings,
        generation_config=generation_config
        )

    return gemini_model