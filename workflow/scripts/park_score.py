from __future__ import annotations

import sys
import csv
from pathlib import Path

"""
Compute Park score:
Score = Completeness - (5 * Contamination) - (5 * num_contigs / 100) - (5 * amb_bases / 100000)
Inputs: join from stats and checkm outputs.
"""

def main(stats_tsv: Path, quality_tsv: Path, out_tsv: Path) -> None:
    metrics = {"num_contigs": 0, "amb_bases": 0}
    comp = 0.0
    cont = 0.0
    # Parse seqkit stats row: mag,readable headers unknown; detect Ns and contigs
    with open(stats_tsv) as f:
        rdr = csv.reader(f, delimiter='\t')
        header = next(rdr, None)
        row = next(rdr, None)
        # Try to infer number of sequences/contigs and N count from seqkit output order
        # Expected columns after prepend: mag, file, format, type, num_seqs, sum_len, min_len, avg_len, max_len, Q1, N50, Q3, GC, N%
        try:
            num_contigs = int(row[4]) if row and len(row) > 4 else 0
        except Exception:
            num_contigs = 0
        try:
            n_pct = float(row[13]) if row and len(row) > 13 else 0.0
            genome_size = int(float(row[5])) if row and len(row) > 5 else 0
            amb_bases = int(round(n_pct/100.0 * genome_size))
        except Exception:
            amb_bases = 0
        metrics["num_contigs"] = num_contigs
        metrics["amb_bases"] = amb_bases
    # Parse quality
    with open(quality_tsv) as f:
        rdr = csv.DictReader(f, delimiter='\t')
        for r in rdr:
            comp = float(r.get("checkm_completeness", 0) or 0)
            cont = float(r.get("checkm_contamination", 0) or 0)
            break
    score = comp - (5*cont) - (5*metrics["num_contigs"]/100.0) - (5*metrics["amb_bases"]/100000.0)
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_tsv, 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(["park_score"]) 
        w.writerow([f"{score:.3f}"])

if __name__ == "__main__":
    stats, qual, outp = map(Path, sys.argv[1:4])
    main(stats, qual, outp)
