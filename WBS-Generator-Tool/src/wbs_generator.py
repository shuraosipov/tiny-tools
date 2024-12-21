import datetime
from typing import Dict, List, Optional, Callable, Any
import json
import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown
from openai import OpenAI
import argparse  # Add this import at the top


class WBSGenerator:
    """Work Breakdown Structure (WBS) Generator.
    This class helps create a structured WBS document by collecting and organizing project information
    including basic details, requirements, constraints, deliverables, risks and resources.
    The generator prompts users for input interactively and produces a formatted Markdown document
    containing the complete WBS.
    Attributes:
        attributes (list): List of main WBS sections to collect data for
        project_info (dict): Basic project information (name, description, dates, etc)
        requirements (list): Project requirements
        constraints (list): Project constraints and limitations
        deliverables (list): Project deliverables and their details
        risks (list): Project risks and mitigation strategies
        resources (list): Required project resources and skills
    Example:
        generator = WBSGenerator()
        generator.run()  # Starts interactive WBS creation process
    """

    def __init__(self, test_mode=False):
        self.project_info = {}
        self.requirements = []
        self.constraints = []
        self.deliverables = []
        self.risks = []
        self.resources = []
        self.progress_bar = None
        self.console = Console()
        self.openai_client = None
        self.test_mode = test_mode
        self.test_inputs = self._get_test_inputs() if test_mode else {}
        self.test_input_counter = {}
        try:
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except Exception as e:
            self.console.print("[yellow]OpenAI integration not available. Set OPENAI_API_KEY env variable for AI enrichment.[/yellow]")

    def _get_test_inputs(self) -> Dict[str, Any]:
        """Return pre-populated test data"""
        return {
            "project_info": {
                "Project Name": "Test Project",
                "Project Description": "A test project for debugging",
                "Start Date (YYYY-MM-DD)": "2024-01-01",
                "Project Sponsor": "Test Sponsor",
                "Project Manager": "Test Manager",
                "Budget (optional)": "100000"
            },
            "requirements": [
                "Requirement 1: User Authentication",
                "Requirement 2: Data Storage",
                "Requirement 3: API Integration"
            ],
            "constraints": [
                "Budget limit: $100,000",
                "Timeline: 3 months",
                "Team size: 5 people"
            ],
            "deliverables": [
                {
                    "name": "User Authentication System",
                    "description": "Implement secure login system",
                    "duration": "2",
                    "dependencies": "",
                    "subtasks": ["Design DB schema", "Implement OAuth", "Add password reset"]
                },
                {
                    "name": "API Gateway",
                    "description": "Create API gateway for microservices",
                    "duration": "3",
                    "dependencies": "1.0",
                    "subtasks": ["Design API", "Implement routing", "Add rate limiting"]
                }
            ],
            "risks": [
                {
                    "description": "Security vulnerabilities",
                    "probability": "medium",
                    "impact": "high",
                    "mitigation": "Regular security audits"
                },
                {
                    "description": "Technical debt",
                    "probability": "high",
                    "impact": "medium",
                    "mitigation": "Code reviews and refactoring"
                }
            ],
            "resources": [
                {
                    "role": "Backend Developer",
                    "quantity": "2",
                    "skills": "Python, SQL, AWS"
                },
                {
                    "role": "Frontend Developer",
                    "quantity": "1",
                    "skills": "React, TypeScript"
                }
            ]
        }

    def get_test_input(self, category: str, prompt: str) -> str:
        """Get pre-populated test input"""
        if category not in self.test_input_counter:
            self.test_input_counter[category] = 0

        if category in self.test_inputs:
            if isinstance(self.test_inputs[category], list):
                if self.test_input_counter[category] < len(self.test_inputs[category]):
                    value = self.test_inputs[category][self.test_input_counter[category]]
                    self.test_input_counter[category] += 1
                    return value
            elif isinstance(self.test_inputs[category], dict):
                if prompt in self.test_inputs[category]:
                    return self.test_inputs[category][prompt]
                
        return ""

    def get_input(
        self,
        prompt: str,
        required: bool = True,
        validator: Optional[Callable[[str], bool]] = None,
    ) -> str:
        """
        Gets user input with optional validation and rich formatting.

        This method repeatedly prompts the user for input until valid input is provided.

        Args:
            prompt (str): The prompt message to display to the user
            required (bool, optional): Whether the input is required. Defaults to True.
            validator (callable, optional): A function that validates the input. Defaults to None.
                                          Validator should return True if input is valid.

        Returns:
            str: The validated user input value

        Examples:
            # Get required input with no validation
            name = get_input("Enter name")

            # Get optional input
            nickname = get_input("Enter nickname", required=False)

            # Get input with validation
            age = get_input("Enter age", validator=lambda x: x.isdigit())
        """
        if self.test_mode:
            value = self.get_test_input("project_info", prompt)
            self.console.print(f"[cyan]{prompt}[/cyan]: {value}")
            return value
        while True:
            try:
                value = Prompt.ask(f"[cyan]{prompt}[/cyan]").strip()
                if not required and not value:
                    return value
                if not value and required:
                    self.console.print("[red]This field is required. Please provide a value.[/red]")
                    continue
                if validator and not validator(value):
                    continue
                return value
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operation cancelled by user[/yellow]")
                raise

    def get_multiline_input(self, prompt: str) -> List[str]:
        """Modified to handle test mode"""
        if self.test_mode:
            category = ""
            if "requirements" in prompt.lower():
                category = "requirements"
            elif "constraints" in prompt.lower():
                category = "constraints"
            elif "subtasks" in prompt.lower():
                return self.test_inputs["deliverables"][self.test_input_counter.get("deliverables", 0)]["subtasks"]
            
            if category:
                values = self.test_inputs.get(category, [])
                self.console.print(f"\n[cyan]{prompt}[/cyan]")
                for value in values:
                    self.console.print(value)
                return values
            return []
        self.console.print(f"\n[cyan]{prompt} (Enter an empty line to finish):[/cyan]")
        lines = []
        while True:
            try:
                line = input().strip()
                if not line:
                    break
                lines.append(line)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Input cancelled[/yellow]")
                break
        return lines

    def display_section_header(self, title: str):
        self.console.print(Panel(f"[bold blue]{title}[/bold blue]", expand=False))

    def collect_project_info(self):
        self.display_section_header("Project Information")
        self.project_info = {
            "name": self.get_input("Project Name"),
            "description": self.get_input("Project Description"),
            "start_date": self.get_input(
                "Start Date (YYYY-MM-DD)", validator=self.validate_date
            ),  # import datetime
            "sponsor": self.get_input("Project Sponsor"),
            "manager": self.get_input("Project Manager"),
            "budget": self.get_input("Budget (optional)", required=False),
        }

    def collect_requirements(self):
        self.display_section_header("Requirements")
        self.requirements = self.get_multiline_input(
            "Enter project requirements (one per line)"
        )

    def collect_constraints(self):
        self.display_section_header("Constraints")
        self.constraints = self.get_multiline_input(
            "Enter project constraints (one per line)"
        )

    def collect_deliverable(self):
        """Modified to handle test mode"""
        if self.test_mode:
            if "deliverables" not in self.test_input_counter:
                self.test_input_counter["deliverables"] = 0
            
            if self.test_input_counter["deliverables"] < len(self.test_inputs["deliverables"]):
                deliverable = self.test_inputs["deliverables"][self.test_input_counter["deliverables"]]
                self.test_input_counter["deliverables"] += 1
                self.console.print(f"\nDeliverable: {deliverable['name']}")
                return deliverable
            return None
        deliverable = {}
        self.console.print("\nEnter deliverable details (or press Enter to finish):")
        name = self.get_input("Deliverable Name", required=False)
        if not name:
            return None

        deliverable["name"] = name
        deliverable["description"] = self.get_input("Description")
        deliverable["duration"] = self.get_input("Estimated Duration (in weeks)")
        deliverable["dependencies"] = self.get_input(
            "Dependencies (comma-separated)", required=False
        )

        subtasks = self.get_multiline_input("Enter subtasks (one per line)")
        deliverable["subtasks"] = subtasks

        return deliverable

    def collect_deliverables(self):
        self.display_section_header("Deliverables")
        while True:
            deliverable = self.collect_deliverable()
            if deliverable is None:
                break
            self.deliverables.append(deliverable)

    def collect_risks(self):
        """Modified to handle test mode"""
        if self.test_mode:
            self.risks = self.test_inputs["risks"]
            for risk in self.risks:
                self.console.print(f"\nAdded risk: {risk['description']}")
            return
        self.display_section_header("Risks")
        while True:
            risk = {}
            self.console.print("\nEnter risk details (or press Enter to finish):")
            description = self.get_input("Risk Description", required=False)
            if not description:
                break

            risk["description"] = description
            risk["probability"] = self.get_input(
                "Probability (High/Medium/Low)",
                validator=lambda x: x.lower() in ["high", "medium", "low"],
            )
            risk["impact"] = self.get_input(
                "Impact (High/Medium/Low)",
                validator=lambda x: x.lower() in ["high", "medium", "low"],
            )
            risk["mitigation"] = self.get_input("Mitigation Strategy")

            self.risks.append(risk)

    def collect_resources(self):
        """Modified to handle test mode"""
        if self.test_mode:
            self.resources = self.test_inputs["resources"]
            for resource in self.resources:
                self.console.print(f"\nAdded resource: {resource['role']}")
            return
        self.display_section_header("Resources")
        while True:
            resource = {}
            self.console.print("\nEnter resource details (or press Enter to finish):")
            role = self.get_input("Role", required=False)
            if not role:
                break

            resource["role"] = role
            resource["quantity"] = self.get_input("Quantity")
            resource["skills"] = self.get_input("Required Skills")

            self.resources.append(resource)

    def generate_wbs_table(self) -> str:
        """Generate WBS in tabular format with timelines and assignments"""
        if not self.openai_client:
            return self.generate_basic_wbs_table()

        try:
            prompt = f"""As a project management expert, create a detailed Work Breakdown Structure in tabular format based on the following project information:

Project Name: {self.project_info['name']}
Start Date: {self.project_info['start_date']}
Description: {self.project_info['description']}

Requirements:
{chr(10).join(f"- {req}" for req in self.requirements)}

Constraints:
{chr(10).join(f"- {const}" for const in self.constraints)}

Existing Deliverables:
{chr(10).join(f"- {d['name']}: {d['description']}" for d in self.deliverables)}

Please create a comprehensive WBS table that includes:
1. Task ID (hierarchical)
2. Task Name
3. Description
4. Duration (in days)
5. Start Date
6. End Date
7. Dependencies
8. Assignee Role
9. Milestone (Yes/No)
10. Critical Path (Yes/No)

Additional requirements:
- Break down high-level requirements into detailed tasks
- Include project management tasks
- Identify major milestones
- Mark critical path items
- Consider given constraints
- Include buffer time for risks
- Provide realistic timeline estimations
- Show dependencies between tasks

Format the response as a markdown table with the specified columns.
After the table, provide a summary including:
1. Total project duration
2. Key milestones with dates
3. Critical path sequence
4. Resource allocation summary
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a project management expert specialized in creating detailed WBS and project timelines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )

            return response.choices[0].message.content

        except Exception as e:
            self.console.print(f"[red]Error generating WBS table: {str(e)}[/red]")
            return self.generate_basic_wbs_table()

    def generate_basic_wbs_table(self) -> str:
        """Generate basic WBS table without AI assistance"""
        table_header = """
