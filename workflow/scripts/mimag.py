from __future__ import annotations

import sys
import csv
from pathlib import Path

"""MIMAG classification
HQ: Completeness > 90, Contamination < 5, tRNA >= 18, rRNA has 5S,16S,23S
MQ: Completeness >= 50, Contamination < 10
LQ: else
"""

def main(quality_tsv: Path, trna_tsv: Path, rrna_tsv: Path, out_tsv: Path) -> None:
    comp = cont = 0.0
    trna_count = 0
    has_5s = has_16s = has_23s = False
    # quality
    with open(quality_tsv) as f:
        rdr = csv.DictReader(f, delimiter='\t')
        for r in rdr:
            comp = float(r.get("checkm_completeness", 0) or 0)
            cont = float(r.get("checkm_contamination", 0) or 0)
            break
    # trna
    with open(trna_tsv) as f:
        next(f)
        line = f.readline().strip()
        if line:
            try:
                trna_count = int(line.split('\t')[0])
            except Exception:
                trna_count = 0
    # rrna counts
    with open(rrna_tsv) as f:
        next(f)
        vals = f.readline().strip().split('\t') if f else ["0","0","0","0"]
        try:
            has_5s = int(vals[0]) > 0
            has_16s = int(vals[1]) > 0
            has_23s = int(vals[2]) > 0
        except Exception:
            pass
    quality = "LQ"
    if comp > 90 and cont < 5 and trna_count >= 18 and has_5s and has_16s and has_23s:
        quality = "HQ"
    elif comp >= 50 and cont < 10:
        quality = "MQ"
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_tsv, 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(["MIMAG"])
        w.writerow([quality])

if __name__ == "__main__":
    q, t, r, o = map(Path, sys.argv[1:5])
    main(q, t, r, o)
