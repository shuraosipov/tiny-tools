def parse_protein_sequence(sequence: str) -> list:
    from Bio.Seq import Seq
    from Bio.SeqUtils import seq3

    protein_seq = Seq(sequence)
    return {
        "length": len(protein_seq),
        "sequence": str(protein_seq),
        "three_letter_code": seq3(protein_seq)
    }

def calculate_molecular_weight(sequence: str) -> float:
    from Bio.SeqUtils import molecular_weight

    return molecular_weight(sequence)

def analyze_protein_structure(structure_file: str) -> dict:
    from Bio.PDB import PDBParser, PPBuilder

    parser = PDBParser()
    structure = parser.get_structure('protein_structure', structure_file)
    ppb = PPBuilder()
    peptides = ppb.build_peptides(structure)

    return {
        "num_peptides": len(peptides),
        "peptide_lengths": [len(peptide) for peptide in peptides]
    }