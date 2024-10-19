import sys

import csv
import os
import sys

def process_prompts(file_path):
    try:
        # Determine if the file is prompts.csv or prompts.txt
        file_extension = os.path.splitext(file_path)[1]
        
        if file_extension == '.csv':
            # Process the CSV file with two columns "prompt" and "base_prompt"
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                
                # Check headers
                if reader.fieldnames != ['prompt', 'base_prompt']:
                    print(f"Error: CSV file must have headers 'prompt' and 'base_prompt'.")
                    sys.exit(1)

                cleaned_rows = []
                prompts_only = []

                for row in reader:
                    prompt = row['prompt'].replace("/", "")
                    base_prompt = row['base_prompt'].replace("/", "")

                    # Check if any prompt exceeds 650 characters
                    if len(prompt) > 650 or len(base_prompt) > 650:
                        offending_prompt = prompt if len(prompt) > 650 else base_prompt
                        print(f"Error: The following prompt exceeds 650 characters:\n{offending_prompt}")
                        sys.exit(1)

                    cleaned_rows.append({'prompt': prompt, 'base_prompt': base_prompt})
                    prompts_only.append(prompt)

            # Save the cleaned CSV file with original columns
            with open(file_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['prompt', 'base_prompt'])
                writer.writeheader()
                writer.writerows(cleaned_rows)

            # Save the new file prompt_txt with only the first column (prompts)
            prompt_txt_path = os.path.join(os.path.dirname(file_path), 'prompt_txt')
            with open(prompt_txt_path, 'w') as file:
                for prompt in prompts_only:
                    file.write(prompt + '\n')

        elif file_extension == '.txt':
            # Process the TXT file, which should have a single column without headers
            with open(file_path, 'r') as file:
                lines = file.readlines()

            cleaned_lines = []
            for line in lines:
                prompt = line.strip().replace("/", "")

                # Check if the prompt exceeds 500 characters
                if len(prompt) > 500:
                    print(f"Error: The following prompt exceeds 500 characters:\n{prompt}")
                    sys.exit(1)

                cleaned_lines.append(prompt)

            # Overwrite the original txt file with cleaned prompts
            with open(file_path, 'w') as file:
                for cleaned_prompt in cleaned_lines:
                    file.write(cleaned_prompt + '\n')

        else:
            print(f"Error: Unsupported file format. Only .csv and .txt are allowed.")
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="Process prompts from a text file")
    parser.add_argument("--prompt_path", type=str, default="/home/ubuntu/t2v-view/prompts.txt", help="Path to the prompt text file")
    prompt_path = parser.parse_args().prompt_path

    process_prompts(prompt_path)
