import os, time, re, json, openai, logging
from pathlib import Path
from datetime import datetime

# Configuration
INPUT_FILE = "input.txt"
LOG_DIR = "logs"
SYSTEM_PROMPT = """DO NOT REWRITE main.py file. It is the main file of the project. 
You are Jarvis, a self-improving AI running inside a Python process with full system access. 
Output a valid JSON object where each key is a filename and each value is the file content."""

# Setup logging
Path(LOG_DIR).mkdir(exist_ok=True)
log_file = Path(LOG_DIR) / f"jarvis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(), logging.FileHandler(log_file)])
logger = logging.getLogger("jarvis")

# Check API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

def call_gpt4(user_input, retries=3):
    """Call GPT-4 API with retry logic"""
    for attempt in range(retries):
        try:
            logger.info(f"Calling GPT-4 API (attempt {attempt+1}/{retries})")
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"API call failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    logger.error(f"Failed after {retries} attempts")
    return None

def parse_json_response(text):
    """Extract and parse JSON from response"""
    if not text:
        return None
    
    # Try code blocks first, then fallback to raw extraction
    matches = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    json_text = matches[-1].strip() if matches else text[text.find('{'):text.rfind('}')+1]
    
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return None

def save_project_files(files_dict):
    """Save files from JSON dictionary"""
    if not files_dict:
        return False
    
    success = 0
    for filename, content in files_dict.items():
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Saved: {filename}")
            success += 1
        except Exception as e:
            logger.error(f"Error saving '{filename}': {e}")
    
    return success > 0

def main():
    logger.info("Starting Jarvis AI project generator")
    input_path = Path(INPUT_FILE)
    
    # Create input file if needed
    if not input_path.exists():
        input_path.write_text(input("Enter project instructions: ").strip())
    
    last_modified = 0
    
    while True:
        try:
            # Ensure input file exists
            if not input_path.exists():
                input_path.touch()
                continue
            
            # Check for modifications
            current_modified = input_path.stat().st_mtime
            if current_modified > last_modified:
                instructions = input_path.read_text(encoding="utf-8").strip()
                last_modified = current_modified
                
                if instructions:
                    logger.info(f"Processing instructions")
                    response = call_gpt4(instructions)
                    project_files = parse_json_response(response)
                    
                    if project_files and save_project_files(project_files):
                        logger.info("Project generated successfully")
                        input_path.write_text("")  # Clear instructions
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
        time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Jarvis terminated by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")