import subprocess, os
from Bio import SeqIO

input_file = "data/qc/qc_passed_orf5.fasta"
output_file = "data/alignments/orf5_aligned.fasta"

os.makedirs("data/alignments", exist_ok=True)

records = list(SeqIO.parse(input_file, "fasta"))
print(f"✅ Loaded {len(records)} QC-passed sequences.")

print("🚀 Running alignment with MAFFT (multi-threaded)...")
cmd = ["mafft", "--thread", "4", "--auto", input_file]
with open(output_file, "w") as f:
    subprocess.run(cmd, stdout=f, check=True)

print(f"✅ Alignment complete! Saved to: {output_file}")

