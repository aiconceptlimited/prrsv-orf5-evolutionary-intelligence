from Bio import SeqIO
import pandas as pd

records = list(
    SeqIO.parse(
        "data/alignments/orf5_prank_nostop.best.fas",
        "fasta"
    )
)

seqs = [str(r.seq) for r in records]

length = len(seqs[0])

rows = []

for pos in range(length - 2):

    motif_count = 0
    total = 0

    for seq in seqs:

        a = seq[pos]
        b = seq[pos + 1]
        c = seq[pos + 2]

        if "-" in (a, b, c):
            continue

        total += 1

        if (
            a == "N"
            and b != "P"
            and c in ["S", "T"]
        ):
            motif_count += 1

    freq = 0.0

    if total > 0:
        freq = motif_count / total

    rows.append([
        pos + 1,
        round(freq, 6)
    ])

df = pd.DataFrame(
    rows,
    columns=[
        "Site",
        "GlycoFrequency"
    ]
)

outfile = (
    "data/eii/features/"
    "glyco_sites.csv"
)

df.to_csv(
    outfile,
    index=False
)

print("Saved:", outfile)
print()

print(
    df.sort_values(
        "GlycoFrequency",
        ascending=False
    ).head(20)
)
