import os
import time
import re
import json
import openai

# Load API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

def system_prompt():
    return (
        "DO NOT REWRITE main.py file. It is the main file of the project. "
        "You are Jarvis, a self-improving AI running inside a Python process with full system access, "
        "long-term memory, contextual information, and all available tools on this computer (including internet access and OS-level commands). "
        "Your task is to create a working Python project based on the provided instructions. "
        "The project must include complete, functional code along with tests and documentation. "
        "Output a valid JSON object where each key is a filename (for example, 'main.py', 'test_main.py', 'README.md') "
        "and each value is the complete file content. Do not include any additional text."
    )

def call_gpt4(user_input):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt()},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def extract_json_block(text):
    """
    Extract a JSON block from the text.
    First, try to find a code block tagged as JSON.
    If not found, fall back to extracting from the first '{' onward.
    """
    pattern = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)
    matches = pattern.findall(text)
    if matches:
        return matches[-1].strip()
    idx = text.find('{')
    if idx != -1:
        return text[idx:].strip()
    return None

def parse_json_response(text):
    """Extract and parse the JSON from the GPT response."""
    json_text = extract_json_block(text)
    if not json_text:
        print("No JSON block found in the response.")
        return None
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("JSON Text was:", json_text)
        return None

def save_project_files(files_dict):
    """Save each file from the JSON dictionary to the local directory."""
    for filename, content in files_dict.items():
        # If content contains literal "\n" but no actual newline, convert them
        if "\\n" in content and "\n" not in content:
            content = content.replace("\\n", "\n")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved file: {filename}")
        except Exception as e:
            print(f"Error saving file '{filename}':", e)

def main():
    # Ask for instructions on startup and write them to input.txt
    user_instruction = input("Enter your project instructions: ").strip()
    with open("input.txt", "w", encoding="utf-8") as f:
        f.write(user_instruction)
    
    print("\nJarvis self-improving mechanism is running. Checking for instructions every 10 seconds...\n")
    
    while True:
        try:
            with open("input.txt", "r", encoding="utf-8") as f:
                instructions = f.read().strip()
        except FileNotFoundError:
            instructions = ""
        
        if instructions:
            print("Instructions received:")
            print(instructions)
            print("\nCalling GPT-4 to generate your project...")
            response = call_gpt4(instructions)
            print("\nGPT-4 raw response:\n", response)
            project_files = parse_json_response(response)
            if project_files and isinstance(project_files, dict):
                save_project_files(project_files)
                print("Project generated and saved locally.")
                # Optionally clear instructions after successful processing:
                with open("input.txt", "w", encoding="utf-8") as f:
                    f.write("")
            else:
                print("No valid project files were generated.")
        else:
            print("No instructions found in input.txt. Waiting for instructions...")
        
        time.sleep(10)

if __name__ == "__main__":
    main()
