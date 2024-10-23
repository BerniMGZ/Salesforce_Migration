from google.cloud import documentai_v1beta3 as documentai
from google.oauth2 import service_account
from PIL import Image
import os
import pandas as pd
import shutil
import sys

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
        prefixes = ['MONSIEUR ', 'M. ', 'Mr. ', 'MR ', 'Mr ']
        for prefix in prefixes:
            if account_holder.startswith(prefix):
                account_holder = account_holder[len(prefix):]
                break
    return account_holder

# Función para eliminar espacios, puntos y guiones en IBAN y RIB
def format_iban_rib(value):
    if value:
        return value.replace(" ", "").replace(".", "").replace("-", "").replace("/", "").replace(",", "").replace(")", "").replace("(", "")
    return value

# Función para convertir archivos jfif a jpg
def convert_jfif_to_jpg(jfif_path):
    jpg_path = jfif_path.replace(".jfif", ".jpg")
    with Image.open(jfif_path) as img:
        img.convert("RGB").save(jpg_path, "JPEG")
    return jpg_path

# Función para procesar el documento
def process_document(file_path):
    client = documentai.DocumentProcessorServiceClient(credentials=credentials)

    # Detectar el tipo de archivo para establecer el mime_type adecuado
    if file_path.lower().endswith(".pdf"):
        mime_type = "application/pdf"
    else:
        mime_type = "image/jpeg"

    # Leer el archivo
    with open(file_path, 'rb') as image_file:
        file_content = image_file.read()

    # Crear la solicitud para procesar el documento
    document = {"content": file_content, "mime_type": mime_type}
    name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'

    request = {"name": name, "raw_document": document}

    # Llamar a la API de Document AI para procesar el documento
    result = client.process_document(request=request)
    return result.document

# Función para mover el archivo procesado a la carpeta 'processed_images'
def move_processed_file(file_path, processed_folder):
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)
    shutil.move(file_path, os.path.join(processed_folder, os.path.basename(file_path)))

# Función para mover el archivo con error a la carpeta 'failed_images'
def move_failed_file(file_path, failed_folder):
    if not os.path.exists(failed_folder):
        os.makedirs(failed_folder)
    shutil.move(file_path, os.path.join(failed_folder, os.path.basename(file_path)))

folder_path = "/Users/bernat.morros/Desktop/Salesforce Migration/Partner Receipts"
processed_folder = "/Users/bernat.morros/Desktop/Salesforce Migration/processed_images_partners"
failed_folder = "/Users/bernat.morros/Desktop/Salesforce Migration/failed_images_partners"

# Variable que define cuántos archivos se deben procesar
max_files_to_process = 414  # Cambia este valor según cuántos archivos quieras procesar

# Procesa cada archivo en la carpeta y guarda los resultados en el DataFrame
files_processed = 0

# Verificar si hay archivos en la carpeta antes de comenzar
files = os.listdir(folder_path)
if not files:
    print("No hay archivos para procesar en la carpeta especificada.")
else:
    for filename in files:
        if files_processed >= max_files_to_process:
            break

        file_path = os.path.join(folder_path, filename)

        # Verificar si el archivo es .jfif y convertirlo a .jpg
        if filename.lower().endswith(".jfif"):
            print(f"Convirtiendo archivo .jfif '{filename}' a .jpg...")
            try:
                file_path = convert_jfif_to_jpg(file_path)
                filename = os.path.basename(file_path)  # Actualizar el nombre del archivo a .jpg
            except Exception as e:
                print(f"Error al convertir '{filename}' a jpg: {e}")
                move_failed_file(file_path, failed_folder)
                continue

        # Incluir soporte para archivos .png
        if filename.lower().endswith((".jpeg", ".jpg", ".pdf", ".png")):
            print(f"Procesando documento '{filename}'...")

            try:
                # Validar si el archivo aún existe antes de procesar
                if not os.path.exists(file_path):
                    print(f"El archivo '{filename}' no se encontró. Saltando.")
                    continue

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

                # Mover el archivo procesado a la carpeta 'processed_images'
                move_processed_file(file_path, processed_folder)
                files_processed += 1

                # Mostrar progreso en consola (live counter)
                sys.stdout.write(f"\rProcessed images: {files_processed}/{max_files_to_process} ")
                sys.stdout.flush()

            except FileNotFoundError:
                print(f"\nEl archivo '{filename}' no se encontró durante el procesamiento. Saltando.")
            except Exception as e:
                print(f"\nOcurrió un error durante el procesamiento de '{filename}': {e}")
                # Mover el archivo fallido a la carpeta 'failed_images' si no existe error al mover
                if os.path.exists(file_path):
                    move_failed_file(file_path, failed_folder)

# Guarda el DataFrame en un archivo Excel si se procesaron imágenes
if not df.empty:
    output_file = "/Users/bernat.morros/Desktop/Salesforce Migration/Results_1_Partners.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\nResultados guardados en '{output_file}'")
else:
    print("\nNo se procesaron imágenes exitosamente, por lo que no se generó un archivo Excel.")
