# JIRA Backlog Grooming Tool

An interactive command-line tool for conducting structured backlog grooming sessions. The tool helps teams evaluate backlog items systematically using industry best practices and generates detailed reports for tracking grooming outcomes.

## Features

- 🔄 Interactive ticket-by-ticket review process
- ✨ Standardized evaluation criteria based on agile best practices
- 📊 Weighted scoring system for ticket readiness assessment
- 📝 Story point estimation for sprint-ready items
- 📋 Detailed markdown reports generation
- 🧪 Mock data support for testing and demonstration
- 🎯 Readiness level classification

## Requirements

- Python 3.9+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/shuraosipov/tiny-tools.git
cd tiny-tools/jira-backlog-grooming-tool
```

2. Install required packages:
```bash
pip install questionary rich
```

3. For JIRA integration (optional):
```bash
pip install jira
```

## Usage

### Quick Start with Mock Data

To test the tool with sample data:

```bash
python JIRA-Backlog-Grooming-Tool.py
```

### Using with JIRA

1. Set up environment variables:
```bash
export JIRA_SERVER='https://your-domain.atlassian.net'
export JIRA_EMAIL='your-email@example.com'
export JIRA_API_TOKEN='your-api-token'
export JIRA_PROJECT_KEY='YOUR_PROJECT'
```

2. Update the script to use JIRA connection instead of mock data.

## Evaluation Criteria

The tool evaluates each backlog item against 10 key criteria:

1. User Story Perspective (weight: 1.0)
2. Acceptance Criteria (weight: 1.5)
3. Business Value (weight: 1.2)
4. Scope Definition (weight: 1.3)
5. Dependencies (weight: 1.1)
6. Technical Approach (weight: 1.2)
7. Sprint Fit (weight: 1.4)
8. Test Scenarios (weight: 1.0)
9. Independence (weight: 1.1)
10. Information Completeness (weight: 1.3)

### Readiness Levels

Based on the weighted score, items are classified into:

- 90%+ : Ready for Sprint
- 75-89% : Minor Refinements Needed
- 50-74% : Needs Discussion
- <50% : Significant Refinement Required

## Output

The tool generates a markdown report (`grooming_results.md`) containing:

- Session summary statistics
- Detailed per-ticket evaluation results
- Story point estimates for sprint-ready items
- Question-by-question responses
- Readiness levels and scores

## Project Structure

```
jira-backlog-grooming-tool/
├── JIRA-Backlog-Grooming-Tool.py    # Main script
├── README.md                         # This file
└── grooming_results.md              # Generated report
```

## Classes

### JiraGroomingPrep
Main class handling the grooming process, including ticket review and report generation.

### GroomingQuestions
Defines evaluation criteria, weights, and scoring logic.

### MockJira & MockJiraData
Provides sample data for testing without JIRA access.

## Contributing

Contributions are welcome! Some areas for potential enhancement:

- Additional evaluation criteria
- Custom scoring algorithms
- Report format options
- JIRA integration improvements
- UI enhancements
- Testing framework

## License

MIT License. See LICENSE file for details.

## Acknowledgments

This tool implements backlog grooming best practices from various agile methodologies and industry standards.

## Support

For issues and feature requests, please use the GitHub issues page.

For questions about using JIRA with this tool, refer to [Atlassian's JIRA API documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/).