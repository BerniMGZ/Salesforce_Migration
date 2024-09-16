from google.cloud import documentai_v1beta3 as documentai
from google.oauth2 import service_account
import os
import pandas as pd

# Ruta al archivo de credenciales JSON de la cuenta de servicio
credentials = service_account.Credentials.from_service_account_file(
    '/Users/bernat.morros/Desktop/Salesforce Migration/client_secrets.json'
)

# Configuración del proyecto y procesador
project_id = 'dh-central-ta-qa'
location = 'us'  # La región donde está desplegado el procesador
processor_id = '4a78e04b0215da8f'  # Reemplaza con el ID correcto del procesador personalizado

# Inicializa un DataFrame vacío para almacenar los resultados
df = pd.DataFrame(columns=["Filename", "Account_Holder", "IBAN", "RIB"])

# Función para formatear el nombre del titular de la cuenta
def format_account_holder(account_holder):
    if account_holder:
        # Elimina prefijos como 'MONSIEUR ', 'M. ', 'Mr. '
        prefixes = ['MONSIEUR ', 'M. ', 'Mr. ', 'MR ']
        for prefix in prefixes:
            if account_holder.startswith(prefix):
                account_holder = account_holder[len(prefix):]
                break
    return account_holder

# Función para eliminar espacios en IBAN y RIB
def format_iban_rib(value):
    if value:
        return value.replace(" ", "")
    return value

def process_document(file_path):
    client = documentai.DocumentProcessorServiceClient(credentials=credentials)

    # Leer el archivo de imagen
    with open(file_path, 'rb') as image_file:
        image_content = image_file.read()

    # Crear la solicitud para procesar el documento
    document = {"content": image_content, "mime_type": "image/jpeg"}
    name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'

    request = {"name": name, "raw_document": document}

    # Llamar a la API de Document AI para procesar el documento
    result = client.process_document(request=request)
    return result.document

folder_path = "/Users/bernat.morros/Desktop/Salesforce Migration/test"

# Procesa cada archivo en la carpeta y guarda los resultados en el DataFrame
for filename in os.listdir(folder_path):
    if filename.lower().endswith((".jpeg", ".jpg", ".pdf")):
        file_path = os.path.join(folder_path, filename)
        print(f"Procesando documento '{filename}'...")

        try:
            document = process_document(file_path)
            account_holder = None
            iban = None
            rib = None

            # Extrae las entidades y guarda los valores relevantes
            for entity in document.entities:
                if entity.type_ == "account-holder":
                    account_holder = format_account_holder(entity.mention_text)
                elif entity.type_ == "iban":
                    iban = format_iban_rib(entity.mention_text)
                elif entity.type_ == "rib":
                    rib = format_iban_rib(entity.mention_text)

            # Crear un nuevo DataFrame con la fila que quieres agregar
            new_row = pd.DataFrame({
                "Filename": [filename],
                "Account_Holder": [account_holder],
                "IBAN": [iban],
                "RIB": [rib]
            })

            # Concatenar el nuevo DataFrame al DataFrame original
            df = pd.concat([df, new_row], ignore_index=True)

        except Exception as e:
            print(f"Ocurrió un error durante el procesamiento de '{filename}': {e}")

# Guarda el DataFrame en un archivo Excel
output_file = "/Users/bernat.morros/Desktop/Salesforce Migration/processed_results4.xlsx"
df.to_excel(output_file, index=False)
print(f"Resultados guardados en '{output_file}'")

## mejor el primer modelo