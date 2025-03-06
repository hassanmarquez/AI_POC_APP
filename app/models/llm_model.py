from typing import Dict, List
from fastapi import File, UploadFile
from pydantic import BaseModel

class PromptRequest(BaseModel):
    llm_type: str
    prompt: str
    
class RoleMessage(BaseModel):
    role: str
    content: str
    
class PromptRequestMessages(BaseModel):
    llm_type: str
    messages: List[RoleMessage]

class PromptResponseMessages(BaseModel):
    messages: List[RoleMessage]
    
class PromptResponse(BaseModel):
    message: str
    
class ModelsResponse(BaseModel):
    name: str
    value: str

class ImagePromptRequest(BaseModel):
    prompt: str

class ChatIdRequest(BaseModel):
    llm_type: str
    prompt: str  

class ChatIdResponse(BaseModel):
    title: str  
    uuid: str  

class AutogenResponse(BaseModel):
    response: str

class AutogenRequest(BaseModel):
    task: str

class ImageDescriptionResponse(BaseModel):
    description: str
    interaction: str

class AssitantRequest(BaseModel):
    prompt: str

class LoadDocumentRequest(BaseModel):
    title: str

class AssitantMessagesRequest(BaseModel):
    status: str
    vin: str
    codes: List[str]
    messages: List[RoleMessage]

class AnalysisDataRequest(BaseModel):
    task: str
    status: str

class AnalysisDataResponse(BaseModel):
    summary: str
    image_name: str