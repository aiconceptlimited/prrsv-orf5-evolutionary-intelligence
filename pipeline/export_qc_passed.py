"""
export_qc_passed.py
-------------------
Exports QC-passed ORF5 sequences from MySQL database
to FASTA (for alignment) and CSV (for metadata tracking).
"""

import mysql.connector
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
import csv
import os

# --- Database config ---
config = {
    'host': 'localhost',
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': 'prrsv_genomics'
}

# --- Output directories ---
output_dir = os.path.join(os.path.dirname(__file__), "../data/qc")
os.makedirs(output_dir, exist_ok=True)

# --- Connect & fetch QC-passed sequences ---
conn = mysql.connector.connect(**config)
cursor = conn.cursor(dictionary=True)
cursor.execute("""
    SELECT accession, sequence, quality_score
    FROM qc_sequences
    WHERE passed_qc = 1
""")
records = cursor.fetchall()
cursor.close()
conn.close()

if not records:
    print("⚠️  No QC-passed sequences found.")
    exit()

# --- Write FASTA ---
fasta_path = os.path.join(output_dir, "qc_passed_orf5.fasta")
records_fasta = [
    SeqRecord(Seq(r["sequence"]),
              id=r["accession"],
              description=f"quality={r['quality_score']:.3f}")
    for r in records
]
SeqIO.write(records_fasta, fasta_path, "fasta")

# --- Write CSV summary ---
csv_path = os.path.join(output_dir, "qc_summary.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["accession", "quality_score", "sequence_length"])
    for r in records:
        writer.writerow([r["accession"], r["quality_score"], len(r["sequence"])])

print(f"✅ Exported {len(records)} QC-passed sequences:")
print(f"   - FASTA: {fasta_path}")
print(f"   - CSV:   {csv_path}")

