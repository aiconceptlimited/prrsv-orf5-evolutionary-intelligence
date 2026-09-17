import re
import numpy as np
from Bio.Seq import Seq

def normalize(values):
    vals = np.array(values, dtype=float)

    if len(vals) == 0:
        return 0.0

    if np.max(vals) == 0:
        return 0.0

    vals = vals - np.min(vals)

    return float(np.mean(vals / (np.max(vals) + 1e-9)))

def compute_glycosylation_dynamics(seqs):
    """
    Compute glycosylation motif dynamics using
    N-X-S/T motif detection.
    """

    glyco_counts = []

    for seq in seqs:

        seq = seq.replace("-", "")

        trim_len = (len(seq) // 3) * 3
        seq = seq[:trim_len]

        if len(seq) < 3:
            continue

        aa_seq = str(Seq(seq).translate(to_stop=False))

        motifs = re.findall(r"N[^P][ST]", aa_seq)

        glyco_counts.append(len(motifs))

    return normalize(glyco_counts)
