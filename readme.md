### Salesforce Migration Document Processing Script

**Overview**

This script is designed to process documents, extracting key information such as the account holder's name, IBAN, and RIB. It leverages Google Document AI for OCR (Optical Character Recognition) and entity extraction, processes different file types (such as .pdf, .jpg, .png, and .jfif), and saves the results in an Excel spreadsheet. Additionally, it formats the extracted data by removing unnecessary prefixes and special characters.

**Features**

-  **Document Processing**: Extracts account holder's name, IBAN, and RIB from various types of documents.

-  **Format Cleanup**: Removes unnecessary prefixes (MONSIEUR, M., etc.) and special characters from extracted fields.

-  **File Conversion**: Converts .jfif files to .jpg before processing.

-  **File Management**: Moves successfully processed files to a separate folder.

**Prerequisites**

**1\. Google Cloud Project Setup**

-  **Google Cloud Account**: Ensure you have a Google Cloud account set up.

-  **Document AI API Enabled**: Enable the Document AI API in your Google Cloud Console.

-  **Service Account**: Create a service account with permissions to access Document AI.

-  **Credentials File**: Download the JSON credentials file for your service account.

**2\. Python Requirements**

-  **Python Version**: The script requires Python 3.7 or later.

**3\. Required Python Packages**

Install the required Python packages using the following command:

```python
pip install google-cloud-documentai google-auth pandas pillow openpyxl
```
Here's a brief description of the required packages:

-  **google-cloud-documentai**: To interact with the Document AI API.

-  **google-auth**: To handle authentication using service account credentials.

-  **pandas**: For data manipulation and creating an Excel file.

-  **pillow**: To handle image processing and conversion (.jfif to .jpg).

-  **openpyxl**: To write data to Excel files.

**4\. Folder Setup**

-  Ensure that you have a folder containing the files to be processed.

-  Define separate folders for storing input files and processed files.

**Getting Started**

### Step-by-Step Instructions

1.  **Clone the Repository (Optional)**:

If this script is hosted in a repository, clone it using:

```python
git clone <repository-url>
```
Otherwise, ensure you have the script in a directory of your choice.

2.  **Set Up Your Environment**:

Install Python dependencies by running:

```python
pip install -r requirements.txt
```
Alternatively, use the individual package installation command shown above.

3.  **Place the Credentials File**:

Make sure that the service account JSON file (client_secrets.json) is saved at the path specified in the script (/Users/bernat.morros/Desktop/Salesforce Migration/client_secrets.json). Update the script if your credentials file is in a different location.

4.  **Organize Your Input Files**:

-  Place the documents you wish to process in the folder /Users/bernat.morros/Desktop/Salesforce Migration/test.

-  Ensure that the documents are in .pdf, .jpg, .jpeg, .png, or .jfif formats.

5.  **Run the Script**:

Execute the script using the following command:

```python
python document_processing.py
```
Alternatively, use the individual package installation command shown above.

3.  **Place the Credentials File**:

Make sure that the service account JSON file (client_secrets.json) is saved at the path specified in the script (/Users/bernat.morros/Desktop/Salesforce Migration/client_secrets.json). Update the script if your credentials file is in a different location.

4.  **Organize Your Input Files**:

-  Place the documents you wish to process in the folder /Users/bernat.morros/Desktop/Salesforce Migration/test.

-  Ensure that the documents are in .pdf, .jpg, .jpeg, .png, or .jfif formats.

5.  **Run the Script**:

Execute the script using the following command:This will process the files in the input folder, extract the required information, and save the results to an Excel file ([your_name].xlsx).

**Script Parameters**

1.  **Folder Paths**:

-  folder_path: Set to the location containing the files to be processed (/Users/bernat.morros/Desktop/Salesforce Migration/test).

-  processed_folder: Set to the location where successfully processed files will be moved (/Users/bernat.morros/Desktop/Salesforce Migration/test_processed_images).

2.  **Max Files to Process**:

-  max_files_to_process: Defines the maximum number of files to be processed. Default is set to 500. Adjust this number based on your requirements.

3.  **Google Cloud Configuration**:

-  project_id: Google Cloud project ID.

-  location: The region where your Document AI processor is deployed (e.g., 'us').

-  processor_id: The unique ID of your Document AI processor. Update this with your custom processor ID.

### Output

*Excel File*:

After processing, an Excel file named [your_name].xlsx will be generated at /Users/bernat.morros/Desktop/Salesforce Migration/.

Columns in the Excel file:

-  Filename: The name of the processed file.

-  Account_Holder: Extracted account holder's name, with prefixes removed.

-  IBAN: Extracted IBAN, cleaned of spaces, dots, and hyphens.

-  RIB: Extracted RIB, cleaned of spaces, dots, and hyphens.

- **Processed Files**: Files that were successfully processed will be moved to the processed_folder.


**Error Handling**

If an error occurs during processing, the script will print the filename and the error message. These files will not be moved to the processed_folder, so you can identify which ones need reprocessing.

**Common Issues and Solutions**

1.  **Authentication Errors**:

-  Make sure the path to the credentials file is correct.

-  Ensure the service account has appropriate permissions for the Document AI API.

2.  **Missing Dependencies**:

-  Run pip install -r requirements.txt again to make sure all dependencies are installed.

-  Ensure you are using Python 3.7 or later.

3.  **File Conversion Issues**:

-  Ensure the PIL (Pillow) library is installed correctly. You may need to install additional system libraries for image processing if errors occur during .jfif to .jpg conversion.

**Customization**

-  **Prefix List**:

If additional prefixes need to be removed from account holder names, add them to the prefixes list in the format_account_holder function.

-  **File Types**:

To add support for additional file types, update the conditional logic in the main loop (if filename.lower().endswith(...)).