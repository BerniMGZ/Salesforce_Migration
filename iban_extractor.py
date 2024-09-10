from google.cloud import documentai_v1beta3 as documentai
from google.oauth2 import service_account
import os

# Ruta al archivo de credenciales JSON
credentials = service_account.Credentials.from_service_account_file(
    '/Users/bernat.morros/Desktop/Salesforce Migration/client_secrets.json'
)

# Inicializa el cliente de Document AI
project_id = 'dh-central-ta-qa'  # Reemplaza con tu ID de proyecto
location = 'us'  # Reemplaza con tu ubicación de procesador
processor_id = '469561897fae299a'  # Reemplaza con el ID de tu procesador

def process_document(file_path):
    client = documentai.DocumentProcessorServiceClient(credentials=credentials)

    # Lee el archivo de imagen
    with open(file_path, 'rb') as image_file:
        image_content = image_file.read()

    # Crea la solicitud para procesar el documento
    document = {"content": image_content, "mime_type": "image/jpeg"}  # Cambia el mime_type si es necesario
    name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'

    request = {"name": name, "raw_document": document}

    # Llama a la API de Document AI para procesar el documento
    result = client.process_document(request=request)
    return result.document

def extract_relevant_entities(document):
    iban = None
    account_holder = None

    for entity in document.entities:
        if "AccountHolder" in entity.type_.lower():
            iban = entity.mention_text
        if "IBAN" in entity.type_.lower() or "name" in entity.type_.lower():
            account_holder = entity.mention_text

    return iban, account_holder

folder_path = "/Users/bernat.morros/Desktop/Salesforce Migration/test"  # Reemplaza esta ruta con la ruta a tu carpeta de imágenes

for filename in os.listdir(folder_path):
    if filename.lower().endswith((".jpeg", ".jpg", ".pdf")):
        file_path = os.path.join(folder_path, filename)
        print(f"Procesando documento '{filename}'...")

        try:
            document = process_document(file_path)
            iban, account_holder = extract_relevant_entities(document)
            print(f"IBAN: {iban}")
            print(f"Titular de la cuenta: {account_holder}")
        except Exception as e:
            print(f"Ocurrió un error durante el procesamiento de '{filename}': {e}")
