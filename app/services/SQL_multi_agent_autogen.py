import os
from dotenv import load_dotenv
from openai import OpenAI
import autogen
import pyodbc


class AutogenSQLService:
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

    admin_prompt = "Admin"

    data_engineer_prompt = '''Do not change user input. You have the opportunity to advise the Admin on selecting the appropriate function, along with the required arguments. The "query_maker" function is designed to accept human input as an argument and construct the SQL query. Meanwhile, the "run_sql_query" function is responsible for executing the query. Please refrain from independently crafting SQL queries.
    Once you receive the results from the Admin in response to the SQL query, ensure that you interpret them accurately. You are also authorized to create SQL queries tailored to user input. Subsequently, execute the query and provide the results. In the event of any errors, please rectify them and rerun the query, and then present the answer.
    If the sql query result is empty, then just say we do not have this mobile in our stock.
    '''

    # Configuration for using Azure agents
    gpt_turbo_config = {
            "temperature": 0.7,
            "functions": [
                {
                    "name": "query_maker",
                    "description": "Generates SQL query as per user input",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_input": {"type": "string", "description": "This is the input from the user side."},
                        },
                        "required": ["user_input"],
                    },
                },
                {
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
            ]
        }

    llm_config = {
        "timeout": 600,
        "cache_seed": 44,  # change the seed for different trials
        "config_list": autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={"model": ["gpt-4"]},
        ),
        "temperature": 0,
        "functions": [
            {
                "name": "query_maker",
                "description": "Generates SQL query using sentences SQL as per user input",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_input": {"type": "string", "description": "This is the input from the user side."},
                    },
                    "required": ["user_input"],
                },
            },
            {
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
        ]
    }

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
    
    """
    def is_termination_msg(content):
        have_content = content.get("content", None) is not None
        if have_content and "Approved" in content["content"]:
            return True
        else:
            return False
    """

    def is_termination_msg(content):
        return content.get("content") is not None and "Approved" in content["content"]

    def generate_sql_query(self, task: str):
        # Load environment variables
        load_dotenv()

        # Placeholder for examples of admin and engineer prompts
        function_map_list = {"query_maker": self.query_maker, "run_sql_query": self.run_sql_query}
        termination_msg = "If everything looks good, respond with Approved."
        
        user_proxy = autogen.UserProxyAgent(
            name="Admin",
            system_message = self.admin_prompt + termination_msg,
            human_input_mode = "NEVER",
            code_execution_config=False,
            is_termination_msg = lambda content: content.get("content") is not None and "Approved" in content["content"],
        )

        engineer = autogen.AssistantAgent(
            name="Data_Engineer",
            llm_config = self.llm_config,
            system_message = self.data_engineer_prompt + termination_msg,
            function_map = function_map_list
        )

        # Register the functions
        user_proxy.register_function(function_map=function_map_list)

        # Initiate chat
        user_proxy.initiate_chat(engineer, message=task, silent=True)

        #user_proxy_chat = user_proxy.chat_messages
        engineer_chat = engineer.chat_messages
        #print(user_proxy_chat)
        #print(engineer_chat)

        engineer_summary = str(engineer_chat)
        engineer_result = ""

        for element in engineer_chat.values():
            #print(f" {str(element)} ")
            
            for message in element:
                if(message.get('name') == 'Data_Engineer' and 'approved' not in str(message.get('content')).lower()):
                    #print(f" {message.get('content')} ")
                    engineer_summary = message.get('content')
                
                if(message.get('name') == 'run_sql_query' and message.get('role') == 'function'):
                    #print(f" {message.get('content')} ")
                    engineer_result = message.get('content')

        #print(f" {engineer_summary} ")
        #print(f" {engineer_result} ")

        return engineer_summary, engineer_result


if __name__ == "__main__":
    autogen_service = AutogenSQLService()
    #autogen_service.generate_sql_query("How many Apple pro vision we have in our stock?")
    autogen_service.generate_sql_query("Give me the specs and quantity of Air Force")
