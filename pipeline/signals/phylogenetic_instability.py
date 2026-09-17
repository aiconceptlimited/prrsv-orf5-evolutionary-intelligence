import numpy as np
from scipy.spatial.distance import pdist

def normalize(values):
    vals = np.array(values, dtype=float)

    if len(vals) == 0:
        return 0.0

    if np.max(vals) == 0:
        return 0.0

    vals = vals - np.min(vals)

    return float(
        np.mean(
            vals / (np.max(vals) + 1e-9)
        )
    )

def compute_phylogenetic_instability(arr):

    mapping = {
        "A": 0,
        "T": 1,
        "G": 2,
        "C": 3,
        "-": 4,
        "N": 5,
    }

    numeric_arr = np.vectorize(
        lambda x: mapping.get(x, 5)
    )(arr)

    phylo_dist = pdist(
        numeric_arr,
        metric="hamming"
    )

    phylo_norm = normalize(phylo_dist)

    return phylo_norm, phylo_dist
