import os
import json
import boto3
from app.config import settings
from .llm_interface import LLMInterface

class AntropicLLM(LLMInterface):
    def __init__(self):
        anthropic_api_key = settings.ANTHROPIC_API_KEY
        anthopic_api_access_key = settings.ANTHROPIC_API_ACCESS_KEY
        self.anthopic_chat = boto3.client(service_name='bedrock-runtime', 
                                                region_name='us-east-1', 
                                                aws_access_key_id=anthropic_api_key, 
                                                aws_secret_access_key=anthopic_api_access_key)
        self.modelId = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
        self.temperature = 0.5
        self.top_p = 1
        self.max_tokens_to_generate = 2500
        self.anthropic_version = "bedrock-2023-05-31"

    def generate(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        body = json.dumps({
           "messages": messages,
           "max_tokens": self.max_tokens_to_generate,
           "temperature": self.temperature,
           "top_p": self.top_p,
           "anthropic_version": self.anthropic_version
        })
        response = self.anthopic_chat.invoke_model(body=body, modelId=self.modelId, accept="application/json", contentType="application/json")
        response_body = json.loads(response.get('body').read())
        result = response_body.get('content', '')
        return result[0]["text"]
    
    def generate_chat_messages(self, messages):
        body = json.dumps({
           "messages": [message.__dict__ for message in messages],
           "max_tokens": self.max_tokens_to_generate,
           "temperature": self.temperature,
           "top_p": self.top_p,
           "anthropic_version": self.anthropic_version
        })
        response = self.anthopic_chat.invoke_model(body=body, modelId=self.modelId, accept="application/json", contentType="application/json")
        response_body = json.loads(response.get('body').read())
        result = response_body.get('content', '')
        return result[0]["text"]
