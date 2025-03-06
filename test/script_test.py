import requests
import os
import base64

def test_uploadimage():
    url = 'http://127.0.0.1:5000/assistent/loadimage'
    # Specify the content type
    #headers = {'Content-Type': 'application/octet-stream'}
    headers = {}

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates\\screen.png')

    files = {'file': (os.path.basename(path), open(path, 'rb').read(),
                        'multipart/form-data')}

    #json = {'file': 'screen.png', 'prompt': 'identificar elementos en la imagen'}

    print(url)
    print(headers)
    #print(file)

    response = requests.post(url, headers=headers, files=files)

    print(response.text)
    print("Status Code", response.status_code)
    print("JSON Response ", response.json())


def test_command():
    
    url = 'http://127.0.0.1:5000/assistent/command'
    headers = {'Content-Type': 'application/json'}

    path = os.path.abspath(os.path.dirname(__file__)) + '\\static\\files\\street_bus.jpg'
    #print(f"path {path}")
    with open(path, "rb") as original_file:
        encoded_string = base64.b64encode(original_file.read()).decode("utf8")
        #print(f"encoded_string {encoded_string}")

    json = {'fileName': 'meeting.jpg',
            'file': encoded_string, 
            'prompt': 'Identify elements into the image'}
    #print(json)
    response = requests.post(url, headers=headers, json=json)

    print(response.text)
    print("Status Code", response.status_code)
    print("JSON Response ", response.json())
    return

if __name__ == '__main__':
    #test_uploadimage()
    test_command()
