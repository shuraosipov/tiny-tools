import os
import json
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
import subprocess
from aws_wat_integration import AWSWellArchitectedToolIntegration

class DevOpsMaturityTool:
    def __init__(self):
        # Initialize AWS WAT integration
        self.wat_integration = AWSWellArchitectedToolIntegration()
        # Define the assessment structure
        self.domains = {
            "organizational_adoption": {
                "title": "Organizational Adoption",
                "areas": {
                    "leader_sponsorship": {
                        "title": "Leader Sponsorship",
                        "description": "Obtaining leader sponsorship of DevOps adoption initiatives helps verify that the organization's leadership is committed to and actively supports the adoption of DevOps practices.",
                        "indicators": [
                            {"id": "OA.LS.1", "text": "Appoint a decision-making leader to own DevOps adoption"},
                            {"id": "OA.LS.2", "text": "Align DevOps adoption with business objectives"},
                            {"id": "OA.LS.3", "text": "Drive continued improvement through business reviews"},
                            {"id": "OA.LS.4", "text": "Open dialogue between leadership and teams"},
                            {"id": "OA.LS.5", "text": "Assemble a cross-functional enabling team that focuses on organizational transformation"}
                        ]
                    },
                    "supportive_team_dynamics": {
                        "title": "Supportive Team Dynamics",
                        "description": "Create a collaborative atmosphere that emphasizes ownership and shared accountability and organizes teams to serve their internal and external customers.",
                        "indicators": [
                            {"id": "OA.STD.1", "text": "Organize teams into distinct topology types to optimize the value stream"},
                            {"id": "OA.STD.2", "text": "Tailor operating models to business needs and team preferences"},
                            {"id": "OA.STD.3", "text": "Prioritize shared accountability over individual achievements"},
                            {"id": "OA.STD.4", "text": "Structure teams around desired business outcomes"},
                            {"id": "OA.STD.5", "text": "Establish team norms that enhance work performance"},
                            {"id": "OA.STD.6", "text": "Provide teams ownership of the entire value stream for their product"},
                            {"id": "OA.STD.7", "text": "Amplify the scale and impact of centralized functions"},
                            {"id": "OA.STD.8", "text": "Promote cognitive diversity within teams"}
                        ]
                    },
                    "team_interfaces": {
                        "title": "Team Interfaces",
                        "description": "Implement mechanisms to enhance productivity within and across teams, providing effective communication channels to guide the flow of work.",
                        "indicators": [
                            {"id": "OA.TI.1", "text": "Communicate work flow and goals between teams and stakeholders"},
                            {"id": "OA.TI.2", "text": "Streamline intra-team communication using tools and processes"},
                            {"id": "OA.TI.3", "text": "Establish mechanisms for teams to gather and manage customer feedback"},
                            {"id": "OA.TI.4", "text": "Refine error tracking and resolution"},
                            {"id": "OA.TI.5", "text": "Design adaptive approval workflows without compromising safety"},
                            {"id": "OA.TI.6", "text": "Prioritize customer needs to deliver optimal business outcomes"},
                            {"id": "OA.TI.7", "text": "Maintain a unified knowledge source for teams"},
                            {"id": "OA.TI.8", "text": "Simplify access to organizational information"},
                            {"id": "OA.TI.9", "text": "Facilitate self-service collaboration through APIs and documentation"},
                            {"id": "OA.TI.10", "text": "Choose interaction modes for improved efficiency and cost savings"},
                            {"id": "OA.TI.11", "text": "Offer optional opportunities for cross-team collaboration"}
                        ]
                    }
                    # Additional areas would be defined similarly
                }
            }
            # Additional domains would be defined similarly
        }
        self.responses = {}
        self.total_questions = self.count_total_questions()
        self.answered_questions = 0

    def count_total_questions(self) -> int:
        total = 0
        for domain in self.domains.values():
            for area in domain['areas'].values():
                total += len(area['indicators'])
        return total

    def clear_screen(self):
        subprocess.run(['cls' if os.name == 'nt' else 'clear'], shell=True) # import subprocess

    def print_progress_bar(self):
        width = 50
        progress = self.answered_questions / self.total_questions
        filled = int(width * progress)
        bar = '█' * filled + '░' * (width - filled)
        percentage = progress * 100
        print(f"Progress: [{bar}] {percentage:.1f}%")
        print(f"Questions answered: {self.answered_questions}/{self.total_questions}\n")

    def print_header(self, text: str):
        self.clear_screen()
        print("=" * 80)
        self.print_progress_bar()
        print("=" * 80)
        print(text.center(80))
        print("=" * 80)
        print()

    def get_yes_no_input(self, indicator: Dict) -> bool:
        while True:
            print(f"\n[{indicator['id']}] {indicator['text']}")
            response = input("Implemented (y/n)? ").lower().strip()
            if response in ['y', 'yes']:
                self.answered_questions += 1
                return True
            elif response in ['n', 'no']:
                self.answered_questions += 1
                return False
            print("Please enter 'y' or 'n'")

    def run_assessment(self):
        for domain_key, domain_data in self.domains.items():
            self.responses[domain_key] = {}
            
            for area_key, area_data in domain_data['areas'].items():
                self.print_header(f"{domain_data['title']} - {area_data['title']}")
                print(f"Description: {area_data['description']}\n")
                
                self.responses[domain_key][area_key] = []
                
                for indicator in area_data['indicators']:
                    response = self.get_yes_no_input(indicator)
                    self.responses[domain_key][area_key].append({
                        'id': indicator['id'],
                        'text': indicator['text'],
                        'implemented': response
                    })

    def calculate_statistics(self) -> Dict:
        stats = {
            'overall': {'implemented': 0, 'total': 0},
            'by_domain': defaultdict(lambda: {'implemented': 0, 'total': 0}),
            'by_area': defaultdict(lambda: {'implemented': 0, 'total': 0})
        }
        
        for domain_key, domain_responses in self.responses.items():
            for area_key, indicators in domain_responses.items():
                area_path = f"{domain_key}.{area_key}"
                
                for indicator in indicators:
                    stats['overall']['total'] += 1
                    stats['by_domain'][domain_key]['total'] += 1
                    stats['by_area'][area_path]['total'] += 1
                    
                    if indicator['implemented']:
                        stats['overall']['implemented'] += 1
                        stats['by_domain'][domain_key]['implemented'] += 1
                        stats['by_area'][area_path]['implemented'] += 1
        
        return stats

    def generate_report(self):
        self.print_header("DevOps Maturity Assessment Report")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Report generated on: {timestamp}\n")
        
        stats = self.calculate_statistics()
        
        # Overall Progress
        overall_percentage = (stats['overall']['implemented'] / stats['overall']['total'] * 100)
        print(f"Overall Progress: {stats['overall']['implemented']}/{stats['overall']['total']} ({overall_percentage:.1f}%)\n")
        
        # Domain-level Statistics
        for domain_key, domain_data in self.domains.items():
            domain_stats = stats['by_domain'][domain_key]
            domain_percentage = (domain_stats['implemented'] / domain_stats['total'] * 100)
            
            print(f"\n{domain_data['title']}:")
            print(f"Progress: {domain_stats['implemented']}/{domain_stats['total']} ({domain_percentage:.1f}%)")
            
            # Area-level Statistics
            for area_key, area_data in domain_data['areas'].items():
                area_path = f"{domain_key}.{area_key}"
                area_stats = stats['by_area'][area_path]
                area_percentage = (area_stats['implemented'] / area_stats['total'] * 100)
                
                print(f"\n  {area_data['title']}:")
                print(f"  Progress: {area_stats['implemented']}/{area_stats['total']} ({area_percentage:.1f}%)")
                
                # Individual Indicators
                for indicator in self.responses[domain_key][area_key]:
                    status = "✓" if indicator['implemented'] else "✗"
                    print(f"    {status} [{indicator['id']}] {indicator['text']}")
        
        self.save_report(stats)

    def save_report(self, stats: Dict):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"devops_assessment_{timestamp}.json"
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'responses': self.responses,
            'statistics': stats
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"\nJSON report saved to {filename}")
        
        # Generate PDF report
        pdf_filename = self.wat_integration.generate_pdf_report(
            workload_id='default',  # You might want to make this configurable
            assessment_data=report_data
        )
        print(f"PDF report saved to {pdf_filename}")

def main():
    tool = DevOpsMaturityTool()
    tool.run_assessment()
    tool.generate_report()

if __name__ == "__main__":
    main()