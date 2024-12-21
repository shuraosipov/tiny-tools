# WBS Generator Tool

A command-line tool for generating Work Breakdown Structure (WBS) documents in Markdown format.

## Features
- Interactive project data collection
- Rich terminal UI with progress bars and colored output
- Validates user input
- Generates structured Markdown output
- Supports:
  - Project information
  - Requirements
  - Constraints
  - Deliverables with subtasks
  - Risks with mitigation strategies
  - Resource planning

## Installation

```bash
git clone ttps://github.com/shuraosipov/tiny-tools.git
cd tiny-tools/wbs-generator-tool
pip install -r requirements.txt
```

## Usage
```
python src/wbs_generator.py
```
Follow the interactive prompts to input your project details.

## Running Tests
```
pytest test/test_wbs_generator.py -v
```
