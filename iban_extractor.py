from google.cloud import documentai_v1beta3 as documentai
from google.oauth2 import service_account
from PIL import Image
import os
import pandas as pd
import shutil

# Path to the JSON credentials file for the service account
credentials = service_account.Credentials.from_service_account_file(
    '/Users/bernat.morros/Desktop/Salesforce Migration/client_secrets.json'
)

# Project and processor configuration
project_id = 'dh-central-ta-qa'
location = 'us'  # The region where the processor is deployed, eu or us
processor_id = ''  # Replace with the correct custom processor ID

# Initialize an empty DataFrame to store the results
df = pd.DataFrame(columns=["Filename", "Account_Holder", "IBAN", "RIB"])

# Function to format the account holder's name
def format_account_holder(account_holder):
    if account_holder:
        # Remove prefixes such as 'MONSIEUR ', 'M. ', 'Mr. '
        prefixes = ['MONSIEUR ', 'M. ', 'Mr. ', 'MR ']
        for prefix in prefixes:
            if account_holder.startswith(prefix):
                account_holder = account_holder[len(prefix):]
                break
    return account_holder

# Function to remove spaces, dots, and hyphens in IBAN and RIB
def format_iban_rib(value):
    if value:
        return value.replace(" ", "").replace(".", "").replace("-", "")
    return value

# Function to convert jfif files to jpg
def convert_jfif_to_jpg(jfif_path):
    jpg_path = jfif_path.replace(".jfif", ".jpg")
    with Image.open(jfif_path) as img:
        img.convert("RGB").save(jpg_path, "JPEG")
    return jpg_path

# Function to process the document
def process_document(file_path):
    client = documentai.DocumentProcessorServiceClient(credentials=credentials)

    # Detect the file type to set the appropriate mime_type
    if file_path.lower().endswith(".pdf"):
        mime_type = "application/pdf"
    else:
        mime_type = "image/jpeg"

    # Read the file
    with open(file_path, 'rb') as image_file:
        file_content = image_file.read()

    # Create the request to process the document
    document = {"content": file_content, "mime_type": mime_type}
    name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'

    request = {"name": name, "raw_document": document}

    # Call the Document AI API to process the document
    result = client.process_document(request=request)
    return result.document

# Function to move the processed file to the 'processed_images' folder
def move_processed_file(file_path, processed_folder):
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)
    shutil.move(file_path, os.path.join(processed_folder, os.path.basename(file_path)))

folder_path = "/Users/bernat.morros/Desktop/Salesforce Migration/test"
processed_folder = "/Users/bernat.morros/Desktop/Salesforce Migration/test_processed_images"

# Variable that defines how many files to process
max_files_to_process = 500  # Change this value according to how many files you want to process

# Process each file in the folder and save the results in the DataFrame
files_processed = 0

for filename in os.listdir(folder_path):
    if files_processed >= max_files_to_process:
        break

    file_path = os.path.join(folder_path, filename)

    # Check if the file is .jfif and convert it to .jpg
    if filename.lower().endswith(".jfif"):
        print(f"Converting .jfif file '{filename}' to .jpg...")
        file_path = convert_jfif_to_jpg(file_path)
        filename = os.path.basename(file_path)  # Update the filename to .jpg

    # Include support for .png files
    if filename.lower().endswith((".jpeg", ".jpg", ".pdf", ".png")):
        print(f"Processing document '{filename}'...")

        try:
            document = process_document(file_path)
            account_holder = None
            iban = None
            rib = None

            # Extract entities and save the relevant values
            for entity in document.entities:
                if entity.type_ == "account-holder":
                    account_holder = format_account_holder(entity.mention_text)
                elif entity.type_ == "iban":
                    iban = format_iban_rib(entity.mention_text)
                elif entity.type_ == "rib":
                    rib = format_iban_rib(entity.mention_text)

            # Create a new DataFrame with the row you want to add
            new_row = pd.DataFrame({
                "Filename": [filename],
                "Account_Holder": [account_holder],
                "IBAN": [iban],
                "RIB": [rib]
            })

            # Concatenate the new DataFrame to the original DataFrame
            df = pd.concat([df, new_row], ignore_index=True)

            # Move the processed file to the 'processed_images' folder
            move_processed_file(file_path, processed_folder)
            files_processed += 1

        except Exception as e:
            print(f"An error occurred while processing '{filename}': {e}")

# Save the DataFrame to an Excel file
output_file = "/Users/bernat.morros/Desktop/Salesforce Migration/Results1000.xlsx"
df.to_excel(output_file, index=False)
print(f"Results saved in '{output_file}'")