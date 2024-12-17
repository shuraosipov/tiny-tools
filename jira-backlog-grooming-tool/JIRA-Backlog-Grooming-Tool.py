import logging
import asyncio
import questionary
from rich.console import Console
from rich.table import Table
from datetime import datetime
from typing import List, Dict

class MockJiraData:
    """Provides mock JIRA issues for testing without JIRA access."""
    
    @staticmethod
    def get_mock_issues():
        return [
            {
                'key': 'PROJ-101',
                'type': 'Story',
                'priority': 'High',
                'status': 'To Do',
                'title': 'Implement user authentication system',
                'description': """As a user, I want to securely log into the application using my email and password.

Acceptance Criteria:
- Users can sign up with email and password
- Password requirements enforced (min 8 chars, special chars, numbers)
- Email verification required
- Password reset functionality
- Login with email/password
- Session management
- Account lockout after failed attempts

Technical Notes:
- Consider using OAuth 2.0
- Need to integrate with existing user database
- Rate limiting required for security""",
                'assignee': 'Jane Smith',
                'created': '2024-03-15 10:30',
                'updated': '2024-03-16 14:20',
                'last_comment': "Security team needs to review the implementation plan."
            },
            {
                'key': 'PROJ-102',
                'type': 'Story',
                'priority': 'Medium',
                'status': 'To Do',
                'title': 'Design and implement product search functionality',
                'description': """Need to add search capability to the product catalog.

- Search by name
- Filter by category
- Sort results
- Price range filter""",
                'assignee': 'Unassigned',
                'created': '2024-03-14 09:15',
                'updated': '2024-03-14 09:15',
                'last_comment': "No comments"
            },
            {
                'key': 'PROJ-103',
                'type': 'Bug',
                'priority': 'High',
                'status': 'To Do',
                'title': 'Fix memory leak in data processing service',
                'description': """Memory usage gradually increases over time in the data processing service, requiring regular restarts.

Impact:
- Service requires restart every 48 hours
- Processing speed degradation
- Increased cloud costs

Steps to reproduce:
1. Run service under normal load
2. Monitor memory usage over 24 hours
3. Observe steady increase in memory consumption

Current findings:
- Happens most notably during batch processing
- Memory not properly released after large file processing
- Garbage collection logs show potential circular references""",
                'assignee': 'Bob Johnson',
                'created': '2024-03-16 16:45',
                'updated': '2024-03-17 11:30',
                'last_comment': "Profiling tools have been set up to track memory allocation patterns."
            }
        ]

class GroomingQuestions:
    """Defines standard grooming evaluation questions and their weights."""
    
    QUESTIONS = [
        {
            "text": "Is the user story written from end-user perspective?",
            "weight": 1.0,
            "category": "clarity"
        },
        {
            "text": "Are acceptance criteria clearly defined?",
            "weight": 1.5,
            "category": "requirements"
        },
        {
            "text": "Is the business value clearly articulated?",
            "weight": 1.2,
            "category": "value"
        },
        {
            "text": "Is the scope well-defined and contained?",
            "weight": 1.3,
            "category": "scope"
        },
        {
            "text": "Are all dependencies identified?",
            "weight": 1.1,
            "category": "technical"
        },
        {
            "text": "Is the technical approach clear?",
            "weight": 1.2,
            "category": "technical"
        },
        {
            "text": "Can this be completed within one sprint?",
            "weight": 1.4,
            "category": "size"
        },
        {
            "text": "Are there clear test scenarios?",
            "weight": 1.0,
            "category": "quality"
        },
        {
            "text": "Is this story independent (can be developed in isolation)?",
            "weight": 1.1,
            "category": "technical"
        },
        {
            "text": "Is all necessary information available to start development?",
            "weight": 1.3,
            "category": "readiness"
        }
    ]

    @classmethod
    def calculate_score(cls, answers: Dict[str, bool]) -> float:
        """Calculate weighted score based on answers."""
        total_weight = sum(q["weight"] for q in cls.QUESTIONS)
        score = sum(q["weight"] for q, answer in zip(cls.QUESTIONS, answers.values()) if answer)
        return (score / total_weight) * 100

    @classmethod
    def get_readiness_level(cls, score: float) -> str:
        """Determine readiness level based on score."""
        if score >= 90:
            return "Ready for Sprint"
        elif score >= 75:
            return "Minor Refinements Needed"
        elif score >= 50:
            return "Needs Discussion"
        else:
            return "Significant Refinement Required"

