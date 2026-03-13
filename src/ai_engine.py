import os
import streamlit as st # type: ignore
from openai import OpenAI # type: ignore
from dotenv import load_dotenv # type: ignore
from src.logger import log
from src.prompts import get_analysis_prompt

#Load environment variables from .env file.
load_dotenv()

class ThreatAI:
    """
    The ai_engine class is used for initiating the AI engine itself, the .env file is loaded in  with the API key.
    Using the .env file improves security of the API key, and prevents hard coded secret values from being uploading with version control.
    This is also where the system prompt is set for the GPT api.
    """

    def __init__(self):
        """
        Initializes the ThreatAI by loading the .env and selecting the GPT model, currently the selected model is gpt-4o-mini.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            log("Error: API KEY not found in environment variables. Please set it in the .env file.", level="error")
            raise ValueError("API KEY not found in environment variables.")
        
        #GPT specific initialization
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

        if "ai_cache" not in st.session_state:
            st.session_state.ai_cache = {}
            log("Initialized AI cache in session state.", level="info")
            

    def get_explanation(self, current_data, user_input, model_name=None):
        """

        :param parsed_data:
        :return:
        """
        

        cache_key = hash(str(current_data) + str(user_input))
        if cache_key in st.session_state.ai_cache:
            log("AI Cache Hit", level="success")
            return st.session_state.ai_cache[cache_key]
        
        nmap_telemetry = current_data.get("nmap", "No network data available.")
        host_telemetry = current_data.get("host", "No host telemetry available.")

        system_prompt = get_analysis_prompt(nmap_telemetry, host_telemetry, user_query=user_input)

        try:
            log("Sending data to AI for analysis...", level="info")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.5,
                max_tokens=500,
                top_p=1.0
            )

            analysis = response.choices[0].message.content

            st.session_state.ai_cache[cache_key] = analysis
            log("AI Response recieved and cached", level="success")
            log(f"AI Analysis by {model_name}, returning response to user.", level="info")

            return analysis

        except Exception as e:
            log(f"API Call Failed: {str(e)}", level="error")
            return f"I'm sorry, I encountered an error analyzing your data: {str(e)}"