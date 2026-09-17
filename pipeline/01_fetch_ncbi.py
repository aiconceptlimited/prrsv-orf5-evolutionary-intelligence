import os
"""
01_fetch_ncbi.py
----------------
Fetches PRRSV ORF5 nucleotide sequences from NCBI GenBank
and stores them into the MySQL database (sequences_raw table).
"""

from Bio import Entrez, SeqIO
import mysql.connector
from tqdm import tqdm
import time

# --- Database Config ---
config = {
    'host': 'localhost',
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': 'prrsv_genomics'
}

# --- Set your NCBI Email ---
Entrez.email = "your_email@example.com"  # required by NCBI to use Entrez

# --- Define search term ---
SEARCH_TERM = "PRRSV[Organism] AND ORF5[Gene]"
MAX_RECORDS = 100  # you can increase this later (e.g. 500, 1000)

def fetch_prrsv_orf5_sequences():
    """Fetches PRRSV ORF5 sequences from NCBI."""
    print(f"🔍 Searching NCBI for: {SEARCH_TERM}")
    handle = Entrez.esearch(db="nucleotide", term=SEARCH_TERM, retmax=MAX_RECORDS)
    record = Entrez.read(handle)
    handle.close()
    ids = record["IdList"]
    print(f"✅ Found {len(ids)} sequences")

    if not ids:
        return []

    # Fetch GenBank records in FASTA + metadata
    handle = Entrez.efetch(db="nucleotide", id=ids, rettype="gb", retmode="text")
    sequences = list(SeqIO.parse(handle, "gb"))
    handle.close()

    print(f"📦 Retrieved {len(sequences)} GenBank entries")
    return sequences

def store_sequences_to_db(sequences):
    """Inserts fetched sequences into MySQL with better metadata extraction."""
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    insert_query = """
        INSERT IGNORE INTO sequences_raw (accession, sequence, collection_date, location, host)
        VALUES (%s, %s, %s, %s, %s)
    """

    for seq in tqdm(sequences, desc="💾 Storing sequences"):
        accession = seq.id
        sequence = str(seq.seq)
        date = None
        country = None
        host = None

        # --- Extract from source features (if present) ---
        for feature in seq.features:
            if feature.type == "source":
                qualifiers = feature.qualifiers
                country = qualifiers.get("country", [None])[0]
                host = qualifiers.get("host", [None])[0]
                date = qualifiers.get("collection_date", [None])[0]

        # --- Try fallback from annotations if still missing ---
        if not date:
            date = seq.annotations.get("date", None)
        if not host:
            host = seq.annotations.get("organism", None)

        # --- Fallback defaults ---
        if not country:
            country = "unknown"
        if not host:
            host = "unknown"
        if not date or date == "0000-00-00":
            date = None  # store as NULL for now

        cursor.execute(insert_query, (accession, sequence, date, country, host))
        conn.commit()
        time.sleep(0.2)  # be gentle with NCBI

    cursor.close()
    conn.close()
    print("✅ All sequences stored with improved metadata extraction.")
if __name__ == "__main__":
    sequences = fetch_prrsv_orf5_sequences()
    if sequences:
        store_sequences_to_db(sequences)
    else:
        print("⚠️ No sequences found.")

