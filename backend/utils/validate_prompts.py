import sys

def process_prompts(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        cleaned_lines = []
        for line in lines:
            prompt = line.strip()

            # Check if the prompt exceeds 500 characters
            if len(prompt) > 500:
                print(f"Error: The following prompt exceeds 500 characters:\n{prompt}")
                sys.exit(1)

            # Remove forward slashes from the prompt
            cleaned_prompt = prompt.replace("/", "")
            cleaned_lines.append(cleaned_prompt)

        # Write cleaned prompts back to the file
        with open(file_path, 'w') as file:
            for cleaned_line in cleaned_lines:
                file.write(cleaned_line + '\n')

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="Process prompts from a text file")
    parser.add_argument("--prompt_path", type=str, default="/home/ubuntu/t2v-view/prompts.txt", help="Path to the prompt text file")
    prompt_path = parser.parse_args().prompt_path
    
    process_prompts(prompt_path)
