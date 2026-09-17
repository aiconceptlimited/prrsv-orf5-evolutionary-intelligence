import pandas as pd

# --------------------------------------------------
# Load FEL
# --------------------------------------------------

fel = pd.read_csv(
    "data/eii/selection/fel_sites.csv"
)

fel_positive = set(
    fel[fel["Selection"]=="Positive"]["Site"]
)

# --------------------------------------------------
# Load MEME
# --------------------------------------------------

meme = pd.read_csv(
    "data/eii/selection/meme_sites.csv"
)

meme_positive = set(
    meme["Site"]
)

# --------------------------------------------------
# Build overlap table
# --------------------------------------------------

rows = []

for site in range(1,210):

    fel_hit = int(site in fel_positive)
    meme_hit = int(site in meme_positive)

    score = fel_hit + meme_hit

    rows.append([
        site,
        fel_hit,
        meme_hit,
        score
    ])

df = pd.DataFrame(
    rows,
    columns=[
        "Site",
        "FEL",
        "MEME",
        "SelectionScore"
    ]
)

outfile = (
    "data/eii/selection/"
    "selection_overlap.csv"
)

df.to_csv(outfile,index=False)

print("Saved:",outfile)

print("\nScore distribution")
print(
    df["SelectionScore"]
    .value_counts()
    .sort_index()
)
