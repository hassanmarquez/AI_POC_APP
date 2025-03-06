import os

from dotenv import load_dotenv
from openai import AzureOpenAI
from app.config import settings
from .llm_interface import LLMInterface

class OpenAILLM(LLMInterface):
    def __init__(self):
        load_dotenv()
        azure_openai_key = settings.AZURE_API_KEY
        azure_openai_endpoint = settings.AZURE_ENDPOINT
        azure_openai_version = settings.AZURE_API_VERSION
        self.azure_client = AzureOpenAI(
                api_key=azure_openai_key,
                azure_endpoint=azure_openai_endpoint,
                api_version=azure_openai_version # Ensure you use the correct API version 
        )

    def generate(self, prompt):
        response = self.azure_client.chat.completions.create(
            model = os.getenv("OPENAI_MODEL"), #"gpt-35-turbo-0613", # Ensure the engine name is correct for your setup 
            messages = [{"role": "user", "content": prompt}]
        )    
        return response.choices[0].message.content

    def generate_chat_messages(self, messages):
        response = self.azure_client.chat.completions.create(
            model = os.getenv("OPENAI_MODEL"), 
            messages = messages,
            #max_tokens  = 200,
            #temperature = 0.7,
            #top_p=0.9,
            #stop = ["\n"],
            #n=1,
            #stream = False
        )    
        return response.choices[0].message.content

    def generate_assistant_chat_messages(self, system_prompt, messages):
        """
        messages: [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a joke."},
            {"role": "assistant", "content": "Why don't scientists trust atoms? Because they make up everything!"}
        ]
        """
        messages.insert(0, {"role": "system", "content": system_prompt})
        
        response = self.azure_client.chat.completions.create(
            model = os.getenv("OPENAI_MODEL"), 
            messages = messages,
            max_tokens  = 200,
            temperature = 0.7,
            #top_p=0.9,
            #stop = ["\n"],
            #n=1,
            stream = False
        )    
        return response.choices[0].message.content
