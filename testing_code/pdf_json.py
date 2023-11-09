import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time
from pdf2image import convert_from_path
import json
import traceback
import docx2pdf

# Initialize Azure Computer Vision client
subscription_key = "fee871b7b007480db5fcbebc0a4e71e7"
endpoint = "https://cv-akam-poc.cognitiveservices.azure.com//"
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Function to convert PDF file to JSON with retry mechanism
# Function to convert PDF file to JSON with retry mechanism
# Function to convert PDF file to JSON with retry mechanism
# Function to convert PDF file to JSON with retry mechanism
# Function to convert PDF file to JSON with retry mechanism
# Function to convert PDF file to JSON with retry mechanism
def convert_pdf_to_json(pdf_file):
    try:
        # Get the base name of the PDF file (without the extension)
        pdf_base_name = os.path.splitext(os.path.basename(pdf_file))[0]

        # Create a folder with the same name as the PDF in the same directory
        pdf_directory = os.path.dirname(pdf_file)
        output_folder = os.path.join(pdf_directory, pdf_base_name)
        os.makedirs(output_folder, exist_ok=True)

        # Convert the PDF to a list of PIL (Pillow) images with a higher DPI (e.g., 300 DPI)
        images = convert_from_path(pdf_file, dpi=200)

        # Initialize a list to store word data for each page
        pdf_word_data_list = []

        # Iterate through each page of the PDF
        for i, image in enumerate(images):
            # Save the page as a PNG file in the created folder
            image_path = os.path.join(output_folder, f"page_{i + 1}.png")
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
                    raise Exception("Maximum retries reached. Could not process the page.")
                retry_count += 1
                print(f"Retrying for '{pdf_file}', Page {i + 1} after a short delay...")
                time.sleep(20)  # Adjust the delay time as needed

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

        # Create a folder named "Json" inside the PDF directory
        json_folder = os.path.join(pdf_directory, "Json")
        os.makedirs(json_folder, exist_ok=True)

        # Export the combined word data to a single JSON file in the "Json" folder
        output_json_file = os.path.join(json_folder, f"{pdf_base_name}_word_data.json")
        with open(output_json_file, "w", encoding="utf-8") as json_file:
            json.dump(pdf_word_data_list, json_file, ensure_ascii=False, indent=4)

        print(f"Word data for all pages of '{pdf_base_name}' saved in '{output_json_file}'.")
    except Exception as e:
        print(f"Error processing '{pdf_file}': {str(e)}")
        traceback.print_exc()





# Function to convert DOCX to PDF and then PDF to JSON with retry mechanism
def convert_docx_to_pdf_and_pdf_to_json(docx_file):
    try:
        # Convert DOCX to PDF
        docx2pdf.convert(docx_file)

        # Get the base name of the PDF file (without the extension)
        pdf_base_name = os.path.splitext(os.path.basename(docx_file))[0]

        # Create a folder with the same name as the PDF in the same directory
        pdf_directory = os.path.dirname(docx_file)
        pdf_file = os.path.join(pdf_directory, f"{pdf_base_name}.pdf")

        # Call the function to convert the resulting PDF to JSON
        convert_pdf_to_json(pdf_file)
    except Exception as e:
        print(f"Error converting DOCX to PDF and processing '{docx_file}': {str(e)}")
        traceback.print_exc()

# Function to search for DOCX files in a directory and its subdirectories
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

# Directory where you want to search for DOCX and PDF files (change to your desired directory)
search_directory = "/Users/sumitkumar/Downloads/OneDrive_1_4-10-2023/"

# Call the function to search for and convert DOCX files to PDF and then to JSON
search_docx_files(search_directory)

# Call the function to search for and convert PDFs to JSON
search_pdfs_in_directory(search_directory)
