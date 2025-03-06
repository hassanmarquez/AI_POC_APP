import os
from app.config import settings
import google.generativeai as genai
from .llm_interface import LLMInterface

class GeminiLLM(LLMInterface):
    def __init__(self):
        # google_api_key = os.getenv("GEMINI_API_KEY")
        google_api_key = settings.GEMINI_API_KEY
        genai.configure(api_key=google_api_key)
        self.geminiClient = genai.GenerativeModel('gemini-1.5-flash')

    def generate(self, prompt):
        response = self.geminiClient.generate_content(prompt)
        return response.text

    def generate_chat_messages(self, messages):
        # convert messages list in open ai context format to a single string to be used in gemini
        context = "\n".join([f"{message.role}: {message.content}" for message in messages])
        response = self.geminiClient.generate_content(context)
        return response.text
        