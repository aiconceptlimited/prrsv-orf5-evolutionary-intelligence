from Bio import SeqIO
import pandas as pd
import math
from collections import Counter

# --------------------------------------------------
# Load aligned protein sequences
# --------------------------------------------------

records = list(
    SeqIO.parse(
        "data/alignments/orf5_prank_nostop.best.fas",
        "fasta"
    )
)

print(f"Loaded {len(records)} aligned sequences")

seqs = [str(r.seq) for r in records]

# All PRANK sequences should have same length
alignment_length = len(seqs[0])

print(f"Alignment length: {alignment_length}")

# Verify alignment consistency
for s in seqs:
    if len(s) != alignment_length:
        raise ValueError(
            f"Inconsistent alignment length: {len(s)}"
        )

# --------------------------------------------------
# Compute conservation and entropy
# --------------------------------------------------

rows = []

for pos in range(alignment_length):

    residues = []

    for s in seqs:

        aa = s[pos]

        if aa != "-":
            residues.append(aa)

    if len(residues) == 0:

        conservation = 0.0
        entropy = 0.0

    else:

        counts = Counter(residues)

        total = len(residues)

        max_freq = max(counts.values())

        conservation = max_freq / total

        entropy = 0.0

        for count in counts.values():

            p = count / total

            entropy -= p * math.log2(p)

    rows.append([
        pos + 1,
        round(conservation, 6),
        round(entropy, 6)
    ])

# --------------------------------------------------
# Save results
# --------------------------------------------------

df = pd.DataFrame(
    rows,
    columns=[
        "Site",
        "Conservation",
        "Entropy"
    ]
)

outfile = (
    "data/eii/features/"
    "conservation_entropy.csv"
)

df.to_csv(
    outfile,
    index=False
)

print(f"\nSaved: {outfile}")
print(f"Sites: {len(df)}")

print("\nTop conserved sites:")
print(
    df.sort_values(
        "Conservation",
        ascending=False
    ).head(10)
)

print("\nHighest entropy sites:")
print(
    df.sort_values(
        "Entropy",
        ascending=False
    ).head(10)
)
