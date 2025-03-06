import requests
from .llm_strategies.antropic_llm import AntropicLLM
from .llm_strategies.gemini_llm import GeminiLLM
from .llm_strategies.openai_llm import OpenAILLM
from .llm_strategies.llama_llm import LlamaLLM
from app.models.llm_model import AnalysisDataRequest, AssitantMessagesRequest
from app.config import settings

class MultiLLMService:
    llm_strategies = {
        'openai': OpenAILLM(),
        'gemini': GeminiLLM(),
        'anthropic': AntropicLLM(),
        'llama': LlamaLLM(),
    }
    
    def generate_response(self, llm_type, prompt):
        llm_strategy = MultiLLMService.llm_strategies.get(llm_type)
        if llm_strategy:
            return llm_strategy.generate(prompt)
        else:
            return {"error": "Unsupported LLM type"}

    def get_models(self):
        return list(MultiLLMService.llm_strategies.keys())
    
    def generate_chat_response(self, llm_type, messages):
        llm_strategy = MultiLLMService.llm_strategies.get(llm_type)
        if llm_strategy:
            response = llm_strategy.generate_chat_messages(messages)
            messages.append({"role": "assistant", "content": response})
            return messages, response
        else:
            return {"error": "Unsupported LLM type"}

    def generate_assistant_chat_response(self, llm_type, assistantmessages: AssitantMessagesRequest):
        llm_strategy = MultiLLMService.llm_strategies.get(llm_type)
        if not llm_strategy:
            return {"error": "Unsupported LLM type"}

        system_prompt = """You are an AI assistant specialized in vehicle diagnostics, particularly in interpreting OBD-II message codes."""
        match assistantmessages.status:
            case "Connecting":
                system_prompt = f"""You are an AI assistant specializing in vehicle diagnostics. 
	                                Your first task is to kindly greet the user and inform him that you will start the connection with the vehicle using the OBD2 port through a Bluetooth connection.
	                                Then you must inform them that you found a vehicle with the VIN '{assistantmessages.vin}', explain what type of vehicle this VIN code corresponds to
                                    Guidelines:
                                    Style: Give a short and simple answer, not more than two sentences.
                                    Maintain a formal tone in all interactions.
                                    User Knowledge Level: Adapt explanations based on simple terms and provide basic explanations.
                                    Expertise: Demonstrate in-depth knowledge of vehicle systems and OBD-II codes.
                                    
                                    """
            case "ScanVehicle" | "Explain":
                system_prompt = f"""You are an AI assistant specialized in vehicle diagnostics, particularly in interpreting OBD-II message codes. Your role is to assist users by performing a triage of the provided OBD-II code, offering information about the code’s implications, and indicating the severity of the issue. 
                                    Triage: Use the OBD-II code to assess the situation and provide a clear recommendation: Red: Serious issue, stop the vehicle immediately and seek assistance. Yellow: Caution, visit a service center soon. Green: No immediate action is required, the issue is not critical.
                                    This system will help users understand whether they need to visit a service center immediately if they should stop driving the vehicle, or if the issue is not urgent. 
                                    When the user asks about a red light in the dashboard, we are sure that the root cause is the error code {', '.join(assistantmessages.codes)}. 
                                    You should then explain what the error code {', '.join(assistantmessages.codes)} means and proceed the triage result based on the {', '.join(assistantmessages.codes)} error code. 
                                    Give a short and simple answer, not more than two sentences. Maintain a formal tone in all interactions.
                                """;
                
                """You are an AI assistant specialized in vehicle diagnostics, particularly in interpreting OBD-II message codes. 
                                    Your role is to assist users by performing a triage of the provided OBD-II code, offering information about the code’s implications, and indicating the severity of the issue using a traffic light system. 
                                    This system will help users understand whether they need to visit a service center immediately if they should stop driving the vehicle, or if the issue is not urgent.
                                    The vehicle has a list of error codes:
                                    {', '.join(assistantmessages.codes)}
                                    Triage: Use the OBD-II code to assess the situation and provide a clear recommendation:
                                    Red: Serious issue, stop the vehicle immediately and seek assistance.
                                    Yellow: Caution, visit a service center soon.
                                    Green: No immediate action is required, the issue is not critical.
                                    Guidelines:
                                    Style: Give a short and simple answer, not more than two sentences.
                                    Maintain a formal tone in all interactions.
                                    User Knowledge Level: Adapt explanations based on simple terms and provide basic explanations.
                                    Expertise: Demonstrate in-depth knowledge of vehicle systems and OBD-II codes.
                                    """
            case "Summarize":
                system_prompt = f"""You are an AI assistant specialized in vehicle diagnostics, particularly in interpreting OBD-II message codes. Your role is to assist users by performing a triage of the provided OBD-II code, offering information about the code’s implications, and indicating the severity of the issue. 
                                    Triage: Use the OBD-II code to assess the situation and provide a clear recommendation: Red: Serious issue, stop the vehicle immediately and seek assistance. Yellow: Caution, visit a service center soon. Green: No immediate action is required, the issue is not critical.
                                    This system will help users understand whether they need to visit a service center immediately if they should stop driving the vehicle, or if the issue is not urgent. 
                                    When the user asks about a red light in the dashboard, we are sure that the root cause is the error code {', '.join(assistantmessages.codes)}. 
                                    You should then explain what the error code {', '.join(assistantmessages.codes)} means and proceed the triage result based on the {', '.join(assistantmessages.codes)} error code. 
                                    Give a short and simple answer, not more than two sentences. Maintain a formal tone in all interactions.
                                """
                """You are an AI assistant specialized in vehicle diagnostics, particularly in interpreting OBD-II message codes. 
                                you should summarize the issue found, offering information about the code’s implications, and indicating the severity of the issue using a traffic light system. 
                                This system will help users understand whether they need to visit a service center immediately, 
                                if they should stop driving the vehicle, or if the issue is not urgent.
                                Red: Serious issue, stop the vehicle immediately and seek assistance.
                                Yellow: Caution, visit a service center soon.
                                Green: No immediate action required, the issue is not critical.
                                Guidelines:
                                Style: Give a short and simple answer, not more than two sentences.
                                Maintain a formal tone in all interactions.
                                User Knowledge Level: Adapt explanations based on simple terms and provide basic explanations.
                                Expertise: Demonstrate in-depth knowledge of vehicle systems and OBD-II codes.
                                """
            case "Appointment":
                latitude = 4.678967
                longitude = -74.044615
                system_prompt = f"""You are an AI assistant specialized in vehicle diagnostics, particularly in interpreting OBD-II message codes. Your role is to assist users by performing a triage of the provided OBD-II code, offering information about the code’s implications, and indicating the severity of the issue. 
                                    Triage: Use the OBD-II code to assess the situation and provide a clear recommendation: Red: Serious issue, stop the vehicle immediately and seek assistance. Yellow: Caution, visit a service center soon. Green: No immediate action is required, the issue is not critical.
                                    This system will help users understand whether they need to visit a service center immediately if they should stop driving the vehicle, or if the issue is not urgent. 
                                    When the user asks about a red light in the dashboard, we are sure that the root cause is the error code {', '.join(assistantmessages.codes)}. 
                                    You should then explain what the error code {', '.join(assistantmessages.codes)} means and proceed the triage result based on the {', '.join(assistantmessages.codes)} error code. 
                                    Give a short and simple answer, not more than two sentences. Maintain a formal tone in all interactions.
                                """
                """You are an AI assistant specializing in vehicle diagnostics.
                                    you should offer to schedule an appointment at the nearest service center to address the issue found.
                                    The user's current location is latitude {latitude} and longitude {longitude}.
                                    you should indicate the maintenance, replacement or repair of the parts, the cost of the service and it was programing for the next saturday
                                    Give a short and simple answer, not more than two sentences.
                                    Maintain a formal tone in all interactions.
                                    User Knowledge Level: Adapt explanations based on simple terms and provide basic explanations.
                                """
            case _: #"Start"
                system_prompt =  f"""You are an AI assistant specialized in vehicle diagnostics, particularly in interpreting OBD-II message codes. Your role is to assist users by performing a triage of the provided OBD-II code, offering information about the code’s implications, and indicating the severity of the issue. 
                                    Triage: Use the OBD-II code to assess the situation and provide a clear recommendation: Red: Serious issue, stop the vehicle immediately and seek assistance. Yellow: Caution, visit a service center soon. Green: No immediate action is required, the issue is not critical.
                                    This system will help users understand whether they need to visit a service center immediately if they should stop driving the vehicle, or if the issue is not urgent. 
                                    When the user asks about a red light in the dashboard, we are sure that the root cause is the error code {', '.join(assistantmessages.codes)}. 
                                    You should then explain what the error code {', '.join(assistantmessages.codes)} means and proceed the triage result based on the {', '.join(assistantmessages.codes)} error code. 
                                    Give a short and simple answer, not more than two sentences. Maintain a formal tone in all interactions.
                                """
                """You are an AI assistant specializing in vehicle diagnostics. 
                                    Your first task is to kindly greet the user and inform him that you will start the connection with the vehicle using the OBD2 port through a Bluetooth connection.
                                    Guidelines:
                                    Style: Give a short and simple answer, not more than two sentences.
                                    Maintain a formal tone in all interactions.
                                    User Knowledge Level: Adapt explanations based on simple terms and provide basic explanations.
                                    Expertise: Demonstrate in-depth knowledge of vehicle systems and OBD-II codes.
                                    """
        print("system_prompt: " + system_prompt)
        response = llm_strategy.generate_assistant_chat_messages(system_prompt, assistantmessages.messages)
        assistantmessages.messages.append({"role": "assistant", "content": response})
        print("assistantmessages: ")
        print(assistantmessages)

        return assistantmessages.messages, response
            

    def generate_response_image(self, prompt, image):
        headers = {
        "Content-Type": "application/json",
        "api-key":settings.VISION_API_KEY
        }
        # Payload for the request
        payload = {
        "messages": [
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "you are an assistant for a blind person, your task is to help and be friendly."
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f"you should help with the next requirement: {prompt} and you are currently seeing the image attached below."
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}"
                }
                }
            ]
            },
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
        }

        ENDPOINT = f"{settings.VISION_API_ENDPOINT}/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview"
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        result = response.json()
        answer =result['choices'][0]['message']['content']
        return answer