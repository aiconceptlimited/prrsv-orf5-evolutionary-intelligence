from Bio import SeqIO
from Bio.Seq import Seq
import os

input_file = "data/alignments/orf5_aligned.fasta"
output_file = "data/alignments/orf5_codon_aligned.fasta"

records = list(SeqIO.parse(input_file, "fasta"))
print(f"✅ Loaded {len(records)} aligned sequences.")

aligned = []
for rec in records:
    seq = str(rec.seq).replace("-", "")
    codon_aligned = "".join(seq[i:i+3] for i in range(0, len(seq), 3))
    rec.seq = Seq(codon_aligned)
    aligned.append(rec)

SeqIO.write(aligned, output_file, "fasta")
print(f"✅ Codon alignment complete. Saved to: {output_file}")

