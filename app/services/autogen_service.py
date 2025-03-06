import autogen
from autogen import Agent, AssistantAgent, ConversableAgent, UserProxyAgent
from autogen.agentchat.contrib.web_surfer import WebSurferAgent
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen import UserProxyAgent, GroupChat, GroupChatManager
from autogen import register_function
import httpx
from typing import Annotated
from openai import OpenAI
import requests
import json
import agentops

#from SQL_multi_agent_autogen import AutogenSQLService
from app.models.llm_model import AnalysisDataRequest
from app.services.SQL_multi_agent_autogen import AutogenSQLService
from app.services.analysis_data_service import AnalysisService

#funtions regions to register on LLM
def get_current_weather(
        lat: Annotated[float, "Latitude of the weather location"],
        lon: Annotated[float, "Longitude of the weather location"],
    ) -> dict:

    base_url = "https://api.openweathermap.org/data/3.0/onecall"
    OPENWEATHER_API_KEY = "sk-u4V8dGD5v1fSLgtYP-j7Jwz6wdBRu7XHG52EpWoNFxT3BlbkFJ0gkbtuVQpj5b_Pkh4pT80La_aofoLYCZvvvZQGWAEA"
    arguments = f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"

    endpoint = f"{base_url}{arguments}"
    response = httpx.get(endpoint)

    return response.json()

def get_image_identification(
        file_name: Annotated[str, "File name"]
) -> str:    
    headers = {
        "Prediction-Key": "791155aeea964392804e4940cfb38c88",
        "Content-Type": "application/octet-stream"
    }
    filename = "image_retail.png"
    image_file = open(filename, "rb")
    ENDPOINT = f"https://eastus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/6f32cd00-e698-4665-9d61-85bf6e9f2865/classify/iterations/Iteration2/image"
    response = requests.post(ENDPOINT, headers=headers, data=image_file)
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    print(response.json())
    return str(response.json())
#end funtions region


