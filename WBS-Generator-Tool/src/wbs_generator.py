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

    def __init__(self):
        self.project_info = {}
        self.requirements = []
        self.constraints = []
        self.deliverables = []
        self.risks = []
        self.resources = []
        self.progress_bar = None
        self.console = Console()

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

    def generate_wbs_markdown(self) -> str:
        md_parts = []
        md_parts.append(f"# Work Breakdown Structure: {self.project_info['name']}\n\n")

        # Project Information
        md_parts.append("## Project Information\n\n")
        for key, value in self.project_info.items():
            md_parts.append(f"- **{key.replace('_', ' ').title()}:** {value}\n")

        # Requirements
        md_parts.append("\n## Requirements\n\n")
        for i, req in enumerate(self.requirements, 1):
            md_parts.append(f"{i}. {req}\n")

        # Constraints
        md_parts.append("\n## Constraints\n\n")
        for i, constraint in enumerate(self.constraints, 1):
            md_parts.append(f"{i}. {constraint}\n")

        # Deliverables
        md_parts.append("\n## Deliverables\n\n")
        for i, deliverable in enumerate(self.deliverables, 1):
            md_parts.append(f"### {i}. {deliverable['name']}\n")
            md_parts.append(f"- **Description:** {deliverable['description']}\n")
            md_parts.append(f"- **Duration:** {deliverable['duration']} weeks\n")
            if deliverable["dependencies"]:
                md_parts.append(f"- **Dependencies:** {deliverable['dependencies']}\n")

            md_parts.append("\n#### Subtasks:\n")
            for j, subtask in enumerate(deliverable["subtasks"], 1):
                md_parts.append(f"{i}.{j}. {subtask}\n")
            md_parts.append("\n")

        # Risks
        md_parts.append("## Risks\n\n")
        for i, risk in enumerate(self.risks, 1):
            md_parts.append(f"### Risk {i}\n")
            md_parts.append(f"- **Description:** {risk['description']}\n")
            md_parts.append(f"- **Probability:** {risk['probability']}\n")
            md_parts.append(f"- **Impact:** {risk['impact']}\n")
            md_parts.append(f"- **Mitigation:** {risk['mitigation']}\n\n")

        # Resources
        md_parts.append("## Resources\n\n")
        for i, resource in enumerate(self.resources, 1):
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

    def collect_project_data(self):
        """Collect basic project data with progress bar"""
        self.display_section_header("Collecting Project Data")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Collecting Project Data", total=3)
            
            self.collect_project_info()
            progress.update(task, advance=1, description="Collecting Requirements")
            
            self.collect_requirements()
            progress.update(task, advance=1, description="Collecting Constraints")
            
            self.collect_constraints()
            progress.update(task, advance=1)
            
        self.console.print("[green]Project data collection completed.[/green]")

    def collect_project_details(self):
        """Collect detailed project information with progress bar"""
        self.display_section_header("Collecting Project Details")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Collecting Project Details", total=3)
            
            self.collect_deliverables()
            progress.update(task, advance=1, description="Collecting Risks")
            
            self.collect_risks()
            progress.update(task, advance=1, description="Collecting Resources")
            
            self.collect_resources()
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
                    
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Process cancelled by user.[/yellow]")
                return

if __name__ == "__main__":
    generator = WBSGenerator()
    generator.run()
