import json
import pandas as pd

with open(
    "data/alignments/orf5_codon_prank_nostop.fasta.MEME.json"
) as f:
    data = json.load(f)

sites = data["MLE"]["content"]["0"]

rows = []

for i, row in enumerate(sites, start=1):

    p = row[6]

    if p <= 0.10:
        rows.append({
            "Site": i,
            "Alpha": row[0],
            "BetaPlus": row[3],
            "PValue": p,
            "Branches": row[7]
        })

df = pd.DataFrame(rows)

outfile = "data/eii/selection/meme_sites.csv"

df.to_csv(outfile, index=False)

print("Saved:", outfile)
print("Sites:", len(df))
