import os
import sys
import numpy as np
from Bio import SeqIO
import mysql.connector
from dotenv import load_dotenv
import re
from collections import Counter
from scipy.spatial.distance import pdist

load_dotenv()

config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# ---------- LOAD SEQUENCES ----------
aligned_file = "data/alignments/orf5_codon_aligned.fasta"
records = list(SeqIO.parse(aligned_file, "fasta"))
print(f"✅ Loaded {len(records)} codon-aligned sequences.")

if len(records) == 0:
    raise Exception("No sequences found in alignment file.")

# Convert to numpy array
seqs = [str(r.seq).upper() for r in records]
max_len = max(len(s) for s in seqs)
seqs = [s.ljust(max_len, "-") for s in seqs]
seq_array = np.array([list(s) for s in seqs])
print(f"✅ Shape: {seq_array.shape}")

# ---------- COMPUTE SIGNALS ----------
print("\n📊 Computing Signals:")

# 1. Epitope Drift (Shannon entropy)
entropy_values = []
for col in range(seq_array.shape[1]):
    col_chars = seq_array[:, col]
    col_chars = col_chars[col_chars != '-']
    if len(col_chars) > 0:
        counts = Counter(col_chars)
        probs = [count/len(col_chars) for count in counts.values()]
        entropy = -sum(p * np.log2(p) for p in probs)
        entropy_values.append(entropy)
epitope_drift = np.mean(entropy_values) if entropy_values else 0
print(f"  Epitope Drift: {epitope_drift:.4f}")

# 2. Selection Pressure (codon-level variation)
# Count codon changes per site
selection_values = []
for pos in range(0, len(seqs[0]), 3):
    if pos + 2 < len(seqs[0]):
        codons = []
        for seq in seqs:
            codon = seq[pos:pos+3]
            if '-' not in codon:
                codons.append(codon)
        if len(codons) > 1:
            unique = len(set(codons))
            selection_values.append(unique / len(codons))
selection_pressure = np.mean(selection_values) if selection_values else 0
print(f"  Selection Pressure: {selection_pressure:.4f}")

# 3. Glycosylation Dynamics (N-X-S/T motifs)
glyco_counts = []
for seq in seqs:
    count = len(re.findall(r'N[^P][ST]', seq))
    glyco_counts.append(count)
glycosylation_dynamics = np.mean(glyco_counts) / (max_len / 10) if max_len > 0 else 0
print(f"  Glycosylation Dynamics: {glycosylation_dynamics:.4f}")

# 4. Phylogenetic Instability (pairwise distances)
if len(seqs) > 1:
    # Sample up to 100 sequences for performance
    sample_size = min(100, len(seqs))
    sample_indices = np.random.choice(len(seqs), sample_size, replace=False)
    sample_seqs = [seqs[i] for i in sample_indices]
    
    distances = []
    for i in range(len(sample_seqs)):
        for j in range(i+1, len(sample_seqs)):
            seq1 = sample_seqs[i]
            seq2 = sample_seqs[j]
            # Count differences (excluding gaps)
            diff = sum(1 for a, b in zip(seq1, seq2) if a != b and a != '-' and b != '-')
            total = sum(1 for a, b in zip(seq1, seq2) if a != '-' and b != '-')
            if total > 0:
                distances.append(diff / total)
    phylogenetic_instability = np.mean(distances) if distances else 0
else:
    phylogenetic_instability = 0
print(f"  Phylogenetic Instability: {phylogenetic_instability:.4f}")

# 5. Distance Outliers
if distances:
    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    outliers = sum(1 for d in distances if d > mean_dist + 2*std_dist)
    distance_outliers = outliers / len(distances) if distances else 0
else:
    distance_outliers = 0
print(f"  Distance Outliers: {distance_outliers:.4f}")

# ---------- NORMALIZE & CALCULATE EII ----------
signals_raw = [epitope_drift, selection_pressure, glycosylation_dynamics, phylogenetic_instability, distance_outliers]
print(f"\n📊 Raw Signals: {signals_raw}")

# Normalize to 0-1 range
signals_norm = []
for val in signals_raw:
    if val > 0:
        signals_norm.append(min(val / max(signals_raw), 1.0) if max(signals_raw) > 0 else 0)
    else:
        signals_norm.append(0)

print(f"📊 Normalized Signals: {signals_norm}")

# EII = mean of normalized signals × 100
eii_value = np.mean(signals_norm) * 100
print(f"\n📊 EII = {eii_value:.2f}")

# ---------- STORE IN DATABASE ----------
try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Insert into eii_index
    cursor.execute("""
        INSERT INTO eii_index (eii_value, created_at)
        VALUES (%s, NOW())
    """, (eii_value,))
    eii_id = cursor.lastrowid
    
    # Insert signals
    signal_names = ['EpitopeDrift', 'SelectionPressure', 'GlycosylationDynamics', 
                    'PhylogeneticInstability', 'DistanceOutliers']
    signal_values = [epitope_drift, selection_pressure, glycosylation_dynamics, 
                     phylogenetic_instability, distance_outliers]
    
    for name, val in zip(signal_names, signal_values):
        cursor.execute("""
            INSERT INTO eii_signals (signal_name, mean_value, created_at)
            VALUES (%s, %s, NOW())
        """, (name, val))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Database updated successfully. EII: {eii_value:.2f}")
    
except Exception as e:
    print(f"❌ Database error: {e}")
