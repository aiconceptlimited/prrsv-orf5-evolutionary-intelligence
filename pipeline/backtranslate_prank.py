from Bio import SeqIO
from Bio.Seq import Seq

# --------------------------------------------------
# Load original nucleotide sequences
# --------------------------------------------------

dna_records = {}

for rec in SeqIO.parse(
    "data/qc/qc_passed_orf5_nostop.fasta",
    "fasta"
):
    dna_records[rec.id] = str(rec.seq)

print(f"Loaded {len(dna_records)} DNA sequences")

# --------------------------------------------------
# Back-translate PRANK protein alignment
# --------------------------------------------------

output = []
missing = 0

for prot_rec in SeqIO.parse(
    "data/alignments/orf5_prank_nostop.best.fas",
    "fasta"
):

    # Example:
    # PV462161.1_1_quality=1.000
    # ->
    # PV462161.1

    pid = prot_rec.id.split("_1_quality=")[0]

    if pid not in dna_records:
        print(f"Missing DNA sequence for: {pid}")
        missing += 1
        continue

    dna = dna_records[pid]
    prot = str(prot_rec.seq)

    # Remove gaps from original DNA
    dna = dna.replace("-", "")

    # Split DNA into codons
    codons = [
        dna[i:i+3]
        for i in range(0, len(dna), 3)
    ]

    codon_pos = 0
    codon_alignment = []

    for aa in prot:

        if aa == "-":
            codon_alignment.append("---")

        else:

            if codon_pos >= len(codons):
                print(
                    f"WARNING: ran out of codons for {pid}"
                )
                break

            codon_alignment.append(
                codons[codon_pos]
            )

            codon_pos += 1

    codon_seq = "".join(codon_alignment)

    prot_rec.id = pid
    prot_rec.name = pid
    prot_rec.description = ""

    prot_rec.seq = Seq(codon_seq)

    output.append(prot_rec)

# --------------------------------------------------
# Save codon alignment
# --------------------------------------------------

outfile = "data/alignments/orf5_codon_prank_nostop.fasta"

SeqIO.write(
    output,
    outfile,
    "fasta"
)

print()
print(f"Saved {len(output)} codon-aligned sequences")
print(f"Missing IDs: {missing}")
print(f"Output: {outfile}")
