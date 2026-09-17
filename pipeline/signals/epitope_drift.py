import numpy as np

def normalize(values):
    vals = np.array(values, dtype=float)

    if len(vals) == 0:
        return 0.0

    if np.max(vals) == 0:
        return 0.0

    vals = vals - np.min(vals)

    return float(np.mean(vals / (np.max(vals) + 1e-9)))


def compute_epitope_drift(arr):
    """
    Compute Shannon entropy across alignment columns.
    Returns normalized epitope drift score.
    """

    entropy_vals = []

    for col in arr.T:
        bases, counts = np.unique(col, return_counts=True)
        freqs = counts / np.sum(counts)

        entropy = -np.sum(freqs * np.log2(freqs))

        entropy_vals.append(entropy)

    return normalize(entropy_vals)
