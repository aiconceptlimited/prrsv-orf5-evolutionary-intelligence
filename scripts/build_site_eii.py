import pandas as pd

# ----------------------------------------
# Load conservation / entropy
# ----------------------------------------

ce = pd.read_csv(
    "data/eii/features/conservation_entropy.csv"
)

# ----------------------------------------
# Load selection overlap
# ----------------------------------------

sel = pd.read_csv(
    "data/eii/selection/selection_overlap.csv"
)

# ----------------------------------------
# Merge
# ----------------------------------------

df = ce.merge(
    sel,
    on="Site",
    how="left"
)

# ----------------------------------------
# Simple Site EII
# ----------------------------------------

df["Variability"] = 1 - df["Conservation"]

df["SelectionNorm"] = (
    df["SelectionScore"] / 2.0
)

df["EntropyNorm"] = (
    df["Entropy"] /
    df["Entropy"].max()
)

df["SiteEII"] = (
      0.40 * df["SelectionNorm"]
    + 0.35 * df["EntropyNorm"]
    + 0.25 * df["Variability"]
)

outfile = (
    "data/eii/final/"
    "eii_site_scores.csv"
)

df.to_csv(
    outfile,
    index=False
)

print("Saved:", outfile)

print("\nTop 20 EII sites\n")

print(
    df.sort_values(
        "SiteEII",
        ascending=False
    )[[
        "Site",
        "Conservation",
        "Entropy",
        "SelectionScore",
        "SiteEII"
    ]].head(20)
)
