# DevOps Maturity Assessment Tool

A command-line tool for assessing your organization's DevOps maturity level based on the AWS Well-Architected Framework DevOps lens. This tool helps organizations evaluate their current DevOps practices and identify areas for improvement.

## Features

- Interactive command-line interface
- Assessment based on AWS Well-Architected Framework DevOps lens
- Real-time progress tracking
- Detailed reporting with statistics at multiple levels
- JSON export for further analysis
- Visual progress indicators
- Hierarchical assessment structure

## Assessment Domains

The tool covers five main domains of DevOps maturity:

1. **Organizational Adoption**
   - Leader Sponsorship
   - Supportive Team Dynamics
   - Team Interfaces
   - Balanced Cognitive Load
   - Adaptive Work Environment
   - Personal and Professional Development

2. **Development Lifecycle**
   - Coming soon

3. **Quality Assurance**
   - Coming soon

4. **Automated Governance**
   - Coming soon

5. **Observability**
   - Coming soon

## Installation

1. Ensure you have Python 3.6 or higher installed
2. Clone this repository:
```bash
git clone https://github.com/shuraosipov/tiny-tools.git
cd tiny-tools/devops-maturity-assessment-tool
```

## Usage

1. Run the assessment tool:
```bash
python devops_maturity_assessment.py
```

2. Answer each question with 'y' (yes) or 'n' (no)
3. Review the generated report
4. Find the detailed JSON report in the same directory

## Report Structure

The assessment generates both console output and a JSON file containing:

### Console Report
- Overall progress percentage
- Domain-level statistics
- Area-specific scores
- Individual practice implementation status

### JSON Export
```json
{
  "timestamp": "2024-12-16T10:00:00",
  "responses": {
    "domain": {
      "area": [
        {
          "id": "OA.LS.1",
          "text": "Practice description",
          "implemented": true
        }
      ]
    }
  },
  "statistics": {
    "overall": {"implemented": 10, "total": 20},
    "by_domain": {...},
    "by_area": {...}
  }
}
```

## Assessment Progress Tracking

The tool provides real-time progress tracking:
- Visual progress bar
- Questions answered / total questions counter
- Percentage completion

Example:
```
Progress: [██████████░░░░░░░░░░] 33.3%
Questions answered: 10/30
```

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Planned Features

- [ ] Complete implementation of all DevOps domains
- [ ] Save/resume assessment progress
- [ ] Export reports in additional formats (PDF, HTML)
- [ ] Customizable assessment criteria
- [ ] Recommendation engine based on responses
- [ ] Historical trend analysis
- [ ] Team collaboration features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on the AWS Well-Architected Framework DevOps lens
- Inspired by DevOps best practices and industry standards
- Built with Python 3

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Version History

* 0.1
    * Initial Release
    * Basic assessment functionality
    * JSON report generation