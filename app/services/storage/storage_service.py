import os
from io import BytesIO
from dotenv import load_dotenv
from app.services.storage.azure_blob_storage_service import AzureBlobStorage
#from storage.azure_blob_storage_service import AzureBlobStorage
import PyPDF2


def load_document_blod(name, file_bytes):
    
    load_dotenv()
    type = os.getenv('TYPE_STORAGE')

    if type == 'azure':

        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
        if not connection_string:
            raise ValueError("Please set the AZURE_STORAGE_CONNECTION_STRING environment variable.")
        azure_blob_storage = AzureBlobStorage(connection_string, container_name)
        azure_blob_storage.upload_blob(name, file_bytes)

    else:

        documents_path = os.getenv("UPLOAD_FOLDER")
        #print(os.path.join(documents_path, name))
        with open(os.path.join(documents_path, name), "wb") as f:
            f.write(file_bytes)


def get_document_list():

    load_dotenv()
    type = os.getenv('TYPE_STORAGE')

    if type == 'azure':

        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
        if not connection_string:
            raise ValueError("Please set the AZURE_STORAGE_CONNECTION_STRING environment variable.")
        azure_blob_storage = AzureBlobStorage(connection_string, container_name)
        profiles_list = azure_blob_storage.list_blobs()
        print(profiles_list)
        return profiles_list

    else:

        path = os.getenv("UPLOAD_FOLDER")
        profiles_list = os.listdir(path)
        print(profiles_list)
        return profiles_list


def read_pdf_document(file_name):

    load_dotenv()
    type = os.getenv('TYPE_STORAGE')

    if type == 'azure':

        text = ''
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
        if not connection_string:
            raise ValueError("Please set the AZURE_STORAGE_CONNECTION_STRING environment variable.")
        azure_blob_storage = AzureBlobStorage(connection_string, container_name)
        content = azure_blob_storage.read_blob(file_name)
        if content:
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    else:

        text = ''
        path = os.getenv("UPLOAD_FOLDER")
        path_file = os.path.join(path, file_name)
        with open(path_file, "rb") as content:
            pdf_reader = PyPDF2.PdfReader(content)
            for page_number in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_number].extract_text()
        return text

