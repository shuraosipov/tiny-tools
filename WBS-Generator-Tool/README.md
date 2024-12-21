# WBS Generator Tool

An AI-powered command-line tool for generating comprehensive Work Breakdown Structure (WBS) documents in Markdown format.

## Features
- Interactive project data collection with rich terminal UI
- Test mode with pre-populated data for quick testing
- AI-enhanced WBS generation using OpenAI GPT-4
- Rich terminal UI with progress bars and colored output
- Input validation and structured data collection
- Generates detailed WBS tables with:
  - Task hierarchies
  - Dependencies
  - Timeline estimates
  - Resource assignments
  - Critical path identification
  - Milestones
- AI-powered project analysis including:
  - Critical path analysis
  - Resource optimization
  - Timeline feasibility
  - Risk assessment
  - Delivery optimization

## AI Integration
The tool uses OpenAI's GPT-4 for:
1. Generating detailed WBS tables with realistic estimates
2. Analyzing project structure and dependencies
3. Identifying potential risks and bottlenecks
4. Suggesting optimization strategies
5. Providing resource allocation recommendations

## Installation

1. Clone the repository:
```bash
git clone ttps://github.com/shuraosipov/tiny-tools.git
cd tiny-tools/wbs-generator-tool
pip install -r requirements.txt
```

## Dependencies
- Python 3.9 or higher
- OpenAI API key (for AI features)
- Required Python packages:
  - `rich>=13.7.0`: Terminal UI components
  - `openai>=1.3.0`: OpenAI API integration
  - `python-dateutil>=2.8.2`: Date handling
  - `pytest>=8.3.0`: Testing framework (dev only)
  - `pytest-mock>=3.14.0`: Test mocking (dev only)

## Environment Setup
Set up OpenAI API key:
```
export OPENAI_API_KEY="INSERT_YOUR_OPENAI_API_KEY"
```

## Run
```
python src/wbs_generator.py
```
Follow the interactive prompts to input your project details.

```
python src/wbs_generator.py --test
```
To run the tool in test mode with sample data.

## Running Tests
```
pytest test/test_wbs_generator.py -v
```
