import os
import requests
import msal
from msal import ConfidentialClientApplication
import atexit
import urllib.parse
import time
import subprocess
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from pdf2image import convert_from_path
import json
import traceback
import docx2pdf
import warnings
import tempfile
import logging


# Configure logging
logging.basicConfig(
    filename='error.log',  # Specify the log file path
    level=logging.ERROR,   # Set the log level to capture only errors
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# specify the directory path
temp_dir = "./demo"


# SharePoint configuration
folder_path = "demo" # replace this with the folder you want to list
tenant_id = '39c7f15b-5f6f-4bab-8ab5-0b6e414bdd83'
client_id = '8433780e-598f-4f92-8d31-80391ff86891'
client_secret = 'm6U8Q~ciyahATSY1AHGHOP8BeI2pIhmLtncoXa4c'
share_point_host = 'pvrt613.sharepoint.com'
site_name = "ai-team"
authority = "https://login.microsoftonline.com/" + tenant_id
end_point = "https://graph.microsoft.com/v1.0"
scopes = ["https://graph.microsoft.com/.default"]
file_list = []
property_name = ""
file_id_list = []

# Initialize a set to keep track of processed file names
processed_files = set()
processed_pdf_files = set()
processed_docx_files = set()
processed_image_files = set()
processed_json_files = set()

# Function to check if a file has a PDF or DOC extension
def is_pdf_or_doc(file_name):
    return file_name.lower().endswith((".pdf", ".doc", ".docx"))

# Initialize Azure Computer Vision client
subscription_key = "fee871b7b007480db5fcbebc0a4e71e7"
endpoint = "https://cv-akam-poc.cognitiveservices.azure.com//"
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


# Function to convert PDF file to JSON with retry mechanism
def convert_pdf_to_json(pdf_file):
    try:
        # Get the base name of the PDF file (without the extension)
        pdf_base_name = os.path.splitext(os.path.basename(pdf_file))[0]

        # Create a folder with the same name as the PDF in the same directory
        pdf_directory = os.path.dirname(pdf_file)

        # Check if a JSON file with the same base name already exists in the PDF directory
        json_file_path = os.path.join(pdf_directory, f"{pdf_base_name}.json")
        if os.path.exists(json_file_path):
            return 

        # Convert the PDF to a list of PIL (Pillow) images with a higher DPI (e.g., 300 DPI)
        images = convert_from_path(pdf_file, dpi=300)

        # Initialize a list to store word data for each page
        pdf_word_data_list = []

        # Iterate through each page of the PDF
        for i, image in enumerate(images):
            # Save the page as a PNG file in the PDF directory with the same PDF name and page number
            image_path = os.path.join(pdf_directory, f"{pdf_base_name}_page_{i + 1}.png")
            image.save(image_path, "PNG")

            # Read the local image file as binary data
            with open(image_path, "rb") as image_stream:
                recognize_handw_results = computervision_client.read_in_stream(image_stream, raw=True)

            # Get the operation location (URL with an ID at the end) from the response
            operation_location_remote = recognize_handw_results.headers["Operation-Location"]

            # Grab the ID from the URL
            operation_id = operation_location_remote.split("/")[-1]

            # Call the "GET" API and wait for it to retrieve the results with retries
            max_retries = 3  # Maximum number of retries
            retry_count = 0
            while True:
                get_handw_text_results = computervision_client.get_read_result(operation_id)
                if get_handw_text_results.status not in ['notStarted', 'running', 'failed']:
                    break

                if retry_count >= max_retries:
                    print(f"Maximum retries reached. Could not process the page for '{pdf_file}', Page {i + 1}.")
                    break  # Exit the retry loop

                retry_count += 1
                # print(f"Extracting text of page {i+1}")
                time.sleep(1)  # Adjust the delay time as needed

            # Initialize a list to store word data for the current page
            word_data_list = []

            # Extract and store information for each word on the current page
            if get_handw_text_results.status == OperationStatusCodes.succeeded:
                # Get the status once for the entire page
                page_status = get_handw_text_results.status
                for text_result in get_handw_text_results.analyze_result.read_results:
                    for line in text_result.lines:
                        # Calculate the offset using bounding box
                        offset = line.bounding_box[0]
                        # Store word data in JSON format
                        word_data = {
                            "content": line.text,
                            "boundingBox": line.bounding_box,
                            "confidence": page_status,
                            "span": {
                                "offset": offset,
                                "length": len(line.text)
                            }
                        }
                        word_data_list.append(word_data)  # Append to the page's list

            # Append the word data list for the current page to the overall list
            pdf_word_data_list.append(word_data_list)

        # Export the combined word data to a single JSON file in the PDF directory
        output_json_file = os.path.join(pdf_directory, f"{pdf_base_name}.json")
        with open(output_json_file, "w", encoding="utf-8") as json_file:
            json.dump(pdf_word_data_list, json_file, ensure_ascii=False, indent=4)

        # print(f"Word data for all pages of '{pdf_base_name}' saved in '{output_json_file}'.")
    except Exception as e:
        logging.error(f"Error processing '{pdf_file}': {str(e)}")
        traceback.print_exc()

# SharePoint download script (beginning)
def get_files(folder_name, drive_id, headers, stage, parent_folder, file_list, property_name, file_id_list): 
    folder_path = folder_name
    folder_url = urllib.parse.quote(folder_path)
    result = requests.get(
        f"{end_point}/drives/{drive_id}/root:/{folder_url}", headers=headers
    )
    result.raise_for_status()
    folder_info = result.json()
    folder_id = folder_info["id"]

    result = requests.get(
        f"{end_point}/drives/{drive_id}/items/{folder_id}/children",
        headers=headers,
    )
    result.raise_for_status()
    children = result.json()["value"]
    return_result = []
    stage += 1
    for file in children:
        file_name = file.get("name")
        if "folder" not in file: 
            if file.get("id") not in file_id_list: 
                # print({"property" : property_name, "doc_type" : parent_folder , "name" : file_name})
                file_download = file.get("@microsoft.graph.downloadUrl")
                response = requests.get(file_download)
                save_to_path = os.path.join(temp_dir,file_name)
                file_base_name=file_name.split('.')[0]

                with open(save_to_path, "wb") as f:
                    f.write(response.content)
                    file_id_list.append(file.get("id"))
                    process_downloaded_files(temp_dir)
                    print({"property" : property_name, "doc_type" : parent_folder , "name" : file_base_name +'.json'})
                   
                    return_result.append({ "folder": False, "name": file_name, "path": folder_name, "parent": parent_folder, "stage": stage})
        else:
            file_info = { "folder": True, "name": file_name, "stage": stage }
            if stage > 1:
                file_info['parent'] = parent_folder
                file_info['path'] = folder_name
            if stage ==2:
                property_name = parent_folder

            return_result.append(file_info)
            next_result = get_files(folder_name + "/" + file_name, drive_id, headers, stage, file_name, file_list, property_name, file_id_list)
            return_result += next_result 
    return return_result    

# Function to process newly downloaded files
def process_downloaded_files(download_dir):
    for root, _, files in os.walk(download_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if is_pdf_or_doc(file):
                # Get the base name of the file (without the extension)
                file_base_name = os.path.splitext(file)[0]

                # Check if a JSON file with the same base name already exists
                json_file_path = os.path.join(root, "Json", f"{file_base_name}.json")
                if os.path.exists(json_file_path):
                    continue

                # Check if a file with the same base name has already been processed
                if file_base_name not in processed_files:
                    # If not, mark it as processed and convert
                    processed_files.add(file_base_name)
                    # If the downloaded file is a PDF or DOC, call the PDF/DOC to JSON script
                    convert_pdf_to_json(file_path)
                    # print(f"JSON.")

def search_docx_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".docx"):
                docx_file = os.path.join(root, file)
                convert_docx_to_pdf_and_pdf_to_json(docx_file)

# Function to search for PDF files in a directory and its subdirectories
def search_pdfs_in_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_file = os.path.join(root, file)
                convert_pdf_to_json(pdf_file)

# Function to convert DOCX to PDF and then PDF to JSON with retry mechanism
def convert_docx_to_pdf_and_pdf_to_json(docx_file):
    try:
        docx_base_name = os.path.splitext(os.path.basename(docx_file))[0]
        docx_directory = os.path.dirname(docx_file)
        # Check if a JSON file with the same base name already exists in the PDF directory
        docx_file_path = os.path.join(docx_directory, f"{docx_base_name}.png")
        if os.path.exists(docx_file_path):
            return 
        # Convert DOCX to PDF
        # Check if a PDF file with the same base name already exists
        pdf_file_path = os.path.join(docx_directory, f"{docx_base_name}.pdf")
        if not os.path.exists(pdf_file_path):
            # Convert DOCX to PDF using docx2pdf
            docx2pdf.convert(docx_file)

        # Get the base name of the PDF file (without the extension)
        pdf_base_name = os.path.splitext(os.path.basename(docx_file))[0]

        # Create a folder with the same name as the PDF in the same directory
        pdf_directory = os.path.dirname(docx_file)
        pdf_file = os.path.join(pdf_directory, f"{pdf_base_name}.pdf")

        # Call the function to convert the resulting PDF to JSON
        convert_pdf_to_json(pdf_file)
    except Exception as e:
        logging.error(f"Error processing '{docx_file}': {str(e)}")
        traceback.print_exc()



# Function to search for DOCX files in a directory and its subdirectories
def search_docx_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".docx"):
                docx_file = os.path.join(root, file)
                if docx_file not in processed_docx_files:
                    convert_docx_to_pdf_and_pdf_to_json(docx_file)

