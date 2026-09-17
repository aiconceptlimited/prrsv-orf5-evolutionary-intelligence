import numpy as np

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

def compute_selection_pressure(arr):

    codon_variability = []

    for col in range(
        0,
        arr.shape[1] - 2,
        3
    ):

        codons = []

        for row in arr:

            codon = "".join(
                row[col:col+3]
            )

            if "-" not in codon:
                codons.append(codon)

        codon_variability.append(
            len(set(codons))
        )

    return normalize(
        codon_variability
    )
