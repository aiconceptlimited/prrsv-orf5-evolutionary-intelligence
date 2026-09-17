import numpy as np

def compute_distance_outliers(phylo_dist):

    mean_dist = np.mean(phylo_dist)
    std_dist = np.std(phylo_dist)

    outliers = phylo_dist > (
        mean_dist + 2 * std_dist
    )

    return float(np.mean(outliers))
