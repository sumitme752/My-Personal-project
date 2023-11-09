import argparse
import os
import openpyxl
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords

# Function to extract unique nouns and adjectives from text
def extract_unique_nouns_adjectives(text):
    tokens = word_tokenize(text)
    tagged_tokens = pos_tag(tokens)
    nouns = set()
    adjectives = set()
    for word, pos in tagged_tokens:
        if pos.startswith('N'):
            nouns.add(word)
        elif pos.startswith('J'):
            adjectives.add(word)
    return list(nouns), list(adjectives)

# Function to process an Excel file and extract unique nouns and adjectives from the first column of the first sheet
def process_excel_file(excel_file_path, noun_output_file, adjective_output_file):
    try:
        wb = openpyxl.load_workbook(excel_file_path)
        first_sheet = wb.active
        column_values = [cell.value for cell in first_sheet['A']]
        
        # Check if any cell in the first column starts with a number or is empty
        skip_first_column = any(cell is None or (isinstance(cell, str) and cell.strip().isdigit()) for cell in column_values)
        
        if skip_first_column:
            # If any cell starts with a number or is empty, read the second column
            column_values = [cell.value for cell in first_sheet['B']]

        # Remove the first row if it contains headers
        if isinstance(column_values[0], str):
            column_values = column_values[1:]

        text = ' '.join([str(value) for value in column_values if isinstance(value, str)])
        text = text.lower()
        nouns, adjectives = extract_unique_nouns_adjectives(text)

        # Remove common English stopwords from nouns and adjectives
        stop_words = set(stopwords.words('english'))
        nouns = [word for word in nouns if word not in stop_words]
        adjectives = [word for word in adjectives if word not in stop_words]

        # Append the extracted nouns to the noun_output_file
        with open(noun_output_file, 'a', encoding='utf-8') as noun_file:
            noun_file.write('\n'.join(nouns) + '\n')

        # Append the extracted adjectives to the adjective_output_file
        with open(adjective_output_file, 'a', encoding='utf-8') as adjective_file:
            adjective_file.write('\n'.join(adjectives) + '\n')

    except Exception as e:
        print(f"Error processing Excel file {excel_file_path}: {e}")

# Function to search for Excel files in a directory and its subdirectories
def search_excel_files(directory, noun_output_file, adjective_output_file):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".xlsx") or file.endswith(".xls"):  # Check for Excel file extensions
                excel_file_path = os.path.join(root, file)
                process_excel_file(excel_file_path, noun_output_file, adjective_output_file)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Extract unique nouns and adjectives from the first column of the first sheet in Excel files in a folder and its subfolders.')
parser.add_argument('folder_name', help='Folder name from the file path')
args = parser.parse_args()

# Construct the full directory path by appending the folder name to a base directory
base_directory = '/Users/sumitkumar/Downloads/OneDrive_1_4-10-2023/'
folder_directory = os.path.join(base_directory, args.folder_name)

# Specify the output files for saving nouns and adjectives
noun_output_file = os.path.join(folder_directory, 'noun.txt')
adjective_output_file = os.path.join(folder_directory, 'adjective.txt')

# Search for Excel files in the specified directory and its subdirectories
search_excel_files(folder_directory, noun_output_file, adjective_output_file)

print(f"Unique nouns saved to {noun_output_file}")
print(f"Unique adjectives saved to {adjective_output_file}")
