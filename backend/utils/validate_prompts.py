# import sys
# import os
# import pandas as pd

# def process_prompts(file_path):
#     # Read the CSV file into a DataFrame, handling inconsistent quotation marks
#     df = pd.read_csv(file_path, quotechar='"', skipinitialspace=True, dtype=str)
    
#     # Ensure required columns are present
#     if 'prompt' not in df.columns or 'base_prompt' not in df.columns:
#         print(f"Error: CSV file must have 'prompt' and 'base_prompt' columns.")
#         sys.exit(1)

#     # Replace "/" and strip whitespace in both 'prompt' and 'base_prompt' columns
#     df['prompt'] = df['prompt'].fillna("").str.replace("/", "").str.strip()
#     df['base_prompt'] = df['base_prompt'].fillna("").str.replace("/", "").str.strip()

#     # Debug: Print original and processed 'base_prompt'
#     for index, row in df.iterrows():
#         print(f"Original base_prompt: '{row['base_prompt']}'")
#         print(f"Processed base_prompt: '{row['base_prompt']}'")

#     # Check for empty 'prompt' values and replace with empty string
#     df['prompt'] = df['prompt'].replace("", '""')

#     # Check if any prompt exceeds 650 characters and exit if any are found
#     long_prompt = df[df['prompt'].str.len() > 650]
#     long_base_prompt = df[df['base_prompt'].str.len() > 650]

#     if not long_prompt.empty or not long_base_prompt.empty:
#         offending_prompt = long_prompt if not long_prompt.empty else long_base_prompt
#         print(f"Error: The following prompt exceeds 650 characters:\n{offending_prompt.iloc[0]}")
#         sys.exit(1)

#     # Save the cleaned CSV file with original columns, ensuring proper quotes for all values
#     df.to_csv(file_path, index=False, quoting=pd.io.common.csv.QUOTE_ALL)

#     # Save the 'prompt' column to prompts.txt, ensuring all prompts are quoted
#     prompt_txt_path = os.path.join(os.path.dirname(file_path), 'prompts.txt')
#     df['prompt'].to_csv(prompt_txt_path, index=False, header=False, quoting=pd.io.common.csv.QUOTE_ALL)

# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser(description="Process prompts from a CSV file")
#     parser.add_argument("--prompt_path", type=str, default="/home/ubuntu/t2v-view/prompts.csv", help="Path to the prompt CSV file")
#     prompt_path = parser.parse_args().prompt_path

#     try:
#         process_prompts(prompt_path)
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         sys.exit(1)

import sys
import os
import pandas as pd
import csv

def add_quotes_to_fields(line):
    """
    This function ensures that fields without commas and not already quoted are quoted.
    It processes each field of a CSV line separately.
    """
    fields = []
    for field in csv.reader([line], skipinitialspace=True).__next__():
        field = field.strip()
        if not field.startswith('"'):
            field = f'"{field}"'  # Add quotes around fields that are not quoted and don't contain commas
        fields.append(field)
    return ",".join(fields)

def process_prompts(file_path):
    # Step 1: Open the file and read lines
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        lines = f.readlines()

    # Step 2: Add quotation marks to individual fields that are not using them and don't contain commas
    new_lines = []
    for line in lines:
        if line.strip():  # Skip empty lines
            new_line = add_quotes_to_fields(line)
            new_lines.append(new_line)

    # Step 3: Write the modified lines back to the file to ensure consistent quoting
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        f.write("\n".join(new_lines) + "\n")

    # Step 4: Now proceed with reading the CSV into a DataFrame, handling inconsistent quotation marks
    df = pd.read_csv(file_path, quotechar='"', skipinitialspace=True, dtype=str)

    # Ensure required columns are present
    if 'prompt' not in df.columns or 'base_prompt' not in df.columns:
        print(f"Error: CSV file must have 'prompt' and 'base_prompt' columns.")
        sys.exit(1)

    # Replace "/" and strip whitespace in both 'prompt' and 'base_prompt' columns
    df['prompt'] = df['prompt'].fillna("").str.replace("/", "").str.strip()
    df['base_prompt'] = df['base_prompt'].fillna("").str.replace("/", "").str.strip()

    # Step 5: Handle empty values in the second column by replacing them with an empty string
    df['base_prompt'] = df['base_prompt'].replace("", '""')

    # Debug: Print original and processed 'base_prompt'
    for index, row in df.iterrows():
        print(f"Original base_prompt: '{row['base_prompt']}'")
        print(f"Processed base_prompt: '{row['base_prompt']}'")

    # Step 6: Check for empty 'prompt' values and replace with an empty string if necessary
    df['prompt'] = df['prompt'].replace("", '""')

    # Step 7: Check if any prompt exceeds 650 characters and exit if any are found
    long_prompt = df[df['prompt'].str.len() > 650]
    long_base_prompt = df[df['base_prompt'].str.len() > 650]

    if not long_prompt.empty or not long_base_prompt.empty:
        offending_prompt = long_prompt if not long_prompt.empty else long_base_prompt
        print(f"Error: The following prompt exceeds 650 characters:\n{offending_prompt.iloc[0]}")
        sys.exit(1)

    # Step 8: Save the cleaned CSV file with original columns, ensuring proper quotes for all values
    df.to_csv(file_path, index=False, quoting=csv.QUOTE_ALL)

    # Step 9: Save the 'prompt' column to prompts.txt, ensuring all prompts are quoted
    prompt_txt_path = os.path.join(os.path.dirname(file_path), 'prompts.txt')
    df['prompt'].to_csv(prompt_txt_path, index=False, header=False, quoting=csv.QUOTE_ALL)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Process prompts from a CSV file")
    parser.add_argument("--prompt_path", type=str, default="/home/ubuntu/t2v-view/prompts.csv", help="Path to the prompt CSV file")
    prompt_path = parser.parse_args().prompt_path

    try:
        process_prompts(prompt_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