| Task ID | Task Name | Description | Duration (days) | Start Date | End Date | Dependencies | Assignee | Milestone | Critical Path |
|---------|-----------|-------------|----------------|------------|----------|--------------|----------|-----------|---------------|
"""
        table_rows = []
        
        start_date = datetime.datetime.strptime(self.project_info['start_date'], "%Y-%m-%d")
        current_date = start_date
        
        # Add project initialization tasks
        table_rows.append("| 1.0 | Project Initialization | Project setup and planning | 5 | " +
                         f"{current_date.strftime('%Y-%m-%d')} | {(current_date + datetime.timedelta(days=5)).strftime('%Y-%m-%d')} | " +
                         "- | Project Manager | Yes | Yes |")
        
        # Add deliverables as tasks
        for i, deliverable in enumerate(self.deliverables, 2):
            duration = int(deliverable['duration']) * 5  # Convert weeks to days
            end_date = current_date + datetime.timedelta(days=duration)
            
            table_rows.append(
                f"| {i}.0 | {deliverable['name']} | {deliverable['description']} | {duration} | " +
                f"{current_date.strftime('%Y-%m-%d')} | {end_date.strftime('%Y-%m-%d')} | " +
                f"{deliverable['dependencies']} | TBD | No | Yes |"
            )
            
            # Add subtasks
            for j, subtask in enumerate(deliverable['subtasks'], 1):
                subtask_duration = duration // len(deliverable['subtasks'])
                subtask_end = current_date + datetime.timedelta(days=subtask_duration)
                table_rows.append(
                    f"| {i}.{j} | {subtask} | Subtask of {deliverable['name']} | {subtask_duration} | " +
                    f"{current_date.strftime('%Y-%m-%d')} | {subtask_end.strftime('%Y-%m-%d')} | " +
                    f"{i}.0 | TBD | No | No |"
                )
                current_date = subtask_end
            
            current_date = end_date

        return table_header + "\n".join(table_rows)

    def generate_wbs_markdown(self) -> str:
        """Generate complete WBS document with tables and analysis"""
        md_parts = []
        
        # Project header
        md_parts.append(f"# Work Breakdown Structure: {self.project_info['name']}\n")
        
        # Project Information
        md_parts.append("## Project Information\n")
        for key, value in self.project_info.items():
            md_parts.append(f"- **{key.replace('_', ' ').title()}:** {value}\n")
        
        # Requirements and Constraints
        md_parts.append("\n## Requirements and Constraints\n")
        md_parts.append("\n### Requirements\n")
        for req in self.requirements:
            md_parts.append(f"- {req}\n")
        
        md_parts.append("\n### Constraints\n")
        for const in self.constraints:
            md_parts.append(f"- {const}\n")
        
        # Detailed WBS Table
        md_parts.append("\n## Work Breakdown Structure\n")
        md_parts.append(self.generate_wbs_table())
        
        # Risks section remains unchanged
        md_parts.append("\n## Risks\n")
        for i, risk in enumerate(self.risks, 1):
            md_parts.append(f"### Risk {i}\n")
            md_parts.append(f"- **Description:** {risk['description']}\n")
            md_parts.append(f"- **Probability:** {risk['probability']}\n")
            md_parts.append(f"- **Impact:** {risk['impact']}\n")
            md_parts.append(f"- **Mitigation:** {risk['mitigation']}\n\n")
        
        # Resources section remains unchanged
        md_parts.append("## Resources\n")
        for resource in self.resources:
            md_parts.append(f"### {resource['role']}\n")
            md_parts.append(f"- **Quantity:** {resource['quantity']}\n")
            md_parts.append(f"- **Required Skills:** {resource['skills']}\n\n")
        
        return "".join(md_parts)

    def validate_date(self, date_string: str) -> bool:
        """Validate date string format YYYY-MM-DD"""
        try:
            datetime.datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
            return False

    def save_to_file(self, content: str, filename: str):
        with open(filename, "w") as f:
            f.write(content)
        print(f"\nWBS document has been saved to {filename}")

    def show_test_progress(self, message: str):
        """Simple progress indication for test mode"""
        if self.test_mode:
            self.console.print(f"[dim]> {message}[/dim]")

    def collect_project_data(self):
        """Collect basic project data with progress bar"""
        self.display_section_header("Collecting Project Data")
        
        if self.test_mode:
            # Fast path for test mode without progress bar
            self.collect_project_info()
            self.show_test_progress("Collecting requirements")
            self.collect_requirements()
            self.show_test_progress("Collecting constraints")
            self.collect_constraints()
            self.console.print("[green]Project data collection completed.[/green]")
            return

        # Regular collection with progress bar for interactive mode
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
            refresh_per_second=1
        ) as progress:
            task = progress.add_task("Collecting Project Data", total=3)
            
            # Clear the progress temporarily for input
            progress.stop()
            self.collect_project_info()
            progress.start()
            progress.update(task, advance=1, description="Collecting Requirements")
            
            progress.stop()
            self.collect_requirements()
            progress.start()
            progress.update(task, advance=1, description="Collecting Constraints")
            
            progress.stop()
            self.collect_constraints()
            progress.start()
            progress.update(task, advance=1)
            
        self.console.print("[green]Project data collection completed.[/green]")

    def collect_project_details(self):
        """Collect detailed project information with progress bar"""
        self.display_section_header("Collecting Project Details")
        
        if self.test_mode:
            # Fast path for test mode without progress bar
            self.show_test_progress("Collecting deliverables")
            self.collect_deliverables()
            self.show_test_progress("Collecting risks")
            self.collect_risks()
            self.show_test_progress("Collecting resources")
            self.collect_resources()
            self.console.print("[green]Project details collection completed.[/green]")
            return

        # Regular collection with progress bar for interactive mode
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
            refresh_per_second=1
        ) as progress:
            task = progress.add_task("Collecting Project Details", total=3)
            
            # Clear the progress temporarily for input
            progress.stop()
            self.collect_deliverables()
            progress.start()
            progress.update(task, advance=1, description="Collecting Risks")
            
            progress.stop()
            self.collect_risks()
            progress.start()
            progress.update(task, advance=1, description="Collecting Resources")
            
            progress.stop()
            self.collect_resources()
            progress.start()
            progress.update(task, advance=1)
            
        self.console.print("[green]Project details collection completed.[/green]")

    def display_summary(self):
        table = Table(title="Project Summary", show_header=True, header_style="bold_magenta")
        table.add_column("Category", style="cyan")
        table.add_column("Count", justify="right", style="green")
        
        table.add_row("Requirements", str(len(self.requirements)))
        table.add_row("Constraints", str(len(self.constraints)))
        table.add_row("Deliverables", str(len(self.deliverables)))
        table.add_row("Risks", str(len(self.risks)))
        table.add_row("Resources", str(len(self.resources)))
        
        self.console.print(table)

    def enrich_wbs_with_ai(self, wbs_content: str) -> str:
        """Enhanced WBS analysis using OpenAI"""
        if not self.openai_client:
            return wbs_content

        try:
            prompt = f"""Analyze this WBS document and provide enhanced insights:

