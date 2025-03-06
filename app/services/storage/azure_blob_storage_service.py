from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from dotenv import load_dotenv

class AzureBlobStorage:
    def __init__(self, connection_string, container_name):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    def list_blobs(self):
        try:
            blobs_list = self.container_client.list_blobs()
            return [blob.name for blob in blobs_list]
        except Exception as e:
            print(f"Error in listing blobs: {e}")
            return []

    def read_blob(self, blob_name):
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob()
            content = blob_data.readall()
            return content  #if the blod is txt file we should add .decode('utf-8')  
        except Exception as e:
            print(f"Error in reading blob {blob_name}: {e}")
            return None

    def upload_blob(self, blob_name, data):
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data, overwrite=True)
            print(f"Blob {blob_name} uploaded successfully.")
        except Exception as e:
            print(f"Error in uploading blob {blob_name}: {e}")

if __name__ == "__main__":
    # load environment vars
    load_dotenv()

    # Example usage:
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')

    if not connection_string:
        raise ValueError("Please set the AZURE_STORAGE_CONNECTION_STRING environment variable.")

    azure_blob_storage = AzureBlobStorage(connection_string, container_name)

    # List blobs
    blobs = azure_blob_storage.list_blobs()
    print("Blobs in container:")
    for blob in blobs:
        print(blob)

    # Read a specific blob
    blob_name = "example.txt"
    content = azure_blob_storage.read_blob(blob_name)
    if content:
        print(f"Content of {blob_name}:")
        print(content)

    # Upload a new blob
    new_blob_name = "new_example.txt"
    data = "This is a sample content for the new blob."
    azure_blob_storage.upload_blob(new_blob_name, data)
