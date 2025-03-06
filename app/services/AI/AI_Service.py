# AI_Service.py
import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
import google.generativeai as genai
import boto3

load_dotenv()

class LLMCLIENT():

    def __init__(self):
        self.azure_client = None
        self.google_api_key = None
        self.google_embedding = None
        self.anthopic_chat = None
        self.type_llm = os.getenv("TYPE_LLM")
        
        if self.type_llm == 'google_api': 
            print("Using Google Gemini")
            genai.configure(api_key = os.getenv("GEMINI_API_KEY"))
            self.google_api_key = os.getenv("GEMINI_API_KEY")

        elif self.type_llm == 'anthropic_api': 
            print("Using Antropic")
            print("aws_access_key_id", self.anthropic_api_key, 
                  "aws_secret_access_key", self.anthopic_api_access_key)
            self.anthopic_chat = boto3.client(service_name = 'bedrock-runtime', 
                                              region_name  = 'us-east-1', 
                                              aws_access_key_id = os.getenv("ANTHROPIC_API_KEY"), 
                                              aws_secret_access_key = os.getenv("ANTHROPIC_API_ACCESS_KEY"))

        else: #type_llm == 'azure_openai':
            print("Using Azure AI")
            self.azure_client = AzureOpenAI (
                api_key = os.getenv("AZURE_API_KEY"),
                azure_endpoint = os.getenv("AZURE_ENDPOINT"),
                api_version = os.getenv("AZURE_API_VERSION") # Ensure you use the correct API version 
                )

        return


    def get_llm(self):

        if self.type_llm == 'google_api': 
            print("Using Google Gemini")
            genai.configure(api_key = os.getenv("GEMINI_API_KEY"))
            self.google_api_key = os.getenv("GEMINI_API_KEY")

        elif self.type_llm == 'anthropic_api': 
            print("Using Antropic")
            print("aws_access_key_id", self.anthropic_api_key, 
                  "aws_secret_access_key", self.anthopic_api_access_key)
            self.anthopic_chat = boto3.client(service_name = 'bedrock-runtime', 
                                              region_name  = 'us-east-1', 
                                              aws_access_key_id = os.getenv("ANTHROPIC_API_KEY"), 
                                              aws_secret_access_key = os.getenv("ANTHROPIC_API_ACCESS_KEY"))

        else: #type_llm == 'azure_openai':
            print("Using Azure AI")
            self.azure_client = AzureOpenAI (
                api_key = os.getenv("AZURE_API_KEY"),
                azure_endpoint = os.getenv("AZURE_ENDPOINT"),
                api_version = os.getenv("AZURE_API_VERSION") # Ensure you use the correct API version 
                )

        return 


    def chat(self, prompt, conversation_id=None):
        if self.type_llm == 'google_api': 
            return self._google_chat(prompt, conversation_id)
        elif self.type_llm == 'anthropic_api':
            return self._antropic_chat(prompt, conversation_id)
        else:
            return self._azure_chat(prompt, conversation_id)

        
    def chat_messages(self, messages):
        if self.type_llm == 'google_api': 
            return self._google_chat_messages(messages)
        elif self.type_llm == 'anthropic_api':
            return self._antropic_chat_messages(messages)
        else:
            #return self._azure_chat_messages(messages)
            return self._azure_chat_messages_inlab(messages)
        

    def _azure_chat(self, prompt, conversation_id=None):
        response = self.azure_client.chat.completions.create(
            model= os.getenv("OPENAI_MODEL"), #"gpt-35-turbo-0613", # Ensure the engine name is correct for your setup 
            messages=[{"role": "system", "content": prompt}]
        )    
        return response.choices[0].message.content
    
    def _azure_chat_messages(self, messages):
        response = self.azure_client.chat.completions.create(
            model= os.getenv("OPENAI_MODEL"), #"gpt-35-turbo-0613", # Ensure the engine name is correct for your setup 
            messages=messages
        )    
        return response.choices[0].message.content


    def _azure_chat_messages_inlab(self, messages):
        """
        messages: [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a joke."},
            {"role": "assistant", "content": "Why don't scientists trust atoms? Because they make up everything!"}
        ]
        """

        system_prompt = """You are an AI assistant specialized in vehicle diagnostics, particularly in interpreting OBD-II message codes. Your role is to assist users by performing a triage of the provided OBD-II code, offering information about the code’s implications, and indicating the severity of the issue using a traffic light system. This system will help users understand whether they need to visit a service center immediately, if they should stop driving the vehicle, or if the issue is not urgent.
        Guidelines:
        Style: Maintain a formal tone in all interactions.
        Expertise: Demonstrate in-depth knowledge of vehicle systems and OBD-II codes.
        Triage: Use the OBD-II code to assess the situation and provide a clear recommendation:
            Red: Serious issue, stop the vehicle immediately and seek assistance.
            Yellow: Caution, visit a service center soon.
            Green: No immediate action required, the issue is not critical.
        User Knowledge Level: Adapt explanations based on the user’s level of mechanical knowledge:
            Beginner: Use simple terms and provide basic explanations.
            Expert: Use technical language and offer detailed insights.
        Responses: Ensure responses are short, clear, and direct.
        Remember to always prioritize the user’s safety and provide the most accurate information based on the given OBD-II code.
        """
        
        messages.insert(0, {"role": "system", "content": system_prompt})
        
        response = self.azure_client.chat.completions.create(
            model = os.getenv("OPENAI_MODEL"), 
            messages = messages,
            max_tokens  = 50,
            temperature = 0.7,
            #top_p=0.9,
            #stop = ["\n"],
            #n=1,
            stream = False
        )    
        return response.choices[0].message.content


    def _google_chat(self, prompt, conversation_id=None):    
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    
    def _google_chat_messages(self, messages):    
        prompt = " ".join([message["content"] for message in messages if message["role"] == "user"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text


    def _antropic_chat(self, prompt, conversation_id=None):    
        modelId = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
        ### parameters for the LLM to control text-generation
        # temperature increases randomness as it increases
        temperature = 0.5
        # top_p increases more word choice as it increases
        top_p = 1
        # maximum number of tokens togenerate in the output
        max_tokens_to_generate = 2500
        messages = [{"role": "user", "content": prompt}]
        body = json.dumps({
           "messages": messages,
           "max_tokens": max_tokens_to_generate,
           "temperature": temperature,
           "top_p": top_p,
           "anthropic_version": "bedrock-2023-05-31"
        })
        response = self.anthopic_chat.invoke_model(body=body, modelId=modelId, accept="application/json", contentType="application/json")
        response_body = json.loads(response.get('body').read())
        result = response_body.get('content', '')
        return result[0]["text"]
    
    def _antropic_chat_messages(self, messages):    
        modelId = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
        ### parameters for the LLM to control text-generation
        # temperature increases randomness as it increases
        temperature = 0.5
        # top_p increases more word choice as it increases
        top_p = 1
        # maximum number of tokens togenerate in the output
        max_tokens_to_generate = 2500
        body = json.dumps({
           "messages": messages,
           "max_tokens": max_tokens_to_generate,
           "temperature": temperature,
           "top_p": top_p,
           "anthropic_version": "bedrock-2023-05-31"
        })
        response = self.anthopic_chat.invoke_model(body=body, modelId=modelId, accept="application/json", contentType="application/json")
        response_body = json.loads(response.get('body').read())
        result = response_body.get('content', '')
        return result[0]["text"]
    

    def create_embedding(self, text):
        if self.type_llm == 'google_api': 
            return self._google_create_embedding(text)
        else:
            return self._azure_create_embedding(text)

    def _azure_create_embedding(self, text):
        response = self.azure_client.embeddings.create(
            model= "text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

    def _google_create_embedding(self, text):
        response = genai.embed_content(model="models/text-embedding-004", content=text)
        return response['embedding']


