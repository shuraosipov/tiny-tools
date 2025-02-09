import json
import os
import boto3
from Bio.PDB.Polypeptide import three_to_one

def create_sample_data():
    """Create synthetic protein data for testing"""
    return {
        "protein_sequences": [
            {"id": "1abc", "three_letter": "ALA-GLY-SER"},
            {"id": "2xyz", "three_letter": "VAL-PRO-THR"},
            {"id": "3def", "three_letter": "LEU-ILE-PHE"}
        ]
    }

def process_sequence(three_letter_seq):
    """Convert three letter amino acid sequence to one letter code"""
    # Split the sequence on hyphens and convert each amino acid
    three_letter_codes = three_letter_seq.split('-')
    one_letter_codes = [three_to_one(code) for code in three_letter_codes]
    return ''.join(one_letter_codes)

def lambda_handler(event, context):
    # Get DynamoDB table name from environment variable
    table_name = os.environ['DYNAMODB_TABLE']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # For demo purposes, we'll use synthetic data instead of reading from S3
    data = create_sample_data()
    
    # Process each protein sequence
    for protein in data['protein_sequences']:
        protein_id = protein['id']
        three_letter_seq = protein['three_letter']
        one_letter_seq = process_sequence(three_letter_seq)
        
        # Store both representations in DynamoDB
        table.put_item(
            Item={
                'protein_id': protein_id,
                'sequence_type': 'three_letter',
                'sequence': three_letter_seq
            }
        )
        
        table.put_item(
            Item={
                'protein_id': protein_id,
                'sequence_type': 'one_letter',
                'sequence': one_letter_seq
            }
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully processed protein sequences')
    }