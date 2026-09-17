import json
import pandas as pd

with open(
    "data/alignments/orf5_codon_prank_nostop.fasta.FEL.json"
) as f:
    data = json.load(f)

sites = data["MLE"]["content"]["0"]

rows = []

for i, row in enumerate(sites, start=1):

    alpha = row[0]
    beta = row[1]
    p = row[4]

    if p <= 0.10:

        if beta > alpha:
            selection = "Positive"
        elif beta < alpha:
            selection = "Negative"
        else:
            selection = "Neutral"

        rows.append({
            "Site": i,
            "Alpha": alpha,
            "Beta": beta,
            "PValue": p,
            "Selection": selection
        })

df = pd.DataFrame(rows)

outfile = "data/eii/selection/fel_sites.csv"

df.to_csv(outfile, index=False)

print("Saved:", outfile)
print("Sites:", len(df))

print("\nPositive sites:")
print(len(df[df["Selection"]=="Positive"]))

print("\nNegative sites:")
print(len(df[df["Selection"]=="Negative"]))