class MockJira:
    """Mock JIRA client for testing without JIRA access."""
    
    def __init__(self, server=None, basic_auth=None):
        self.mock_data = MockJiraData()
    
    def search_issues(self, jql_query, maxResults=1000, fields=None):
        return self.mock_data.get_mock_issues()
    
    def comments(self, issue):
        return [type('Comment', (), {'body': issue['last_comment']})]

class JiraGroomingPrep:
    def __init__(self):
        """Initialize with mock data."""
        self.console = Console()
        self.jira = MockJira()
        logging.info("Using mock JIRA data for testing")

    async def review_ticket(self, ticket: Dict) -> Dict:
        """Interactively review a single ticket."""
        self.console.clear()
        self.console.print(f"\n[bold blue]Reviewing Ticket: {ticket['key']} - {ticket['title']}[/bold blue]")
        self.console.print("\n[yellow]Description:[/yellow]")
        self.console.print(ticket['description'])
        self.console.print(f"\n[yellow]Assignee:[/yellow] {ticket['assignee']}")
        self.console.print(f"[yellow]Status:[/yellow] {ticket['status']}")
        self.console.print(f"[yellow]Last Comment:[/yellow] {ticket['last_comment']}\n")

        answers = {}
        for question in GroomingQuestions.QUESTIONS:
            answer = await questionary.confirm(
                question["text"],
                default=False
            ).ask_async()
            answers[question["text"]] = answer

        score = GroomingQuestions.calculate_score(answers)
        readiness = GroomingQuestions.get_readiness_level(score)
        
        ticket['grooming_score'] = score
        ticket['readiness_level'] = readiness
        ticket['evaluation_answers'] = answers

        self.console.print(f"\n[bold green]Score: {score:.1f}%[/bold green]")
        self.console.print(f"[bold]Readiness Level: {readiness}[/bold]\n")
        
        if score >= 75:
            story_points = await questionary.select(
                "Estimate story points:",
                choices=['1', '2', '3', '5', '8', '13', '21']
            ).ask_async()
            ticket['story_points'] = int(story_points)
        
        return ticket

    async def review_backlog(self, project_key: str = "MOCK") -> List[Dict]:
        """Review all backlog items interactively."""
        try:
            issues = self.jira.search_issues(
                f"project = {project_key}",
                maxResults=1000
            )
            
            reviewed_items = []
            for issue in issues:
                reviewed_ticket = await self.review_ticket(issue)
                reviewed_items.append(reviewed_ticket)
                
                if len(reviewed_items) < len(issues):
                    continue_review = await questionary.confirm(
                        "\nContinue to next ticket?",
                        default=True
                    ).ask_async()
                    if not continue_review:
                        break
            
            return reviewed_items
            
        except Exception as e:
            logging.error(f"Error during backlog review: {str(e)}")
            raise

    def generate_review_report(self, items: List[Dict], output_file: str = 'grooming_results.md'):
        """Generate a detailed report of the grooming session."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# Backlog Grooming Session Results\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                
                f.write("## Summary\n\n")
                f.write("| Metric | Value |\n")
                f.write("|--------|-------|\n")
                f.write(f"| Total Items Reviewed | {len(items)} |\n")
                f.write(f"| Ready for Sprint | {sum(1 for i in items if i['grooming_score'] >= 90)} |\n")
                f.write(f"| Needs Minor Refinement | {sum(1 for i in items if 75 <= i['grooming_score'] < 90)} |\n")
                f.write(f"| Needs Major Refinement | {sum(1 for i in items if i['grooming_score'] < 75)} |\n\n")
                
                f.write("## Detailed Results\n\n")
                for item in items:
                    f.write(f"### [{item['key']}] {item['title']}\n\n")
                    f.write(f"**Score:** {item['grooming_score']:.1f}%  \n")
                    f.write(f"**Readiness Level:** {item['readiness_level']}  \n")
                    if 'story_points' in item:
                        f.write(f"**Story Points:** {item['story_points']}  \n")
                    f.write("\n**Evaluation Details:**\n\n")
                    
                    for question, answer in item['evaluation_answers'].items():
                        f.write(f"- {question}: {'✅' if answer else '❌'}\n")
                    
                    f.write("\n---\n\n")
            
            logging.info(f"Generated grooming report: {output_file}")
            
        except Exception as e:
            logging.error(f"Error generating grooming report: {str(e)}")
            raise

async def main():
    logging.basicConfig(level=logging.INFO)
    
    try:
        grooming_prep = JiraGroomingPrep()
        reviewed_items = await grooming_prep.review_backlog()
        grooming_prep.generate_review_report(reviewed_items)
        
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())