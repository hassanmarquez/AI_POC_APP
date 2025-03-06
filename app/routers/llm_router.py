import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from app.dependencies import get_autogen_service, get_llm_service
from app.models.llm_model import AnalysisDataResponse, AutogenRequest, AutogenResponse, ChatIdRequest, ChatIdResponse, PromptRequest, PromptRequestMessages, PromptResponse, PromptResponseMessages
from app.models.llm_model import AssitantMessagesRequest, AnalysisDataRequest, LoadDocumentRequest, AssitantRequest
from app.services.multi_llm_service.multi_llm_service import MultiLLMService
from app.services.autogen_service import AutogenService

from app.services.storage.storage_service import load_document_blod
from app.services.persistence.database_service import store_collection
from app.services.document_service import read_document, save_document, search_documents

#from app.services.rag.rag_service import store_collection
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import requests

router = APIRouter()


@router.get("/models",response_model=list)
def get_models(llm_service: MultiLLMService = Depends(get_llm_service)):
    descriptions = [
        "OpenAI is a research laboratory based in San Francisco that focuses on building advanced artificial intelligence (AI) systems.",
        "Gemini is a general-purpose, multilingual, multimodal AI model developed by Google.",
        "Anthropic is a company that develops AI-powered chatbots and virtual assistants.",
        "Meta is a company that develops AI-powered chatbots and virtual assistants.",
    ]
    images_links = [
        "https://static-00.iconduck.com/assets.00/openai-icon-2021x2048-4rpe5x7n.png",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcThr7qrIazsvZwJuw-uZCtLzIjaAyVW_ZrlEQ&s",
        "https://www.appengine.ai/uploads/images/profile/logo/Anthropic-AI.png",
        "https://res.cloudinary.com/apideck/image/upload/w_196,f_auto/v1677940393/marketplaces/ckhg56iu1mkpc0b66vj7fsj3o/listings/meta_nnmll6.webp",
    ]
    models = llm_service.get_models()
    print(models)
    result = []
    for i in range(len(models)):
        model = models[i]
        print(model,str(i))
        result.append({
            "name": model,
            "value": model,
            "image": images_links[i],
            "description": descriptions[i]
        })
    return result


