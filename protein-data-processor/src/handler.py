def main(event, context):
    # Extract protein data from the incoming event
    protein_data = event.get('body', {}).get('protein_data', '')

    if not protein_data:
        return {
            'statusCode': 400,
            'body': 'No protein data provided.'
        }

    # Import utility functions
    from utils.bio_utils import parse_protein_sequence, calculate_molecular_weight, analyze_protein_structure

    # Process the protein data
    try:
        sequence = parse_protein_sequence(protein_data)
        molecular_weight = calculate_molecular_weight(sequence)
        structure_analysis = analyze_protein_structure(sequence)

        return {
            'statusCode': 200,
            'body': {
                'molecular_weight': molecular_weight,
                'structure_analysis': structure_analysis
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error processing protein data: {str(e)}'
        }