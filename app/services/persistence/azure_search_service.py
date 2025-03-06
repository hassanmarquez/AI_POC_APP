import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery

# load environment variables
load_dotenv()

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]


def get_embeddings(text: str):
    # There are a few ways to get embeddings. This is just one example.
    import openai

    open_ai_endpoint = os.getenv("AZURE_ENDPOINT")
    open_ai_key = os.getenv("AZURE_API_KEY")
    open_ai_version = os.getenv("AZURE_API_VERSION")
    open_ai_embedding_model = os.getenv("DEPLOYMENT_EMBEDDING_MODEL")

    client = openai.AzureOpenAI(
        azure_endpoint = open_ai_endpoint,
        api_key        = open_ai_key,
        api_version    = open_ai_version,
    )
    embedding = client.embeddings.create(
        input = [text], 
        model = open_ai_embedding_model
    )
    return embedding.data[0].embedding


def get_document_index(name: str):
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SearchField,
        SearchFieldDataType,
        SimpleField,
        SearchableField,
        VectorSearch,
        VectorSearchProfile,
        HnswAlgorithmConfiguration,
    )

    fields = [
        SimpleField(
            name = "id", 
            type = SearchFieldDataType.String, 
            key  = True),
        SearchableField(
            name = "project", 
            type = SearchFieldDataType.String,
            filterable=True),
        SearchableField(
            name = "title", 
            type = SearchFieldDataType.String,
            filterable=True),            
        SearchableField(
            name = "url", 
            type = SearchFieldDataType.String),
        SearchableField(
            name = "content", 
            type = SearchFieldDataType.String),                        
        SearchField(
            name = "documentVector",
            type = SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable = True,
            vector_search_dimensions   = 1536,
            vector_search_profile_name = "my-vector-config",
        )
    ]

    vector_search = VectorSearch(
        profiles=[
            VectorSearchProfile(
                name = "my-vector-config", 
                algorithm_configuration_name = "my-algorithms-config"
            )
        ],
        algorithms = [HnswAlgorithmConfiguration(name = "my-algorithms-config")],
    )

    return SearchIndex(name   = name, 
                       fields = fields, 
                       vector_search = vector_search)


def create_index_if_not_exists(index_name):
    print(f"create_index_if_not_exists {index_name}")
    search_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    if not index_name in search_client.list_index_names():
        print(f"Creating index ... {index_name}")
        index = get_document_index(index_name)
        search_client.create_index(index)


def upload_azure_search_document(index_name, project, title, url, document_text):
    create_index_if_not_exists(index_name)
    import uuid
    id = str(uuid.uuid4())[-6:]
    credential = AzureKeyCredential(key)
    client = SearchClient(service_endpoint, index_name, credential)
    docs = [
    {
        "id": id,
        "project": project,
        "title": title,
        "url": url,
        "content": document_text,
        "documentVector": get_embeddings(document_text),
    }]
    client.upload_documents(documents=docs)


def update_azure_search_document(index_name, document):
    create_index_if_not_exists(index_name)
    credential = AzureKeyCredential(key)
    search_client = SearchClient(service_endpoint, index_name, credential)
    document["documentVector"] = get_embeddings(document["content"])
    result = search_client.upload_documents(documents=[document])
    print("Upload of new document succeeded: {}".format(result[0].succeeded))


def upload_azure_search_documents_list(index_name, docs):
    create_index_if_not_exists(index_name)
    #import uuid
    #id = str(uuid.uuid4())[-6:]
    credential = AzureKeyCredential(key)
    client = SearchClient(service_endpoint, index_name, credential)
    #print(f"loading documents ... {docs}")
    client.upload_documents(documents=docs)


def store_azure_collection(index_name, project, ids, titles, urls, documents):
    docs = []
    for i in range(len(documents)):
        document = {
            "id": ids[i],
            "project": project,
            "title": titles[i],
            "url": urls[i],
            "content": documents[i],
            "documentVector": get_embeddings(documents[i]),
        }
        docs.append(document)
    #print(f"store_azure_collection {docs}")
    upload_azure_search_documents_list(index_name, docs)
    return docs


def get_azure_collection(index_name):
    collection = search_all_documents(index_name)
    documents = []
    try:
        for element in collection:
            documents.append(element["content"])
    except Exception as e:
        print(f"Error get_azure_collection {str(e)}")
        return []
    return documents


def delete_azure_collection(index_name):
    try:
        search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
        results = search_client.search(
            select = ["id", "project", "title", "url", "content"],
        )
        document_list = list(results)
        #print(f"delete_azure_collection {document_list}")
        result = search_client.delete_documents(documents=document_list)
        print("deletion of document succeeded: {}".format(result[0].succeeded))
        return True
    except Exception as e:
        print(f"delete_azure_collection {str(e)}")
        return False


def search_all_documents(index_name):
    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    results = search_client.search(
        select = ["id", "project", "title", "url", "content"],
    )
    return results


def vector_search(index_name, text_query):

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    vector_query = VectorizedQuery(
        vector = get_embeddings(text_query), k_nearest_neighbors=3, fields="documentVector"
    )

    results = search_client.search(
        vector_queries = [vector_query],
        select = ["id", "project", "title", "url", "content"],
    )
    
    return results


def vector_search_with_filter(index_name: str, query: str, filter: str):
    # [START single_vector_search_with_filter]
    # query = "Top hotels in town"
    # filter= "category eq 'Luxury'"

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    vector_query = VectorizedQuery(
        vector=get_embeddings(query), k_nearest_neighbors=3, fields="documentVector"
    )

    results = search_client.search(
        search_text = "",
        vector_queries = [vector_query],
        filter = filter,
        select = ["id", "project", "title", "url", "content"],
    )

    for result in results:
        print(result)
    # [END single_vector_search_with_filter]


def search_with_filter(index_name: str, filter: str):
    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    results = search_client.search(
        filter = filter,
        select = ["id", "project", "title", "url", "content"],
    )
    return results

def search_by_title(index_name: str, project: str, title: str):
    create_index_if_not_exists(index_name)
    filter = f"title eq '{title}' and project eq '{project}'"
    results = search_with_filter(index_name, filter)
    for result in results:
        return result
    return


def query_azure_search(index_name, text_query):
    collection = vector_search(index_name, text_query)
    
    documents = []
    try:
        for element in collection:
            if element['@search.score'] > 0.8:
                documents.append(element["content"])
    except Exception as e:
        print(f"Error get_azure_collection {str(e)}")
        return []
    return documents