# Function to search for PDF files in a directory and its subdirectories
def search_pdfs_in_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_file = os.path.join(root, file)
                if pdf_file not in processed_pdf_files:
                    convert_pdf_to_json(pdf_file)


# Directory where you want to search for DOCX and PDF files (change to your desired directory)
search_directory = temp_dir

# Main loop
while True:
    # Check for newly downloaded files and process them
    # process_downloaded_files(temp_dir)  # Replace with your download directory
    
    # Call the function to search for and convert DOCX files to PDF and then to JSON
    search_docx_files(search_directory)

    # Call the function to search for and convert PDFs to JSON
    search_pdfs_in_directory(search_directory)
    
    # Sharepoint download function
    try:
        cache = msal.SerializableTokenCache()

        if os.path.exists("token_cache.bin"):
            cache.deserialize(open("token_cache.bin", "r").read())

        atexit.register(
            lambda: open("token_cache.bin", "w").write(cache.serialize())
            if cache.has_state_changed
            else None
        )

        app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority,
            token_cache=cache,
        )

        accounts = app.get_accounts()
        result = None

        if len(accounts) > 0:
            result = app.acquire_token_silent(scopes, account=accounts[0])

        if not result:
            result = app.acquire_token_for_client(scopes=scopes)

        if "access_token" in result:
            headers = {"Authorization": "Bearer " + result["access_token"]}
            # get the site id
            result = requests.get(
                f"{end_point}/sites/{share_point_host}:/sites/{site_name}",
                headers=headers,
            )
            result.raise_for_status()
            site_info = result.json()
            site_id = site_info["id"]

            # get the drive id
            result = requests.get(f"{end_point}/sites/{site_id}/drive", headers=headers)
            result.raise_for_status()
            drive_info = result.json()
            drive_id = drive_info["id"]
            file_list1 = get_files(folder_path, drive_id, headers, 0, "", file_list, property_name, file_id_list)
            file_list.extend(file_list1)
        else:
            raise Exception("no access token in result")

    except Exception as e:
        logging.error(f"Error processing: {str(e)}")
    
    time.sleep(2)
