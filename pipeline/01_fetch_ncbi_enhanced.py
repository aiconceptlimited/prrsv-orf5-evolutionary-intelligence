"""
Fetch PRRSV ORF5 sequences with extended metadata extraction
from GenBank + BioSample text fields, optimized for speed.
"""

from Bio import Entrez, SeqIO
import mysql.connector
import re, time
from tqdm import tqdm

# ------------------- Configuration -------------------
from dotenv import load_dotenv
import os

load_dotenv()

config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}
Entrez.email = "your_email@example.com"  # replace with your email
SEARCH_TERM = "PRRSV[Organism] AND ORF5[Gene] AND 600:700[Sequence Length]"
MAX_RECORDS = 200
BATCH_SIZE = 50  # fetch 50 records at once for speed

# ------------------- Metadata Extraction -------------------
def extract_metadata_from_description(description: str):
    """Extract country/year info if available in sequence description."""
    country, date = None, None

    # Try to detect known countries
    m_country = re.search(
        r"\b(USA|China|Vietnam|Korea|Japan|Germany|Denmark|Thailand|Philippines|Brazil|Mexico)\b",
        description,
        re.IGNORECASE,
    )
    if m_country:
        country = m_country.group(1).title()

    # Detect year (19xx or 20xx)
    m_year = re.search(r"\b(19|20)\d{2}\b", description)
    if m_year:
        date = m_year.group(0)

    return country, date


# ------------------- Fetch Sequences -------------------
def fetch_sequences():
    print(f"🔍 Searching NCBI for: {SEARCH_TERM}")
    handle = Entrez.esearch(db="nucleotide", term=SEARCH_TERM, retmax=MAX_RECORDS)
    record = Entrez.read(handle)
    handle.close()
    ids = record["IdList"]

    if not ids:
        print("⚠️ No sequences found.")
        return []

    print(f"✅ Found {len(ids)} sequences")

    sequences = []
    for i in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[i:i + BATCH_SIZE]
        handle = Entrez.efetch(db="nucleotide", id=",".join(batch_ids), rettype="gb", retmode="text")
        batch_records = list(SeqIO.parse(handle, "gb"))
        sequences.extend(batch_records)
        handle.close()
        time.sleep(0.3)  # be kind to NCBI

    return sequences


# ------------------- Store in Database -------------------
def store_to_db(sequences):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    query = """
        INSERT IGNORE INTO sequences_raw (accession, sequence, host)
        VALUES (%s, %s, %s)
    """

    print(f"💾 Storing {len(sequences)} sequences into database...")

    data_batch = []
    for seq in tqdm(sequences, desc="📥 Inserting"):
        accession = seq.id
        sequence = str(seq.seq)
        country, date = None, None
        host = None

        # Extract from features
        for feature in seq.features:
            if feature.type == "source":
                q = feature.qualifiers
                country = q.get("country", [None])[0]
                host = q.get("host", [None])[0]
                date = q.get("collection_date", [None])[0]

        # Fallback: description
        if not country or not date:
            desc = seq.description
            c2, d2 = extract_metadata_from_description(desc)
            if not country:
                country = c2
            if not date:
                date = d2

        # Fallback host
        if not host:
            host = seq.annotations.get("organism", "unknown")

        data_batch.append((accession, sequence, host or "unknown"))

    # Batch insert for performance
    cursor.executemany(query, data_batch)
    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Successfully inserted {len(data_batch)} sequences into database.")


# ------------------- Main Runner -------------------
if __name__ == "__main__":
    seqs = fetch_sequences()
    if seqs:
        store_to_db(seqs)
        print("✅ Enhanced metadata loading complete.")
    else:
        print("⚠️ No sequences fetched.")