@router.post("/generate/prompt", response_model=PromptResponse)
def get_response(prompt_request: PromptRequest, llm_service: MultiLLMService = Depends(get_llm_service)):
    try:
        response = llm_service.generate_response(prompt_request.llm_type, prompt_request.prompt)
        return PromptResponse(message=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/chat", response_model=PromptResponseMessages)
def get_chat_response(prompt_request: PromptRequestMessages, llm_service: MultiLLMService = Depends(get_llm_service)):
    try:
        messages, response = llm_service.generate_chat_response(prompt_request.llm_type,prompt_request.messages)
        return PromptResponseMessages(messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/autogen_websurfer", response_model=AutogenResponse)
def get_chat_response(autogen_request: AutogenRequest, autogen_service: AutogenService = Depends(get_autogen_service)):
    try:
        #date_time = datetime.now().strftime('%Y/%m/%d %H:%M')
        reponse_autogen = autogen_service.generate_websurfer(autogen_request.task) 
        #store_collection("autogen_websurfer", [uuid.uuid4().hex], [date_time], [reponse_autogen])
        return AutogenResponse(response=reponse_autogen)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assistant/generate_chat_id", response_model=ChatIdResponse)
def get_chat_response(chat_id_request: ChatIdRequest, llm_service: MultiLLMService = Depends(get_llm_service)):
    try:
        prompt = """Summarize the following text in a maximum of 10 words """ + chat_id_request.prompt
        response = llm_service.generate_response(chat_id_request.llm_type, prompt)
        return ChatIdResponse(title=response, uuid=uuid.uuid4().hex)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# POST route that recevie an prompt and a image to generate a response
@router.post("/assistant/analize_image", response_model=PromptResponse)
async def get_response_image(image: UploadFile = File(...), prompt: str = Form(...), llm_service: MultiLLMService = Depends(get_llm_service)):
    try:
        # Read the image file
        image = Image.open(BytesIO(await image.read()))
        
        # Convert image to RGB if it's in RGBA mode (PNG with transparency)
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        buffer = BytesIO()
        # Save as JPEG (which doesn't support transparency)
        image.save(buffer, format="JPEG", quality=95)
        encoded_image = base64.b64encode(buffer.getvalue()).decode('ascii')
        
        answer = llm_service.generate_response_image(prompt, encoded_image)
        # Send request
        return PromptResponse(message=answer)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to make the request. Error: {str(e)}")


# POST route that recevie an prompt and a image to generate a response
@router.post("/assistant/command_image", response_model=PromptResponse)
async def command_image(image: UploadFile = File(...), prompt_request: PromptRequest = Form(...), llm_service: MultiLLMService = Depends(get_llm_service)):
    try:

        # Read the image file
        image = Image.open(BytesIO(await image.read()))
        
        # Convert image to RGB if it's in RGBA mode (PNG with transparency)
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        buffer = BytesIO()
        # Save as JPEG (which doesn't support transparency)
        image.save(buffer, format="JPEG", quality=95)
        encoded_image = base64.b64encode(buffer.getvalue()).decode('ascii')

        #store blod
        load_document_blod(image.filename, encoded_image)

        #prompt = f"""you are an assistant for a blind person, your task is to help and be friendly. "
        #            you should help with the next requirement: {prompt}
        #            and you are currently seeing the next: {image}"""

        response = llm_service.generate_response_image(prompt_request.prompt, encoded_image)
        #print(f"prompt {response}") 

    except Exception as error:
        response = f"An exception occurred:{error} "

    return get_response(response, 200)


@router.post("/assistant/load_document", response_model=PromptResponse)
def command_load_document(file: UploadFile = File(...), document_request: LoadDocumentRequest = Form(...), llm_service: MultiLLMService = Depends(get_llm_service)):
    try:

        if not file or not document_request.title:
            raise HTTPException(status_code=500, detail=str('file and title are required'))

        bytes_file = base64.b64decode(file.file.read())

        #store blod
        load_document_blod(file.filename, bytes_file)

        #analysis image 
        url, text_document = read_document(file.filename)
        print("#save_document")
        save_document(file.filename, url, text_document)
          
        return PromptResponse(message=f"document save {file.filename}")

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to make the request. Error: {str(e)}")


@router.post("/assistant/prompt", response_model=PromptResponse)
def command_prompt(request_prompt: AssitantRequest, llm_service: MultiLLMService = Depends(get_llm_service)):
    
    try:
        print(request_prompt)
        print(request_prompt.prompt)
        response = llm_service.generate_response('openai', request_prompt.prompt)
        return PromptResponse(message=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/assistant/prompt_messages", response_model=PromptResponse)
def prompt_messages(request_messages: AssitantMessagesRequest, llm_service: MultiLLMService = Depends(get_llm_service)):

    try:
        messages, response = llm_service.generate_assistant_chat_response('openai', request_messages)  
        return PromptResponse(message=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assistant/prompt_search", response_model=PromptResponse)
def prompt_search(request: AssitantMessagesRequest, llm_service: MultiLLMService = Depends(get_llm_service)):

    try:    
        result = search_documents(request.codes.join(","))
        content_text = ""
        for(index, row) in result.iterrows():
            print(row['Content'])
            content_text = f"{content_text} {row['Content']}"

        messages, response = llm_service.generate_assistant_chat_response('openai', request)  
        return PromptResponse(message=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to make the request. Error: {str(e)}")


@router.post("/assistant/analysis_data", response_model=AnalysisDataResponse)
async def prompt_messages(request_messages: AnalysisDataRequest, autogen_service: AutogenService = Depends(get_autogen_service)):

    try:
        summary, image_name = await autogen_service.generate_analysis_data_response(request_messages.status, request_messages.task)  
        return AnalysisDataResponse(summary=summary, image_name=image_name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
