import os
from dotenv import load_dotenv
#from app.services.persistence.chromadb_service import get_chromadb_collection, store_chromadb_collection, delete_chromadb_collection, chroma_query
from app.services.persistence.azure_search_service import get_azure_collection, store_azure_collection, delete_azure_collection, create_index_if_not_exists, query_azure_search


def store_collection (collection_name, ids, titles, urls, documents):

    load_dotenv()
    type = os.getenv('TYPE_DATABASE')
    project = os.getenv('PROJECT_NAME')

    if type == 'azure_search':
        create_index_if_not_exists(collection_name)
        collection = store_azure_collection(collection_name, project, ids, titles, urls, documents)
        documents = []
        for element in collection:
            documents.append(element["content"])
        return documents

    #else:
    #    collection = store_chromadb_collection(collection_name, ids, metadatas, documents)
    #    return collection.get()["documents"]


def get_collection(collection_name):

    load_dotenv()
    type = os.getenv('TYPE_DATABASE')
    project = os.getenv('PROJECT_NAME')

    if type == 'azure_search':
        return get_azure_collection(collection_name, project)
    #else:
    #    return get_chromadb_collection(collection_name)


def delete_collection(collection_name):

    load_dotenv()
    type = os.getenv('TYPE_DATABASE')
    project = os.getenv('PROJECT_NAME')

    if type == 'azure_search':
        return delete_azure_collection(collection_name, project)
    #else:
    #    return delete_chromadb_collection(collection_name)

def semantic_query(collection_name, text_query):

    load_dotenv()
    type = os.getenv('TYPE_DATABASE')
    project = os.getenv('PROJECT_NAME')

    if type == 'azure_search':
        return query_azure_search(collection_name, project, text_query)
    #else:
    #    return chroma_query(collection_name, text_query)
    