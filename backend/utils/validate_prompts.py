# import sys
# import os
# import pandas as pd

# def process_prompts(file_path):
    
#     # Read the CSV file into a DataFrame
#     df = pd.read_csv(file_path)

#     # Check for required headers
#     if 'prompt' not in df.columns or 'base_prompt' not in df.columns:
#         print(f"Error: CSV file must have 'prompt' and 'base_prompt' columns.")
#         sys.exit(1)

#     # Replace "/" and strip whitespace in both 'prompt' and 'base_prompt' columns
#     df['prompt'] = df['prompt'].str.replace("/", "").str.strip()
#     df['base_prompt'] = df['base_prompt'].fillna("").str.replace("/", "").str.strip()

#     # Debug: Print original and processed 'base_prompt'
#     for index, row in df.iterrows():
#         print(f"Original base_prompt: '{row['base_prompt']}'")
#         print(f"Processed base_prompt: '{row['base_prompt']}'")

#     # Check for empty 'prompt' values and exit if any are found
#     if df['prompt'].eq("").any():
#         print(f"Error: 'prompt' column cannot be empty.")
#         sys.exit(1)

#     # Check if any prompt exceeds 650 characters and exit if any are found
#     long_prompt = df[df['prompt'].str.len() > 650]
#     long_base_prompt = df[df['base_prompt'].str.len() > 650]

#     if not long_prompt.empty or not long_base_prompt.empty:
#         offending_prompt = long_prompt if not long_prompt.empty else long_base_prompt
#         print(f"Error: The following prompt exceeds 650 characters:\n{offending_prompt.iloc[0]}")
#         sys.exit(1)

#     # Save the cleaned CSV file with original columns
#     df.to_csv(file_path, index=False)

#     # Save the 'prompts' column to prompts.txt
#     prompt_txt_path = os.path.join(os.path.dirname(file_path), 'prompts.txt')
#     df['prompt'].to_csv(prompt_txt_path, index=False, header=False)

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

def validate_and_process_csv(file_path):
    """Validates and processes the CSV, ensuring correct field count and treating empty base_prompt as empty strings."""

    try:
        # Read the raw content of the CSV file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Remove trailing commas from lines where base_prompt is empty
        cleaned_lines = []
        for line in lines:
            # Check if the line ends with a comma and has only one comma (meaning base_prompt is empty)
            if line.count(',') == 1 and line.strip().endswith(','):
                cleaned_lines.append(line.strip().rstrip(',') + '\n')
            else:
                cleaned_lines.append(line)

        # Now read the CSV content from the cleaned lines
        from io import StringIO
        csv_content = ''.join(cleaned_lines)
        df = pd.read_csv(StringIO(csv_content), dtype=str, keep_default_na=False)

        # Rest of your processing remains the same...
        # Check if the CSV contains the correct columns
        if 'prompt' not in df.columns or 'base_prompt' not in df.columns:
            print(f"Error: CSV file must contain exactly two columns: 'prompt' and 'base_prompt'.")
            sys.exit(1)

        # Replace "/" and strip whitespace in both 'prompt' and 'base_prompt' columns
        df['prompt'] = df['prompt'].str.replace("/", "").str.strip()
        df['base_prompt'] = df['base_prompt'].fillna("").str.replace("/", "").str.strip()

        # Check for empty 'prompt' values and raise an error if found
        empty_prompts = df[df['prompt'].str.strip() == ""]
        if not empty_prompts.empty:
            print(f"Error: 'prompt' column contains empty values.")
            print(empty_prompts)
            sys.exit(1)

        # Check if any 'prompt' or 'base_prompt' exceeds 650 characters
        long_prompt = df[df['prompt'].str.len() > 650]
        long_base_prompt = df[df['base_prompt'].str.len() > 650]

        if not long_prompt.empty or not long_base_prompt.empty:
            offending_prompt = long_prompt if not long_prompt.empty else long_base_prompt
            print(f"Error: The following prompt exceeds 650 characters:\n{offending_prompt.iloc[0]}")
            sys.exit(1)

        # Save the cleaned CSV file with original columns
        df.to_csv(file_path, index=False)

        # Save the 'prompts' column to prompts.txt
        prompt_txt_path = os.path.join(os.path.dirname(file_path), 'prompts.txt')
        df['prompt'].to_csv(prompt_txt_path, index=False, header=False)

    except pd.errors.ParserError as e:
        print(f"An error occurred while parsing the CSV: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="Process prompts from a CSV file")
    parser.add_argument("--prompt_path", type=str, default="/home/ubuntu/t2v-view/prompts.csv", help="Path to the prompt CSV file")
    prompt_path = parser.parse_args().prompt_path

    try:
        validate_and_process_csv(prompt_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
