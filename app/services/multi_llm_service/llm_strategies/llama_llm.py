import os
import json
from app.config import settings
from .llm_interface import LLMInterface

import urllib.request

class LlamaLLM(LLMInterface):
    def __init__(self):
        # google_api_key = os.getenv("GEMINI_API_KEY")
        self.llama_api_key = settings.LLAMA_API_KEY
        self.url = settings.LLAMA_API_ENDPOINT
        self.max_tokens = 128
        self.temperature = 0.8
        self.top_p = 0.1
        self.best_of = 1
        self.presence_penalty = 0
        self.use_beam_search = "false"
        self.ignore_eos = "false"
        self.skip_special_tokens = "false"
        self.stream = "false"

    def generate(self, prompt):
        data =  {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "best_of": self.best_of,
            "presence_penalty": self.presence_penalty,
            "use_beam_search": self.use_beam_search,
            "ignore_eos": self.ignore_eos,
            "skip_special_tokens": self.skip_special_tokens,
            "stream": self.stream
        }
        body = str.encode(json.dumps(data))
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ self.llama_api_key)}
        req = urllib.request.Request(self.url, body, headers)
        response = urllib.request.urlopen(req)
        result = response.read()
        result_str = result.decode('utf-8')  # Decode byte to string
        result_json = json.loads(result_str)  # Parse string to JSON
        return result_json["choices"][0]["message"]["content"]
    
    def generate_chat_messages(self, messages):
        serialized_messages = []
        for message in messages:
            serialized_message = {
                "role": message.role,
                "content": message.content
            }
            serialized_messages.append(serialized_message)
        
        data =  {
            "messages": serialized_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "best_of": self.best_of,
            "presence_penalty": self.presence_penalty,
            "use_beam_search": self.use_beam_search,
            "ignore_eos": self.ignore_eos,
            "skip_special_tokens": self.skip_special_tokens,
            "stream": self.stream
        }
        body = str.encode(json.dumps(data))
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ self.llama_api_key)}
        req = urllib.request.Request(self.url, body, headers)
        response = urllib.request.urlopen(req)
        result = response.read()
        result_str = result.decode('utf-8')  # Decode byte to string
        result_json = json.loads(result_str)  # Parse string to JSON
        return result_json["choices"][0]["message"]["content"]