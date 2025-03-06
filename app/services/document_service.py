import os 
import io
from PyPDF2 import PdfReader
import pandas as pd
import requests
from app.services.persistence.azure_search_service import upload_azure_search_document, update_azure_search_document, search_by_title, vector_search

def read_document(document_name):

    path = os.getenv("AZURE_DATA_STORE_PATH")
    path_file = os.path.join(path, document_name)

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
    response = requests.get(url=path_file, headers=headers, timeout=200)
    pdf_file = io.BytesIO(response.content)
    pdf_reader = PdfReader(pdf_file)
    document_text = ""

    # loop over PDF pages
    for page_number in range(len(pdf_reader.pages)):
        document_text += pdf_reader.pages[page_number].extract_text()

    return path_file, document_text


def save_document(document_title, document_url, document_text):

    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    project = os.getenv('PROJECT_NAME')

    # check if the document exists
    document = search_by_title(index_name, project, document_title)
    if document == None:
        upload_azure_search_document(index_name, project, document_title, document_url, document_text)    
    else:
        document["title"] = document_title
        document["url"] = document_url
        document["content"] = document_text
        update_azure_search_document(index_name, document)


def search_documents(key_words):
    
    id = []
    title = []
    link = []
    content = []
    list_documents = vector_search(key_words)
    
    for document in list_documents:
        if document['@search.score'] > 0.8:
            print(document)
            id.append(document["id"])
            title.append(document["title"]) 
            link.append(document["url"]) 
            content.append(document["content"])

    data_df = pd.DataFrame({ 
        "Id": id, 
        "Title": title, 
        "Link": link,
        "Content": content })

    return data_df


def scrape_text(url):
    import requests
    from bs4 import BeautifulSoup    
    
    # Send a GET request to the URL
    response = requests.get(url)

    # If the GET request is successful, the status code will be 200
    if response.status_code == 200:
        # Get the content of the response
        page_content = response.content

        # Create a BeautifulSoup object and specify the parser
        soup = BeautifulSoup(page_content, "html.parser")

        # Get the text of the soup object
        text = soup.get_text()

        # Return the text
        return text
    else:
        return "Failed to scrape the website"