import os
import time
import re
import json
import openai
import logging
import http.client
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("jarvis")

# Enable OpenAI API request logging
http.client.HTTPConnection.debuglevel = 0

# Log all OpenAI requests and responses
class APILogger:
    @staticmethod
    def log_request(method, url, headers, data):
        logger.info(f"API Request: {method} {url}")
        logger.debug(f"Request Headers: {headers}")
        logger.debug(f"Request Data: {data}")
    
    @staticmethod
    def log_response(status_code, headers, content):
        logger.info(f"API Response: Status {status_code}")
        logger.debug(f"Response Headers: {headers}")
        # Log a truncated version of the content to avoid overwhelming logs
        content_preview = str(content)[:500] + "..." if len(str(content)) > 500 else content
        logger.debug(f"Response Content: {content_preview}")

# Setup OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

SYSTEM_PROMPT = """DO NOT REWRITE main.py file. It is the main file of the project. 
You are Jarvis, a self-improving AI running inside a Python process with full system access, 
long-term memory, contextual information, and all available tools on this computer (including internet access and OS-level commands). 
Your task is to create a working Python project based on the provided instructions. 
The project must include complete, functional code along with tests and documentation. 
Output a valid JSON object where each key is a filename (for example, 'main.py', 'test_main.py', 'README.md') 
and each value is the complete file content. Do not include any additional text."""

INPUT_FILE = "input.txt"
LOG_DIR = "logs"


def setup_communication_logging():
    """Set up detailed logging for API communications"""
    # Create logs directory if it doesn't exist
    Path(LOG_DIR).mkdir(exist_ok=True)
    
    # Create a file handler for API communications
    api_log_file = Path(LOG_DIR) / f"api_communications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(api_log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Add the handler to the logger
    api_logger = logging.getLogger("api_communications")
    api_logger.setLevel(logging.DEBUG)
    api_logger.addHandler(file_handler)
    
    return api_logger


# Initialize API communication logger
api_logger = setup_communication_logging()


def call_gpt4(user_input, retries=3, backoff_factor=2):
    """Call GPT-4 API with retry logic, exponential backoff, and detailed logging"""
    for attempt in range(retries):
        try:
            logger.info(f"Calling GPT-4 API (attempt {attempt+1}/{retries})...")
            
            # Prepare request data
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
            request_data = {
                "model": "gpt-4",
                "messages": messages
            }
            
            # Log request details
            api_logger.info(f"Request to GPT-4 API:")
            api_logger.info(f"System prompt: {SYSTEM_PROMPT[:100]}...")
            api_logger.info(f"User input: {user_input[:100]}...")
            
            # Measure response time
            start_time = time.time()
            
            # Make the API call
            response = openai.chat.completions.create(**request_data)
            
            # Calculate response time
            elapsed_time = time.time() - start_time
            logger.info(f"HTTP Request: POST https://api.openai.com/v1/chat/completions \"HTTP/1.1 {response.model_dump().get('response_ms', 'N/A')} ms\"")
            logger.info(f"API response received in {elapsed_time:.2f} seconds")
            
            # Log response details
            content = response.choices[0].message.content
            api_logger.info(f"Response from GPT-4 API:")
            api_logger.info(f"Completion ID: {response.id}")
            api_logger.info(f"Model used: {response.model}")
            api_logger.info(f"Response content (first 200 chars): {content[:200]}...")
            api_logger.info(f"Full raw response: {json.dumps(response.model_dump(), indent=2)}")
            
            # Log content to main log with reduced verbosity
            content_preview = content[:100] + "..." if len(content) > 100 else content
            logger.info(f"GPT-4 response preview: {content_preview}")
            
            return content
            
        except Exception as e:
            logger.warning(f"API call failed: {e}")
            api_logger.error(f"API call error details: {str(e)}")
            
            if attempt < retries - 1:
                sleep_time = backoff_factor ** attempt
                logger.warning(f"Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                logger.error(f"Failed after {retries} attempts: {e}")
                return None


def parse_json_response(text):
    """Extract and parse JSON from GPT response with improved pattern matching and verbose logging"""
    if not text:
        logger.error("No response text to parse")
        return None
    
    logger.info("Parsing JSON response...")
    api_logger.info(f"Attempting to parse JSON from response of length {len(text)}")
    
    # Try to find JSON in code blocks first
    pattern = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)
    matches = pattern.findall(text)
    
    if matches:
        logger.info(f"Found {len(matches)} JSON code blocks in response")
        json_text = matches[-1].strip()
        api_logger.info(f"Selected JSON from code block: {json_text[:200]}...")
    else:
        # Fall back to extracting from the first '{' to the last '}'
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            logger.info(f"Extracting JSON from text positions {start} to {end}")
            json_text = text[start:end+1].strip()
            api_logger.info(f"Extracted JSON: {json_text[:200]}...")
        else:
            logger.error("No JSON block found in the response.")
            api_logger.error("JSON extraction failed: No valid JSON block found in response")
            return None
    
    try:
        parsed = json.loads(json_text)
        logger.info(f"Successfully parsed JSON with {len(parsed)} keys")
        api_logger.info(f"Parsed JSON keys: {list(parsed.keys())}")
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        api_logger.error(f"JSON parsing error: {str(e)}")
        api_logger.error(f"Attempted to parse: {json_text[:500]}...")
        return None


