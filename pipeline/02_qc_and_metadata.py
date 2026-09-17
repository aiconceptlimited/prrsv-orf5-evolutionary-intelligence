from Bio import SeqIO
from Bio.Seq import Seq
import mysql.connector
from tqdm import tqdm
import numpy as np
import pandas as pd

from dotenv import load_dotenv
import os

load_dotenv()

config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def calculate_gc_content(seq):
    seq = seq.upper()
    return ((seq.count("G") + seq.count("C")) / len(seq)) * 100 if len(seq) else 0

def calculate_ambiguous_percent(seq):
    seq = seq.upper()
    return (seq.count("N") / len(seq)) * 100 if len(seq) else 0

def check_length(seq):
    return 600 <= len(seq) <= 700

def check_frameshift(seq):
    return len(seq) % 3 != 0

def check_stop_codon(seq):
    try:
        trim_len = (len(seq) // 3) * 3
        seq = seq[:trim_len]

        aa = str(Seq(seq).translate())

        return "*" in aa[:-1]

    except Exception:
        return True

def run_qc():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    cursor.execute("SELECT accession, sequence FROM sequences_raw")
    rows = cursor.fetchall()

    conn.close()

    if not rows:
        print("⚠️ No sequences found for QC.")
        return

    print(f"🔍 Evaluating {len(rows)} sequences...")

    df = pd.DataFrame(rows, columns=["accession", "sequence"])

    df["seq_length"] = df["sequence"].str.len()

    df["gc_content"] = df["sequence"].apply(calculate_gc_content)

    df["ambiguous_count"] = (
        df["sequence"]
        .str.upper()
        .str.count("N")
    )

    df["ambiguous_percent"] = (
        df["ambiguous_count"] / df["seq_length"]
    ) * 100

    df["quality_score"] = (
        1 - (df["ambiguous_count"] / df["seq_length"])
    )

    df["length_valid"] = (
        df["sequence"].apply(check_length)
    )

    df["frameshift"] = (
        df["sequence"].apply(check_frameshift)
    )

    df["stop_codon"] = (
        df["sequence"].apply(check_stop_codon)
    )

    df["passed_qc"] = (
        (df["length_valid"])
        &
        (~df["frameshift"])
        &
        (~df["stop_codon"])
        &
        (df["quality_score"] > 0.90)
    )

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    passed = df[df["passed_qc"]]

    data = list(zip(
        passed["accession"],
        passed["sequence"],
        passed["quality_score"],
        passed["passed_qc"],
        passed["seq_length"],
        passed["gc_content"],
        passed["ambiguous_count"],
        passed["ambiguous_percent"],
        passed["length_valid"],
        passed["frameshift"],
        passed["stop_codon"]
    ))

    cursor.executemany(
        """
        REPLACE INTO qc_sequences
        (
            accession,
            sequence,
            quality_score,
            passed_qc,
            seq_length,
            gc_content,
            ambiguous_count,
            ambiguous_percent,
            length_valid,
            frameshift,
            stop_codon
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        data
    )

    conn.commit()
    conn.close()

    print(f"✅ QC complete. Passed: {len(passed)}/{len(df)} sequences.")

if __name__ == "__main__":
    run_qc()
