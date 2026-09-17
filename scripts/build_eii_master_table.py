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

def classify(row):

    if row["SelectionScore"] == 2:

        if row["GlycoFrequency"] > 0.30:
            return "Immune Escape"

        elif row["Entropy"] > 1.5:
            return "Diversifying Selection"

        else:
            return "Adaptive Convergence"

    elif row["Entropy"] > 1.5:
        return "High Variability"

    elif row["GlycoFrequency"] > 0.30:
        return "Glycosylation Shield"

    else:
        return "Conserved / Neutral"

df["Mechanism"] = df.apply(
    classify,
    axis=1
)

df["FinalScore"] = (
      0.50 * df["SiteEII"]
    + 0.20 * (df["SelectionScore"] / 2.0)
    + 0.20 * (df["Entropy"] / df["Entropy"].max())
    + 0.10 * df["GlycoFrequency"]
)

df = df.sort_values(
    "FinalScore",
    ascending=False
)

outfile = (
    "data/eii/final/EII_MASTER_TABLE.csv"
)

df.to_csv(
    outfile,
    index=False
)

print("\nSaved:", outfile)

print("\nTop 20 Hotspots\n")

print(
    df[
        [
            "Site",
            "SiteEII",
            "SelectionScore",
            "Entropy",
            "GlycoFrequency",
            "Mechanism",
            "FinalScore"
        ]
    ]
    .head(20)
)