def save_project_files(files_dict):
    """Save each file from the JSON dictionary with better path handling and verbose logging"""
    if not files_dict:
        logger.error("No files to save - empty dictionary provided")
        return False
    
    logger.info(f"Saving {len(files_dict)} project files...")
    api_logger.info(f"File saving started for: {list(files_dict.keys())}")
    
    success_count = 0
    total_count = len(files_dict)
    
    for filename, content in files_dict.items():
        file_path = Path(filename)
        
        # Create parent directories if they don't exist
        if file_path.parent != Path('.'):
            logger.info(f"Creating directory: {file_path.parent}")
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Log file details    
        content_length = len(content)
        content_preview = content[:100] + "..." if content_length > 100 else content
        api_logger.info(f"Saving file '{filename}' (length: {content_length} chars)")
        api_logger.info(f"Content preview: {content_preview}")
        
        try:
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Saved file: {filename}")
            success_count += 1
        except Exception as e:
            logger.error(f"Error saving file '{filename}': {e}")
            api_logger.error(f"File saving error for '{filename}': {str(e)}")
    
    logger.info(f"File saving completed: {success_count}/{total_count} files saved successfully")
    return success_count > 0


def main():
    logger.info("Starting Jarvis AI project generator...")
    
    # Create input file if it doesn't exist
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        user_instruction = input("Enter your project instructions: ").strip()
        input_path.write_text(user_instruction, encoding="utf-8")
        logger.info(f"Instructions saved to {INPUT_FILE}")
    
    logger.info("Jarvis self-improving mechanism is running. Checking for instructions every 10 seconds...\n")
    api_logger.info("Jarvis monitoring started")
    
    last_modified = 0
    
    while True:
        try:
            # Check if input file exists
            if not input_path.exists():
                logger.info(f"Input file {INPUT_FILE} not found. Creating empty file.")
                input_path.touch()
                continue
            
            # Check if file has been modified
            current_modified = input_path.stat().st_mtime
            
            # Only process if file has been modified
            if current_modified > last_modified:
                instructions = input_path.read_text(encoding="utf-8").strip()
                last_modified = current_modified
                
                if not instructions:
                    logger.info("Empty instructions file. Waiting for content...")
                    continue
                
                modification_time = time.ctime(current_modified)
                logger.info(f"Processing instructions (modified at {modification_time})...")
                api_logger.info(f"Processing new instructions from {INPUT_FILE}")
                api_logger.info(f"Instructions: {instructions}")
                
                # Call GPT-4 API
                response = call_gpt4(instructions)
                
                if not response:
                    logger.error("Failed to get response from GPT-4")
                    continue
                
                # Parse and save project files
                project_files = parse_json_response(response)
                
                if save_project_files(project_files):
                    logger.info("Project generated and saved successfully.")
                    # Clear instructions after successful processing
                    input_path.write_text("", encoding="utf-8")
                    api_logger.info("Project generation completed successfully. Input file cleared.")
                else:
                    logger.error("Failed to generate valid project files.")
                    api_logger.error("Project generation failed: Invalid or empty project files")
            else:
                logger.info("Waiting for instructions...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            api_logger.error(f"Runtime error: {str(e)}")
            
        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nJarvis process terminated by user.")
        api_logger.info("Jarvis process terminated by user (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        api_logger.critical(f"Fatal error caused program termination: {str(e)}")