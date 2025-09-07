from __future__ import annotations

import sys
import csv
from pathlib import Path

# Usage: python mimag.py quality.tsv trna.tsv rrna.tsv out.tsv --mag MAG1 --method checkm2

"""MIMAG classification
HQ: Completeness > 90, Contamination < 5, tRNA >= 18, rRNA has 5S,16S,23S
MQ: Completeness >= 50, Contamination < 10
LQ: else
"""

def main(quality_tsv: Path, trna_tsv: Path, rrna_tsv: Path, out_tsv: Path, mag_name: str, method: str) -> None:
    comp = cont = 0.0
    trna_count = 0
    has_5s = has_16s = has_23s = False
    # quality
    with open(quality_tsv) as f:
        if method == "checkm2":
            # For CheckM2, find the row with matching genome name
            for row in csv.DictReader(f, delimiter='\t'):
                if mag_name in row.get("Name", ""):
                    print(f"found quality row for {mag_name}")
                    comp = float(row.get("Completeness", 0) or 0)
                    cont = float(row.get("Contamination", 0) or 0)
                    break
        else:  # checkm1
            # For CheckM1, find the row with matching bin id
            for row in csv.DictReader(f, delimiter='\t'):
                if mag_name in row.get("Bin Id", ""):
                    comp = float(row.get("Completeness", 0) or 0)
                    cont = float(row.get("Contamination", 0) or 0)
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
    print(f"MIMAG for {mag_name}: {quality} (comp={comp}, cont={cont}, tRNA={trna_count}, 5S={has_5s},16S={has_16s},23S={has_23s})")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Classify MAG according to MIMAG standards")
    parser.add_argument("quality_tsv", type=Path, help="CheckM quality TSV file")
    parser.add_argument("trna_tsv", type=Path, help="tRNA results TSV file")
    parser.add_argument("rrna_tsv", type=Path, help="rRNA results TSV file")
    parser.add_argument("out_tsv", type=Path, help="Output TSV file")
    parser.add_argument("--mag", required=True, help="MAG name to process")
    parser.add_argument("--method", choices=["checkm1", "checkm2"], default="checkm2", help="CheckM version used")
    args = parser.parse_args()
    
    main(args.quality_tsv, args.trna_tsv, args.rrna_tsv, args.out_tsv, args.mag, args.method)
