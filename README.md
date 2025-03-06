# AI_POC_APP

Este proyecto es el backend de la POC de un asistente Automotriz, una aplicación que utiliza modelos de lenguaje para generar respuestas y realizar otras tareas relacionadas con el procesamiento de lenguaje natural.

## Requisitos

- Python 3.13
- Git
- [Postman](https://www.postman.com/downloads/) (opcional, para probar las APIs)

## Instalación

Sigue estos pasos para clonar el repositorio, instalar las dependencias y ejecutar el servidor localmente.

### Clonar el repositorio

1. Abre una terminal.
2. Clona el repositorio desde GitHub:
   ```sh
   git clone https://github.com/hassanmarquez/AI_POC_APP.git

   cd AI_POC_APP
   ```

### Crear y activar un entorno virtual

3. Crea un entorno virtual para aislar las dependencias del proyecto:
   ```sh
   python -m venv venv
   ```

4. Activa el entorno virtual:
   - En Windows:
     ```sh
     .\venv\Scripts\activate
     ```
   - En macOS/Linux:
     ```sh
     source venv/bin/activate
     ```

### Instalar las dependencias

5. Instala las dependencias necesarias desde el archivo requirements.txt:
   ```sh
   pip install -r requirements.txt
   ```

### Configurar las variables de entorno

6. Crea un archivo .env en el directorio raíz del proyecto y añade las variables de entorno necesarias. 

```ini
PROJECT_NAME

TYPE_LLM
AZURE_API_KEY
AZURE_ENDPOINT
AZURE_API_VERSION
OPENAI_MODEL
DEPLOYMENT_EMBEDDING_MODEL

GEMINI_API_KEY
ANTHROPIC_API_KEY
ANTHROPIC_API_ACCESS_KEY

#Storage Section
TYPE_STORAGE
UPLOAD_FOLDER
AZURE_STORAGE_CONNECTION_STRING
AZURE_STORAGE_CONTAINER_NAME
AZURE_DATA_STORE_PATH
AZURE_URL_PATH_IMAGE

#database Section
TYPE_DATABASE
AZURE_SEARCH_SERVICE_ENDPOINT
AZURE_SEARCH_API_KEY
AZURE_SEARCH_INDEX_NAME

URL_IMAGE
VISION_ENDPOINT
VISION_KEY


### Iniciar el servidor FastAPI

7. Inicia el servidor FastAPI:
   ```sh
   uvicorn app.main:app --reload
   ```

## Probar las APIs

Puedes probar las APIs utilizando `curl` o Postman.

### Usando `curl`

Ejemplo de solicitud POST al endpoint `/generate/prompt`:
```sh
curl -X POST "http://127.0.0.1:8000/generate/prompt" \
     -H "Content-Type: application/json" \
     -d '{
           "llm_type": "openai",
           "prompt": "You are an AI assistant specialized in vehicle diagnostics, particularly in interpreting OBD-II message codes. Your role is to assist users by performing a triage of the provided OBD-II code, offering information about the code’s implications, and indicating the severity of the issue using a traffic light system. This system will help users understand whether they need to visit a service center immediately if they should stop driving the vehicle, or if the issue is not urgent.Triage: Use the OBD-II code to assess the situation and provide a clear recommendation: Red: Serious issue, stop the vehicle immediately and seek assistance. Yellow: Caution, visit a service center soon. Green: No immediate action is required, the issue is not critical. The vehicle has a list of error codes: P050D Guidelines: Style: Maintain a formal tone in all interactions. User Knowledge Level: Adapt explanations based on simple terms and provide basic explanations. Expertise: Demonstrate in-depth knowledge of vehicle systems and OBD-II codes."
         }'
```

### Usando Postman

1. Abre Postman y crea una nueva solicitud.
2. Selecciona el método `POST`.
3. Introduce la URL `http://127.0.0.1:8000/generate/prompt`.
4. En la pestaña "Body", selecciona "raw" y "JSON" y añade el siguiente JSON:
   ```json
   {
     "llm_type": "openai",
     "prompt": "You are an AI assistant specialized in vehicle diagnostics, particularly in interpreting OBD-II message codes. Your role is to assist users by performing a triage of the provided OBD-II code, offering information about the code’s implications, and indicating the severity of the issue using a traffic light system. This system will help users understand whether they need to visit a service center immediately if they should stop driving the vehicle, or if the issue is not urgent.Triage: Use the OBD-II code to assess the situation and provide a clear recommendation: Red: Serious issue, stop the vehicle immediately and seek assistance. Yellow: Caution, visit a service center soon. Green: No immediate action is required, the issue is not critical. The vehicle has a list of error codes: P050D Guidelines: Style: Maintain a formal tone in all interactions. User Knowledge Level: Adapt explanations based on simple terms and provide basic explanations. Expertise: Demonstrate in-depth knowledge of vehicle systems and OBD-II codes."
   }
   ```
5. Haz clic en "Send" para enviar la solicitud y verifica la respuesta.

## Ejecutar los tests

Para ejecutar los tests, asegúrate de que el servidor FastAPI esté corriendo y luego ejecuta:
```sh
pytest
```

Alternativamente, puedes ejecutar un archivo de test específico:
```sh
pytest test/test_google_search.py
```

## Contribuir

Si deseas contribuir a este proyecto, por favor abre un issue o envía un pull request.

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT.