class AutogenService:

    analysis_service = AnalysisService()

    def generate_image_description(self, image_path, task: str):
        config_list_4v = autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={
                "model": ["gpt-4-vision-preview"],
            },
        )

        config_list_gpt4 = autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={
                "model": ["gpt-4"],
            },
        )

        llm_config = {
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list_gpt4,
            "temperature": 0
        }

        summarizer_llm_config = {
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list_gpt4,
            "temperature": 0
        }

        bing_api_key = "88fe301c73b34ee0ba66aa3dad69fbb3"

        user_proxy = autogen.UserProxyAgent(
            name="User_proxy",
            system_message="A human admin.",
            human_input_mode="NEVER",  # Try between ALWAYS or NEVER
            max_consecutive_auto_reply=0,
            code_execution_config={
                "use_docker": False
            },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
        )

        # Initialize Multimodal Agent for image analysis
        image_agent = MultimodalConversableAgent(
            name="image-explainer",
            max_consecutive_auto_reply=10,
            llm_config={"config_list": config_list_4v, "temperature": 0.5, "max_tokens": 300},
            #llm_config=gpt4_llm_config
        )

        # Initialize WebSurfer Agent for product search
        web_surfer = WebSurferAgent(
        "web_surfer",
        description="Search for stores based on the output of the summarizer agent",
        system_message="Search for stores based on the output of the summarizer agent",
        llm_config=llm_config,
        summarizer_llm_config=summarizer_llm_config,
        browser_config={
            "viewport_size": 4096,
            "bing_api_key": bing_api_key
        }
        )

        summarizer_agent = AssistantAgent(
            "summarizer",
            description="Summarises the response provided by the image-explainer agent",
            system_message="Explain the output from the image explainer. Provide historical information in one sentence",
            llm_config={"config_list": config_list_gpt4, "cache_seed": 42},
            human_input_mode="NEVER",  # Never ask for human input.
        )

        formatter_agent = AssistantAgent(
            "formatter",
            description="Formats the output from the web_surfer in a few words and in a Json way before sending the response to the user.",
            system_message="Format the output from the summarizer in Json format. When you are done you have to say the word TERMINATE",
            llm_config={"config_list": config_list_gpt4, "cache_seed": 42},
            human_input_mode="NEVER",  # Never ask for human input.
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"].lower(),
        )

        # Set up GroupChat and GroupChatManager
        group_chat = GroupChat(
            agents=[user_proxy, image_agent, web_surfer, summarizer_agent, formatter_agent],
            messages=[],
            max_round=5
        )

        group_chat_manager = GroupChatManager(
            groupchat=group_chat,
            llm_config={"config_list": config_list_gpt4, "cache_seed": 42}
        )

        chat_result = user_proxy.initiate_chat(
            group_chat_manager,
            message = f"""{task}: 
            <img src="{image_path}">"""
        )

        return (chat_result.summary, json.dumps(chat_result.chat_history))

    def generate_websurfer(self, task: str):

        bing_api_key = "88fe301c73b34ee0ba66aa3dad69fbb3"
        
        config_list = [
            {
                "model": "gpt-4",
                "api_key": "b0d3e6aebc2d4e00b2e76fa9faf8b66a",
                "base_url": "https://aihackathoneastcan.openai.azure.com/",
                "api_type": "azure",
                "api_version": "2024-05-01-preview"
            }
        ]
        
        llm_config={
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
        }
        
        summarizer_llm_config={
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
        }

        from autogen.agentchat.contrib.web_surfer import WebSurferAgent  # noqa: E402
        
        web_surfer = WebSurferAgent(
            "web_surfer",
            llm_config=llm_config,
            summarizer_llm_config=summarizer_llm_config,
            browser_config={"viewport_size": 4096, "bing_api_key": bing_api_key},
        )
        
        user_proxy = autogen.UserProxyAgent(
            "user_proxy",
            human_input_mode="NEVER",
            code_execution_config=False,
            default_auto_reply="",
            is_termination_msg=lambda x: True,
        )
        
        chat_result = user_proxy.initiate_chat(web_surfer, message=task, silent=True)
        return chat_result.summary

    def generate(self, task: str):
        
        llm_config = {
            "timeout": 600,
            "cache_seed": 44,  # change the seed for different trials
            "config_list": autogen.config_list_from_json(
                "OAI_CONFIG_LIST",
                filter_dict={"model": ["gpt-4", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0613", "gpt-4-1106-preview"]},
            ),
            "temperature": 0,
        }
        
        summarizer_llm_config = {
            "timeout": 600,
            "cache_seed": 44,  # change the seed for different trials
            "config_list": autogen.config_list_from_json(
                "OAI_CONFIG_LIST",
                filter_dict={"model": ["gpt-3.5-turbo-1106", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]},
            ),
            "temperature": 0,
        }
        
        bing_api_key = "88fe301c73b34ee0ba66aa3dad69fbb3"
        
        config_list = [
            {
                "model": "gpt-4",
                "api_key": "b0d3e6aebc2d4e00b2e76fa9faf8b66a",
                "base_url": "https://aihackathoneastcan.openai.azure.com/",
                "api_type": "azure",
                "api_version": "2024-05-01-preview"
            }
        ]
        
        llm_config={
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
        }
        
        summarizer_llm_config={
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
        }

        from autogen.agentchat.contrib.web_surfer import WebSurferAgent  # noqa: E402

        web_surfer = WebSurferAgent(
            "web_surfer",
            llm_config=llm_config,
            summarizer_llm_config=summarizer_llm_config,
            browser_config={"viewport_size": 4096, "bing_api_key": bing_api_key},
        )
        
        user_proxy = autogen.UserProxyAgent(
            "user_proxy",
            human_input_mode="NEVER",
            code_execution_config=False,
            default_auto_reply="",
            is_termination_msg=lambda x: True,
        )
        
        #task1 = """
        #Search the web for information about NBA news ONLY related to the date August, 10 2024.
        #"""
        
        chat_result = user_proxy.initiate_chat(web_surfer, message=task, silent=True)
        return chat_result.summary

    def generate_api(self, task: str):
        
        llm_config = {
            "timeout": 600,
            "cache_seed": 44,  # change the seed for different trials
            "config_list": autogen.config_list_from_json(
                "OAI_CONFIG_LIST",
                filter_dict={"model": ["gpt-4"]},
            ),
            "temperature": 0,
        }
                
        image_assistant = AssistantAgent(
            name="Image Assistant",
            system_message="You are a helpful AI for identify content in an image. "
            "You can help by providing the probability of an image as the same type of object based on available model data."
            "Return 'TERMINATE' when the task is done.",
            llm_config=llm_config,
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"].lower(),
        )

        user_proxy = ConversableAgent(
            name="User",
            llm_config=False,
            default_auto_reply="Make an API request to get the product detail",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )

        register_function(
            get_image_identification,
            caller=image_assistant,
            executor=user_proxy,
            name="get_image_identification",
            description="A tool for obtaining image information. Identify if the probability of image given is the same type.",
        )

        chat_result = user_proxy.initiate_chat(image_assistant, message=task, silent=True)

        return chat_result.summary

    def generate_simple(self, task:str):
        from openai import OpenAI

        api_key = "sk-u4V8dGD5v1fSLgtYP-j7Jwz6wdBRu7XHG52EpWoNFxT3BlbkFJ0gkbtuVQpj5b_Pkh4pT80La_aofoLYCZvvvZQGWAEA"
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create (
            model = "gpt-4o",
            messages=[            
                    {"role": "system", 
                     "content": "You are and AI Assitent and you should give advices about products"},
                    {"role": "user", 
                     "content": task}        
                ],        
                temperature=0.7    
            )    
        result = response.choices[0].message.content.strip()
        return result

    def get_retail_search_service(self, image_path):
        
        # When initializing AgentOps, you can pass in optional tags to help filter sessions
        agentops.init(default_tags=["retail-example-V1"], api_key="c208bb26-4e76-4b63-91ea-d2644d5a3dbe")
        
        llm_config = {
            "timeout": 600,
            "cache_seed": 44,  # change the seed for different trials
            "config_list": autogen.config_list_from_json(
                "OAI_CONFIG_LIST",
                filter_dict={"model": ["gpt-4o"]},
            ),
            "temperature": 0,
        }

        image_assistant = AssistantAgent(
            name="Image Assistant",
            system_message="You are a helpful AI for identify content in an image. "
            "You can help by providing the probability of an image as the same type of object based on available model data."
            "Return 'TERMINATE' when the task is done.",
            llm_config=llm_config,
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"].lower(),
        )

        user_proxy = ConversableAgent(
            name="User",
            llm_config=False,
            default_auto_reply="Make an API request to get the product detail",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )

        register_function(
            get_image_identification,
            caller=image_assistant,
            executor=user_proxy,
            name="get_image_identification",
            description="A tool for obtaining image information. Identify if the probability of image given is the same type.",
        )

        chat_result = user_proxy.initiate_chat(image_assistant, message="Identify the product in the image image_retail.jpg", silent=True)
        modelai_result = chat_result.summary

        ## genrate database result 
        autogen_database_service = AutogenSQLService()
        database_summary, database_result = autogen_database_service.generate_sql_query(f"Give me the specs, quantity and price of the product with highest probability: {modelai_result}")
        summary = self.generate_simple(f"give me the advice to use the next product in an one sentence: {database_result}")

        # Close your AgentOps session to indicate that it completed.
        agentops.end_session("Success")

        return (modelai_result, str(database_summary), str(database_result), summary)


    def get_retail_search_service_v2(self, image_path):

        # When initializing AgentOps, you can pass in optional tags to help filter sessions
        agentops.init(default_tags=["retail-example-V2"], api_key="c208bb26-4e76-4b63-91ea-d2644d5a3dbe")

        llm_config = {
            "timeout": 600,
            "cache_seed": 44,  # change the seed for different trials
            "config_list": autogen.config_list_from_json(
                "OAI_CONFIG_LIST",
                filter_dict={"model": ["gpt-4o"]},
            ),
            "temperature": 0,
        }

        llm_config_data = {
            "timeout": 600,
            "cache_seed": 44,  # change the seed for different trials
            "config_list": autogen.config_list_from_json(
                "OAI_CONFIG_LIST",
                filter_dict={"model": ["gpt-4"]},
            ),
            "temperature": 0,
            "tools" : [
                {
                    "type": "function",
                    "function": {
                        "name": "query_maker",
                        "description": "Generates SQL query using sentences SQL as per user input",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_input": {"type": "string", "description": "This is the input from the user side."},
                            },
                            "required": ["user_input"],
                        },
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "run_sql_query",
                        "description": "This function runs the SQL query against user input to get results.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "sql_query": {"type": "string", "description": "This is the SQL Server query."},
                            },
                            "required": ["sql_query"],
                        },
                    }
                }
            ]
        }

        admin_prompt = "UserProxyDB"

        user_proxy = autogen.UserProxyAgent(
            name="User_proxy",
            system_message="A human requester",
            human_input_mode="NEVER",  # Try between ALWAYS or NEVER
            max_consecutive_auto_reply=0,
            code_execution_config={
                "use_docker": False
            },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
        ) 

        user_proxy_image = ConversableAgent(
            name="User",
            llm_config=False,
            default_auto_reply="Make an API request to get the product detail",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )

        product_recognizer_agent = autogen.AssistantAgent(
            name="product_recognizer_agent",
            description = "You are a helpful AI for identify content in an image. "
                "You can help by providing the probability of an image as the same type of object based on available model data."
                "Return 'TERMINATE' when the task is done.", 
            llm_config = llm_config,
            system_message="You are a helpful AI for identify content in an image. "
                "You can help by providing the probability of an image as the same type of object based on available model data."
                "Return 'TERMINATE' when the task is done.", 
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"].lower(),
        )

        register_function(
            get_image_identification,
            caller=product_recognizer_agent,
            executor=user_proxy_image,
            name="get_image_identification",
            description="A tool for obtaining image information. Identify if the probability of image given is the same type.",
        )

        function_map_list = {"query_maker": self.query_maker, "run_sql_query": self.run_sql_query}
        termination_msg = " If everything looks good, respond with Approved."
        data_engineer_prompt = '''Do not change user input. You have the opportunity to advise the UserProxyDB on selecting the appropriate function, along with the required arguments. The "query_maker" function is designed to accept human input as an argument and construct the SQL query. Meanwhile, the "run_sql_query" function is responsible for executing the query. Please refrain from independently crafting SQL queries.
        Once you receive the results from the UserProxyDB in response to the SQL query, ensure that you interpret them accurately. You are also authorized to create SQL queries tailored to user input. Subsequently, execute the query and provide the results. In the event of any errors, please rectify them and rerun the query, and then present the answer.
        If the sql query result is empty, then just say we do not have this mobile in our stock.
        '''

        user_proxy_db = autogen.UserProxyAgent(
            name="UserProxyDB",
            description = f"You are {admin_prompt}, you should execute the SQL Query after the db_agent " +  termination_msg,
            system_message = "You should execute the SQL query given by db_agent " + termination_msg,
            human_input_mode = "NEVER",
            llm_config = llm_config_data,
            code_execution_config=False,
            is_termination_msg = lambda content: content.get("content") is not None and "Approved" in content["content"],
        )

        db_agent = autogen.AssistantAgent(
            name="db_agent",
            llm_config = llm_config_data,
            system_message = data_engineer_prompt + termination_msg,
            description = "You will receive the name of a product you will call a function to generate a SQL query to obtain all the information about the product in the product table. Then, return the information in a JSON format including the field names and the values",
            function_map = function_map_list,
        )

        # Register the functions
        user_proxy_db.register_function(function_map=function_map_list)

        adviser_agent = autogen.AssistantAgent(
            name="adviser_agent",
            system_message="""You are the last agent. You need to give advice in one sentence on how to use the product based on the information provided by the db_agent """,
            llm_config = llm_config
        )

        groupchat = autogen.GroupChat(
            agents=[user_proxy, user_proxy_image, product_recognizer_agent, user_proxy_db, db_agent, adviser_agent], messages=[], max_round=50
        )

        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config = llm_config)

        user_proxy.initiate_chat(
            manager,
            message="""Identify the product in the image image_retail.png""",
            silent=True
        )
 
        engineer_summary = ""
        engineer_result  = ""
        modelai_result   = ""
        summary          = ""

        for element in db_agent.chat_messages.values():
            #print(f"element: {str(element)} ")
            
            for message in element:
                #print(f"role: {message.get('role')} - content: {message.get('content')} - tool_calls: {str(message.get('tool_calls'))}")
                if(message.get('role') == 'assistant' and 'query_maker' in str(message.get('tool_calls'))):
                    #print(f" {message.get('content')} ")
                    modelai_result = message.get('content')
                
                if(message.get('role') == 'tool' and message.get('name') == 'UserProxyDB'):
                    #print(f" {message.get('content')} ")
                    engineer_result = message.get('content')

                if(message.get('name') == 'adviser_agent'):
                    #print(f" {message.get('content')} ")
                    summary = message.get('content')

        #print(f"engineer_summary: {engineer_summary} ")
        #print(f"engineer_result : {engineer_result} ")
        #print(f"modelai_result  : {modelai_result} ")
        #print(f"summary         : {summary} ")

        # Close your AgentOps session to indicate that it completed.
        agentops.end_session("Success")

        return (str(modelai_result), str(engineer_result), str(engineer_result), str(summary))

    query_maker_gpt_system_prompt = '''You are MySQL Query Generator. 
        Kindly generate the sql query only and use only the listed columns in below schema. 
        Do not use any column by yourself. 

        Below is the Schema of the available tables to make the sql queries. 
        Create and return only one query.

        CREATE TABLE `mobile_stock` (  
            `Product_id` int NOT NULL,  
            `Product_Name` varchar(255) DEFAULT NULL,
            `Available_Quantity` int DEFAULT NULL,  
            `Mobile_Specs` text,  
            `Price` float NOT NULL,
            PRIMARY KEY (`Product_id`),  
            FULLTEXT KEY `mobile_stock_Product_Name_IDX` 
            (`Product_Name`,`Mobile_Specs`));
            
            Use like with % for the right product match against
            Product_name column. only use the above mentioned columns in making sqlquery.
            User Input: 
            '''

    def query_maker(self, user_input):    
        # OpenAI API key
        api_key = "sk-u4V8dGD5v1fSLgtYP-j7Jwz6wdBRu7XHG52EpWoNFxT3BlbkFJ0gkbtuVQpj5b_Pkh4pT80La_aofoLYCZvvvZQGWAEA"
        #openai.api_key = api_key

        client = OpenAI(api_key=api_key)

        # Direct OpenAI API call to generate SQL query    
        response = client.chat.completions.create (
            model = "gpt-4o",
            messages=[            
                    {"role": "system", 
                        "content": self.query_maker_gpt_system_prompt},
                    {"role": "user", 
                        "content": user_input}        
                ],        
                temperature=0.7    
            )    
        query = response.choices[0].message.content.strip()
        return query

    # Function to run SQL queries on Azure SQL Database
    def run_sql_query(self, sql_query):
        import pyodbc

        AZURE_SQL_HOST='sql-logic-server.database.windows.net'
        AZURE_SQL_DATABASE='sqldatabase'
        AZURE_SQL_USER='admindb'
        AZURE_SQL_PASSWORD='4dm1ngdb!'
        
        conn_str = (
                'DRIVER={ODBC Driver 17 for SQL Server};'
                #'SERVER=' + os.getenv('AZURE_SQL_HOST') + ';'
                #'DATABASE=' + os.getenv('AZURE_SQL_DATABASE') + ';'
                #'UID=' + os.getenv('AZURE_SQL_USER') + ';'
                #'PWD=' + os.getenv('AZURE_SQL_PASSWORD') + ';'
                'SERVER=' + AZURE_SQL_HOST + ';'
                'DATABASE=' + AZURE_SQL_DATABASE + ';'
                'UID=' + AZURE_SQL_USER + ';'
                'PWD=' + AZURE_SQL_PASSWORD + ';'
            )

        try:
            # Establish the connection
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Execute the SQL query
            cursor.execute(sql_query)
            result = cursor.fetchall()

            # Close cursor and connection
            cursor.close()
            conn.close()
        except Exception as e:
            return str(e)

        return result


    async def generate_analysis_data_response(self, status :str, task: str):
        
        (image_name, summary) = await self.analysis_service.execute_command(status, task)        
        return (image_name, summary)



if __name__ == "__main__":
    autogen_service = AutogenService()
    #user_image_path = "zapatillas.jpg"
    #autogen_service.generate_image_description(user_image_path, "What's in this image")
   
    #response = autogen_service.generate_websurfer(task = "Search the web for information about NBA news ONLY related to the date August, 10 2024.")
    #print(response)

    #autogen_service.generate_api("Identify the product in the image zapatillas.jpg")

    #autogen_service.get_retail_search_service("image_retail.png")

    #autogen_service.get_retail_search_service_v2("Identify the product in the image zapatillas.jpg")

    autogen_service.generate_analysis_data_response("Generate a plot about hours worked for every vehicle in the last days")


