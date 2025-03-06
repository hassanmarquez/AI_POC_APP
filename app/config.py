import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.credentials import AccessToken
from pydantic_settings import BaseSettings # NEW

class Settings(BaseSettings):
    PROJECT_NAME	:str
        
    TYPE_LLM	:str
    # Azure credentials
    AZURE_API_KEY	:str
    AZURE_ENDPOINT	:str
    AZURE_API_VERSION	:str
    OPENAI_MODEL	:str
    DEPLOYMENT_EMBEDDING_MODEL	:str
        
    GEMINI_API_KEY	:str

    # Antropic AWS
    ANTHROPIC_API_KEY	:str
    ANTHROPIC_API_ACCESS_KEY	:str        
    
    # Llama keys
    LLAMA_API_KEY :str
    LLAMA_API_ENDPOINT :str

    #Storage Section	
    TYPE_STORAGE	:str
    UPLOAD_FOLDER	:str
    AZURE_STORAGE_CONNECTION_STRING	:str
    AZURE_STORAGE_CONTAINER_NAME	:str
    AZURE_DATA_STORE_PATH	:str
    AZURE_URL_PATH_IMAGE	:str
        
    #database Section	
    TYPE_DATABASE	:str
    AZURE_SEARCH_SERVICE_ENDPOINT	:str
    AZURE_SEARCH_API_KEY	:str
    AZURE_SEARCH_INDEX_NAME	:str
        
    # IMAGE processing access
    URL_IMAGE	:str
    VISION_ENDPOINT	:str
    VISION_KEY	:str

    class Config:
        env_file = ".env"


def get_secret_from_key_vault(secret_name: str,access_token:str) -> str:
    kv_uri = f"https://{settings.key_vault_name}.vault.azure.net"
    if access_token:
        # If an access token is provided, use it for authentication
        print("TOKEN")
        class TokenCredential:
            def get_token(self, *scopes, **kwargs):
                return AccessToken(token=access_token, expires_on=0)  # expires_on can be set accordingly

        credential = TokenCredential()
    else:
        print("CREDENTIALS")
        # Fallback to DefaultAzureCredential if no access token is provided
        credential = DefaultAzureCredential()
    
    client = SecretClient(vault_url=kv_uri, credential=credential)
    retrieved_secret = client.get_secret(secret_name)
    return retrieved_secret.value

settings = Settings()


if not settings.GEMINI_API_KEY:
    #settings.GEMINI_API_KEY = get_secret_from_key_vault("GEMINIAPIKEY",settings.ACCESS_TOKEN)
    #settings.AZURE_API_KEY = get_secret_from_key_vault("AZURE-API-KEY",settings.ACCESS_TOKEN)
    #settings.AZURE_ENDPOINT = get_secret_from_key_vault("AZURE-ENDPOINT",settings.ACCESS_TOKEN)
    #settings.AZURE_API_VERSION = get_secret_from_key_vault("AZURE-API-VERSION",settings.ACCESS_TOKEN)
    #settings.ANTHROPIC_API_KEY = get_secret_from_key_vault("ANTHROPIC-API-KEY",settings.ACCESS_TOKEN)
    #settings.ANTHROPIC_API_ACCESS_KEY = get_secret_from_key_vault("ANTHROPIC-API-ACCESS-KEY",settings.ACCESS_TOKEN)
    #settings.LLAMA_API_KEY = get_secret_from_key_vault("LLAMA-API-KEY",settings.ACCESS_TOKEN)
    #settings.LLAMA_API_ENDPOINT = get_secret_from_key_vault("LLAMA-API-ENDPOINT",settings.ACCESS_TOKEN)
    settings.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    settings.AZURE_API_KEY = os.getenv("AZURE_API_KEY")
    settings.AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
    settings.AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
    settings.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    settings.ANTHROPIC_API_ACCESS_KEY = os.getenv("ANTHROPIC_API_ACCESS_KEY")
    settings.LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
    settings.LLAMA_API_ENDPOINT = os.getenv("LLAMA_API_ENDPOINT")
