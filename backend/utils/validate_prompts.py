import sys
import csv
import os

def process_prompts(file_path):
    
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        
        # Check headers
        if reader.fieldnames != ['prompt', 'base_prompt']:
            print(f"Error: CSV file must have headers 'prompt' and 'base_prompt'.")
            sys.exit(1)

        cleaned_rows = []
        prompts_only = []

        for row in reader:
            prompt = row['prompt'].replace("/", "").strip()
            
            # Debug: Print original base_prompt
            print(f"Original base_prompt: '{row['base_prompt']}'")
            
            # Explicitly check for None or empty after stripping
            base_prompt = row.get('base_prompt', '')
            if base_prompt is None or base_prompt.strip() == "":
                base_prompt = ""  # Force empty string
            else:
                base_prompt = base_prompt.replace("/", "").strip()
            
            # Debug: Print processed base_prompt
            print(f"Processed base_prompt: '{base_prompt}'")


            # Raise an error if prompt is empty
            if not prompt:
                print(f"Error: 'prompt' column cannot be empty for row: {row}")
                sys.exit(1)

            # Check if any prompt exceeds 650 characters
            if len(prompt) > 650 or len(base_prompt) > 650:
                offending_prompt = prompt if len(prompt) > 650 else base_prompt
                print(f"Error: The following prompt exceeds 650 characters:\n{offending_prompt}")
                sys.exit(1)

            # Ensure base_prompt is written as an empty string if it's empty
            cleaned_rows.append({'prompt': prompt, 'base_prompt': base_prompt})
            prompts_only.append(prompt)

    # Save the cleaned CSV file with original columns
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['prompt', 'base_prompt'])
        writer.writeheader()
        writer.writerows(cleaned_rows)

    # Save the new file prompts.txt with only the first column (prompts)
    prompt_txt_path = os.path.join(os.path.dirname(file_path), 'prompts.txt')
    with open(prompt_txt_path, 'w') as file:
        for prompt in prompts_only:
            file.write(prompt + '\n')


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="Process prompts from a text file")
    parser.add_argument("--prompt_path", type=str, default="/home/ubuntu/t2v-view/prompts.csv", help="Path to the prompt text file")
    prompt_path = parser.parse_args().prompt_path

    try:
        process_prompts(prompt_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
