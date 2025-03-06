from fastapi import Depends

from app.services.autogen_service import AutogenService
from app.services.multi_llm_service.multi_llm_service import MultiLLMService

def get_llm_service() -> MultiLLMService:
    return MultiLLMService()

def get_autogen_service() -> AutogenService:
    return AutogenService()
