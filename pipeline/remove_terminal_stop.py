from Bio import SeqIO
from Bio.Seq import Seq

records = []

for rec in SeqIO.parse(
    "data/qc/qc_passed_orf5.fasta",
    "fasta"
):

    seq = str(rec.seq)

    if seq[-3:].upper() in ["TAA", "TAG", "TGA"]:
        seq = seq[:-3]

    rec.seq = Seq(seq)
    records.append(rec)

SeqIO.write(
    records,
    "data/qc/qc_passed_orf5_nostop.fasta",
    "fasta"
)

print(f"Saved {len(records)} sequences")
