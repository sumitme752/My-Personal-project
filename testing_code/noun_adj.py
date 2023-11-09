import nltk
import argparse
import os
import openpyxl

# Download NLTK data (if not already downloaded)
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('stopwords')

from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords

# Function to extract nouns and adjectives from text
def extract_nouns_adjectives(text):
    tokens = word_tokenize(text)
    tagged_tokens = pos_tag(tokens)
    nouns = [word for word, pos in tagged_tokens if pos.startswith('N')]
    adjectives = [word for word, pos in tagged_tokens if pos.startswith('J')]
    return nouns, adjectives

# Function to process an Excel file and extract nouns and adjectives from the first column of the first sheet
def process_excel_file(excel_file_path):
    try:
        wb = openpyxl.load_workbook(excel_file_path)
        first_sheet = wb.active
        column_values = [cell.value for cell in first_sheet['A']]
        
        # Check if any cell in the first column starts with a number or is empty
        skip_first_column = any(cell is None or (isinstance(cell, str) and cell.strip().isdigit()) for cell in column_values)
        
        if skip_first_column:
            # If any cell starts with a number or is empty, read the second column
            column_values = [cell.value for cell in first_sheet['B']]

        text = ' '.join([str(value) for value in column_values if isinstance(value, str)])
        text = text.lower()
        nouns, adjectives = extract_nouns_adjectives(text)

        # Remove common English stopwords from nouns and adjectives
        stop_words = set(stopwords.words('english'))
        nouns = [word for word in nouns if word not in stop_words]
        adjectives = [word for word in adjectives if word not in stop_words]

        # Get the Excel file name from the file path
        file_name = os.path.basename(excel_file_path)

        # Print the file location, Excel file name, list of nouns, and list of adjectives
        print(f"File Name: {file_name}")
        print("Nouns:", nouns)
        print("*" * 150)
        print(f"File Name: {file_name}")
        print("Adjectives:", adjectives)
        print("-" * 150)

        # Save the output to a text file at the same location as the Excel file
        output_file_path = os.path.splitext(excel_file_path)[0] + "_output.txt"
        with open(output_file_path, 'w') as output_file:
            output_file.write(f"File Name: {file_name}\n")
            output_file.write("Nouns: {}\n".format(nouns))
            output_file.write("*" * 150 + "\n")
            output_file.write(f"File Name: {file_name}\n")
            output_file.write("Adjectives: {}\n".format(adjectives))
            output_file.write("-" * 150 + "\n")
        
        print(f"Output saved to: {output_file_path}")
        
    except Exception as e:
        print(f"Error processing Excel file {excel_file_path}: {e}")


# Function to search for Excel files in a directory and its subdirectories
def search_excel_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".xlsx") or file.endswith(".xls"):  # Check for Excel file extensions
                excel_file_path = os.path.join(root, file)
                process_excel_file(excel_file_path)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Extract nouns and adjectives from the first column of the first sheet in Excel files in a folder and its subfolders.')
parser.add_argument('folder_name', help='Folder name from the file path')
args = parser.parse_args()

# Construct the full directory path by appending the folder name to a base directory
base_directory = '/Users/sumitkumar/Downloads/OneDrive_1_4-10-2023/'
folder_directory = os.path.join(base_directory, args.folder_name)

# Search for Excel files in the specified directory and its subdirectories
search_excel_files(folder_directory)
