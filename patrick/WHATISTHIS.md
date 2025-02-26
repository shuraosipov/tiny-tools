## What This Tool Does

This is a self-improving project generator that:
1. Takes instructions from an `input.txt` file
2. Sends those instructions to GPT-4 with a specific system prompt
3. Parses the JSON response from GPT-4
4. Automatically creates project files based on the response

## Best Use Cases

This tool would be ideal for:

1. **Rapid Prototyping**: Quickly generate starter code for new projects
2. **Learning New Frameworks**: Generate example projects to understand how different technologies work together
3. **Boilerplate Generation**: Create standard project structures with tests and documentation
4. **Code Challenges**: Generate solutions to coding challenges with complete tests
5. **Documentation Generation**: Create README files and documentation for existing code

## Example Prompts and Input Instructions

Here are some effective instructions you could place in the `input.txt` file:

### Example 1: Web Scraper

```
Create a Python web scraper that extracts product information from an e-commerce website. The scraper should:
1. Accept a URL as input
2. Extract product names, prices, and descriptions
3. Save the data to a CSV file
4. Handle pagination
5. Include error handling for network issues
6. Include unit tests and documentation
```

### Example 2: Data Visualization Tool

```
Create a data visualization tool using Python that:
1. Reads data from CSV files
2. Creates various charts (bar, line, scatter plots)
3. Allows customization of colors and labels
4. Saves visualizations as PNG files
5. Includes a command-line interface
6. Has comprehensive documentation and examples
```

### Example 3: REST API

```
Create a REST API using Flask that:
1. Provides CRUD operations for a 'task' resource
2. Includes user authentication using JWT
3. Connects to a SQLite database
4. Has proper error handling and status codes
5. Includes Swagger documentation
6. Has unit tests for all endpoints
```

## Important Notes and Improvements

1. **Security Concerns**: The script uses environment variables for the API key, which is good, but be careful about what you instruct the AI to generate, as it has "self-improving" capabilities.

2. **Error Handling**: The script has basic error handling, but you might want to add more robust error recovery mechanisms.

3. **Persistence**: Consider adding a log file to track which projects have been generated and when.

4. **Specificity**: When writing instructions, be as specific as possible about the technologies, design patterns, and code quality requirements you want.

5. **Resource Management**: The script continuously polls for instructions every 10 seconds. For production use, you might want a more efficient trigger mechanism.

To use this tool:
1. Set your OpenAI API key as an environment variable: `OPENAI_API_KEY`
2. Run the script: `python patrick.py`
3. Enter your initial instructions or edit the `input.txt` file directly
4. The script will generate your project files in the current directory