{wbs_content}

Please provide:
1. Critical Path Analysis
   - List all critical path tasks
   - Identify potential bottlenecks
   - Suggest optimization strategies

2. Resource Optimization
   - Analyze resource allocation
   - Identify potential resource conflicts
   - Suggest resource leveling strategies

3. Timeline Analysis
   - Evaluate timeline feasibility
   - Identify schedule risks
   - Suggest buffer allocation

4. Risk Assessment
   - Additional risks based on WBS
   - Impact on critical path
   - Additional mitigation strategies

5. Delivery Optimization
   - Parallel execution opportunities
   - Dependencies optimization
   - Milestone achievement strategies

Format the response in Markdown with clear sections and tables where appropriate."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a project management expert specializing in WBS analysis and optimization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )

            analysis = response.choices[0].message.content
            return f"{wbs_content}\n\n## AI-Enhanced Project Analysis\n\n{analysis}"

        except Exception as e:
            self.console.print(f"[red]Error during AI analysis: {str(e)}[/red]")
            return wbs_content

    def run(self):
        """Main execution method"""
        self.console.print("\n[bold cyan]Welcome to WBS Generator![/bold cyan]")
        self.console.print("\nThis tool will help you create a Work Breakdown Structure for your project.")
        
        if Confirm.ask("\nReady to start collecting project data?"):
            try:
                # Collect all project data
                self.collect_project_data()
                self.collect_project_details()
                
                # Generate and save WBS
                wbs_content = self.generate_wbs_markdown()
                
                if Confirm.ask("\nWould you like to save the WBS to a file?"):
                    filename = f"wbs_{self.project_info['name'].lower().replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.md"
                    self.save_to_file(wbs_content, filename)
                    
                if Confirm.ask("\nWould you like to preview the WBS?"):
                    self.console.print(Markdown(wbs_content))

                if self.openai_client and Confirm.ask("\nWould you like to enrich the WBS with AI analysis?"):
                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                        task = progress.add_task("Enriching WBS with AI analysis...")
                        wbs_content = self.enrich_wbs_with_ai(wbs_content)
                        progress.update(task, completed=True)
                    
                    if Confirm.ask("\nWould you like to save the enriched WBS?"):
                        filename = f"wbs_{self.project_info['name'].lower().replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}_enriched.md"
                        self.save_to_file(wbs_content, filename)
                    
                    if Confirm.ask("\nWould you like to preview the enriched WBS?"):
                        self.console.print(Markdown(wbs_content))
                    
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Process cancelled by user.[/yellow]")
                return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Work Breakdown Structure')
    parser.add_argument('--test', action='store_true', help='Run in test mode with pre-populated data')
    args = parser.parse_args()
    
    generator = WBSGenerator(test_mode=args.test)
    generator.run()
