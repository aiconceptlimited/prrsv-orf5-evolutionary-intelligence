import pandas as pd


def compute_adaptive_selection():

    infile = (
        "data/eii/selection/"
        "selection_overlap.csv"
    )

    df = pd.read_csv(infile)

    # SelectionScore:
    # 0 = none
    # 1 = FEL or MEME
    # 2 = FEL + MEME

    max_score = 2.0

    adaptive_score = (
        df["SelectionScore"].sum()
        /
        (len(df) * max_score)
    )

    return float(adaptive_score)
