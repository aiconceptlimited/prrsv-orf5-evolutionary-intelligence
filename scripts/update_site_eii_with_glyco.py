import pandas as pd

eii = pd.read_csv(
    "data/eii/final/eii_site_scores.csv"
)

glyco = pd.read_csv(
    "data/eii/features/glyco_sites.csv"
)

df = eii.merge(
    glyco,
    on="Site",
    how="left"
)

df["GlycoFrequency"] = (
    df["GlycoFrequency"]
    .fillna(0)
)

# Updated EII

df["SiteEII_v2"] = (
      0.35 * df["SelectionNorm"]
    + 0.25 * df["EntropyNorm"]
    + 0.20 * df["Variability"]
    + 0.20 * df["GlycoFrequency"]
)

outfile = (
    "data/eii/final/"
    "eii_site_scores_v2.csv"
)

df.to_csv(
    outfile,
    index=False
)

print("Saved:", outfile)

print("\nTop 25 sites\n")

print(
    df.sort_values(
        "SiteEII_v2",
        ascending=False
    )[[
        "Site",
        "SelectionScore",
        "Conservation",
        "Entropy",
        "GlycoFrequency",
        "SiteEII_v2"
    ]].head(25)
)
