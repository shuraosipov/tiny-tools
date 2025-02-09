import boto3
from typing import Dict, List
from fpdf import FPDF

class AWSWellArchitectedToolIntegration:
    def __init__(self):
        self.wat_client = boto3.client('wellarchitected')
        
    def list_workloads(self) -> List[Dict]:
        """List all workloads in AWS Well-Architected Tool."""
        workloads = []
        paginator = self.wat_client.get_paginator('list_workloads')
        for page in paginator.paginate():
            workloads.extend(page['WorkloadSummaries'])
        return workloads
    
    def get_lens_review(self, workload_id: str, lens_alias: str = 'wellarchitected') -> Dict:
        """Get a specific lens review for a workload."""
        response = self.wat_client.get_lens_review(
            WorkloadId=workload_id,
            LensAlias=lens_alias
        )
        return response
    
    def get_answers(self, workload_id: str, lens_alias: str = 'wellarchitected') -> List[Dict]:
        """Get all answers for a specific lens review."""
        answers = []
        paginator = self.wat_client.get_paginator('list_answers')
        for page in paginator.paginate(
            WorkloadId=workload_id,
            LensAlias=lens_alias
        ):
            answers.extend(page['AnswerSummaries'])
        return answers
    
    def generate_pdf_report(self, workload_id: str, assessment_data: Dict) -> str:
        """Generate a PDF report combining WAT data and assessment results."""
        pdf = FPDF()
        pdf.add_page()
        
        # Set up fonts
        pdf.set_font('Arial', 'B', 16)
        
        # Title
        pdf.cell(0, 10, 'DevOps Maturity Assessment Report', ln=True, align='C')
        pdf.set_font('Arial', '', 12)
        
        # AWS WAT Information
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'AWS Well-Architected Tool Results', ln=True)
        pdf.set_font('Arial', '', 12)
        
        # Get WAT data
        lens_review = self.get_lens_review(workload_id)
        answers = self.get_answers(workload_id)
        
        # Add WAT summary
        pdf.cell(0, 10, f"Workload ID: {workload_id}", ln=True)
        pdf.cell(0, 10, f"Risk Counts:", ln=True)
        for risk_count in lens_review.get('RiskCounts', []):
            pdf.cell(0, 10, f"- {risk_count['Risk']}: {risk_count['Count']}", ln=True)
            
        # Add assessment results
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Assessment Results', ln=True)
        pdf.set_font('Arial', '', 12)
        
        stats = assessment_data['statistics']
        overall = stats['overall']
        pdf.cell(0, 10, f"Overall Progress: {overall['implemented']}/{overall['total']} "
                f"({(overall['implemented']/overall['total']*100):.1f}%)", ln=True)
        
        # Save the PDF
        timestamp = assessment_data['timestamp'].replace(':', '').replace('-', '')[:14]
        filename = f'devops_assessment_{timestamp}.pdf'
        pdf.output(filename)
        return filename