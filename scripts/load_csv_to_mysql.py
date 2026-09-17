import os
import numpy as np

def clean_value(v):
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v

import pandas as pd
import mysql.connector

config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "prrsv_genomics")
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor()

def load_csv(path, table, columns, mapping=None):
    df = pd.read_csv(path)

    # normalize columns safely
    df.columns = [c.strip() for c in df.columns]

    if mapping:
        df = df.rename(columns=mapping)

    # ensure required columns exist
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise Exception(f"Missing columns {missing} in {path}. Found: {list(df.columns)}")

    df = df.fillna(0)

    placeholders = ",".join(["%s"] * len(columns))
    cols = ",".join(columns)

    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

    for _, row in df.iterrows():
        cursor.execute(sql, tuple(clean_value(row[c]) for c in columns))

    conn.commit()
    print(f"Loaded {len(df)} rows into {table}")

# ---------------- FIXED LOADERS ----------------

load_csv(
    "data/eii/features/conservation_entropy.csv",
    "conservation_entropy",
    ["site", "conservation", "entropy"],
    mapping={
        "Site": "site",
        "Conservation": "conservation",
        "Entropy": "entropy"
    }
)

load_csv(
    "data/eii/features/glyco_sites.csv",
    "glyco_sites",
    ["site", "glyco_frequency"],
    mapping={
        "Site": "site",
        "GlycoFrequency": "glyco_frequency"
    }
)

load_csv(
    "data/eii/selection/selection_overlap.csv",
    "selection_overlap",
    ["site", "fel", "meme", "selection_score"],
    mapping={
        "Site": "site",
        "FEL": "fel",
        "MEME": "meme",
        "SelectionScore": "selection_score"
    }
)

load_csv(
    "data/eii/final/eii_site_scores_v2.csv",
    "site_eii",
    [
        "site","conservation","entropy","fel","meme",
        "selection_score","variability",
        "selection_norm","entropy_norm",
        "site_eii","glyco_frequency","site_eii_v2"
    ],
    mapping={
        "Site": "site",
        "Conservation": "conservation",
        "Entropy": "entropy",
        "FEL": "fel",
        "MEME": "meme",
        "SelectionScore": "selection_score",
        "Variability": "variability",
        "SelectionNorm": "selection_norm",
        "EntropyNorm": "entropy_norm",
        "SiteEII": "site_eii",
        "GlycoFrequency": "glyco_frequency",
        "SiteEII_v2": "site_eii_v2"
    }
)

conn.close()
