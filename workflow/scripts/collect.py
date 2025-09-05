from __future__ import annotations

import sys
from pathlib import Path
import csv
import re
import pandas as pd

# Collect per-sample TSVs into a consolidated table
# We try to join on sample name across available modules.

MODULES = {
    "seqkit": ("results/seqkit", ".seqkit.tsv"),
    "quality2": ("results/quality", ".checkm2.tsv"),
    "quality1": ("results/quality", ".checkm1.tsv"),
    "park": ("results/park", ".park.tsv"),
    "gunc": ("results/gunc", ".gunc.tsv"),
    "rrna": ("results/rrna", ".rrna.tsv"),
    "trna": ("results/trna", ".trna.tsv"),
    "orfs": ("results/orfs", ".orfs.tsv"),
    "gtdb": ("results/gtdbtk", ".gtdb.tsv"),
    "r16": ("results/16S", ".16S.tsv"),
    "mimag": ("results/mimag", ".mimag.tsv"),
}


def load_optional_tsv(path: Path, key: str) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, sep='\t')
    except Exception:
        return pd.DataFrame()
    # Ensure sample column exists
    if 'mag' in df.columns:
        df = df.rename(columns={'mag': 'sample'})
    if 'sample' not in df.columns:
        # Inject sample from filename
        df.insert(0, 'sample', path.stem.replace(path.suffix, ''))
    # Prefix columns (except sample) to avoid collisions
    cols = ['sample'] + [f"{key}_{c}" for c in df.columns if c != 'sample']
    df.columns = cols
    return df


def canonicalize(df: pd.DataFrame) -> pd.DataFrame:
    # Start canonical fields
    df = df.rename(columns={"sample": "MAG_ID"})
    # Stats
    if "seqkit_sum_len" in df.columns:
        df = df.rename(columns={
            "seqkit_sum_len": "Genome_Size",
            "seqkit_num_seqs": "Num_Contigs",
            "seqkit_N50": "N50",
            "seqkit_GC": "GC_Content",
            "seqkit_Npct": "N_pct",
        })
        if "N_pct" in df.columns and "Genome_Size" in df.columns:
            try:
                df["Ambiguous_Bases"] = (df["N_pct"].astype(float) / 100.0 * df["Genome_Size"].astype(float)).round().astype("Int64")
            except Exception:
                df["Ambiguous_Bases"] = pd.NA
    # Quality
    for qpref in ("quality2", "quality1"):
        c = f"{qpref}_checkm_completeness"
        k = f"{qpref}_checkm_contamination"
        if c in df.columns:
            df = df.rename(columns={c: "Completeness"})
        if k in df.columns:
            df = df.rename(columns={k: "Contamination"})
    # Park score
    if "park_park_score" in df.columns:
        df = df.rename(columns={"park_park_score": "Park_Score"})
    # rRNA counts
    rrna_map = {
        "rrna_5S": "rRNA_5S",
        "rrna_16S": "rRNA_16S",
        "rrna_23S": "rRNA_23S",
        "rrna_total": "rRNA_total",
    }
    df = df.rename(columns={k: v for k, v in rrna_map.items() if k in df.columns})
    # tRNA
    if "trna_trna_count" in df.columns:
        df = df.rename(columns={"trna_trna_count": "tRNA_count"})
    # ORFs
    if "orfs_orf_count" in df.columns:
        df = df.rename(columns={"orfs_orf_count": "Gene_count"})
    # GTDB
    if "gtdb_lineage" in df.columns:
        df = df.rename(columns={"gtdb_lineage": "GTDB_Taxonomy"})
        def get_rank(lineage: str, rank: str) -> str:
            if not isinstance(lineage, str):
                return ""
            m = re.search(rf"{rank}__([^;]+)", lineage)
            return m.group(1) if m else ""
        df["Domain"] = df["GTDB_Taxonomy"].apply(lambda s: get_rank(s, 'd'))
        df["Phylum"] = df["GTDB_Taxonomy"].apply(lambda s: get_rank(s, 'p'))
    # 16S taxonomy
    if "r16_stitle" in df.columns:
        df = df.rename(columns={"r16_stitle": "Taxonomy_16S"})
    # MIMAG
    if "mimag_MIMAG" in df.columns:
        df = df.rename(columns={"mimag_MIMAG": "MIMAG_Quality"})
    return df


def main(out_tsv: Path, results_dir: Path, mag_paths: list[str]):
    samples = [Path(p).stem for p in mag_paths]
    base = pd.DataFrame({'sample': samples})
    for key, (subdir, suffix) in MODULES.items():
        merged_any = False
        dfs = []
        for s in samples:
            p = Path(results_dir) / subdir / f"{s}{suffix}"
            if p.exists():
                df = load_optional_tsv(p, key)
                if not df.empty:
                    dfs.append(df)
        if dfs:
            dfcat = pd.concat(dfs, axis=0, ignore_index=True)
            base = base.merge(dfcat, on='sample', how='left')
    base = canonicalize(base)
    base.to_csv(out_tsv, sep='\t', index=False)


if __name__ == '__main__':
    out = Path(sys.argv[1])
    results_dir = Path(sys.argv[2])
    mags = sys.argv[3:]
    out.parent.mkdir(parents=True, exist_ok=True)
    main(out, results_dir, mags)
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List

FIELDS = [
    "MAG_ID",
    "Genome_Size",
    "Num_Contigs",
    "N50",
    "GC",
    "Ambiguous_Bases",
    "CheckM_Completeness",
    "CheckM_Contamination",
    "GUNC_Score",
    "GUNC_Status",
    "rRNA_5S",
    "rRNA_16S",
    "rRNA_23S",
    "rRNA_Total",
    "tRNA_Count",
    "ORF_Count",
    "GTDB_Lineage",
    "R16_TopHit",
    "Park_Score",
    "MIMAG_Quality",
]


def read_first_value(tsv_path: Path) -> str:
    if not tsv_path.exists() or tsv_path.stat().st_size == 0:
        return ""
    with open(tsv_path) as f:
        rdr = csv.reader(f, delimiter='\t')
        next(rdr, None)
        row = next(rdr, None)
        return row[0] if row else ""


def parse_seqkit(tsv_path: Path):
    if not tsv_path.exists():
        return {"Genome_Size": "", "Num_Contigs": "", "N50": "", "GC": "", "Ambiguous_Bases": ""}
    with open(tsv_path) as f:
        r = next(csv.reader(f, delimiter='\t'))
        try:
            genome_size = r[5]
            num_contigs = r[4]
            n50 = r[10]
            gc = r[12]
            n_pct = float(r[13])
            amb = int(round(n_pct/100.0 * float(genome_size))) if genome_size else ""
        except Exception:
            genome_size = num_contigs = n50 = gc = amb = ""
    return {
        "Genome_Size": genome_size,
        "Num_Contigs": num_contigs,
        "N50": n50,
        "GC": gc,
        "Ambiguous_Bases": amb,
    }


def main(out_tsv: Path, mags: List[str], results_dir: Path):
    rows: List[Dict[str, str]] = []
    for mag in mags:
        stem = Path(mag).stem
        row = {f: "" for f in FIELDS}
        row["MAG_ID"] = stem
        # stats
        row.update(parse_seqkit(results_dir/"seqkit"/f"{stem}.seqkit.tsv"))
        # quality
        q = results_dir/"quality"/f"{stem}.checkm2.tsv"
        if not q.exists():
            q = results_dir/"quality"/f"{stem}.checkm1.tsv"
        if q.exists():
            with open(q) as f:
                rdr = csv.DictReader(f, delimiter='\t')
                r = next(rdr, None)
                if r:
                    row["CheckM_Completeness"] = r.get("checkm_completeness", "")
                    row["CheckM_Contamination"] = r.get("checkm_contamination", "")
        # gunc
        g = results_dir/"gunc"/f"{stem}.gunc.tsv"
        if g.exists():
            with open(g) as f:
                next(f)
                vals = f.readline().strip().split('\t') if f else ["",""]
                row["GUNC_Score"], row["GUNC_Status"] = (vals + [""]*2)[:2]
        # rrna
        rr = results_dir/"rrna"/f"{stem}.rrna.tsv"
        if rr.exists():
            with open(rr) as f:
                next(f)
                vals = f.readline().strip().split('\t') if f else ["0","0","0","0"]
                row["rRNA_5S"], row["rRNA_16S"], row["rRNA_23S"], row["rRNA_Total"] = (vals + ["","","",""])[:4]
        # trna
        row["tRNA_Count"] = read_first_value(results_dir/"trna"/f"{stem}.trna.tsv")
        # orfs
        row["ORF_Count"] = read_first_value(results_dir/"orfs"/f"{stem}.orfs.tsv")
        # gtdb
        row["GTDB_Lineage"] = read_first_value(results_dir/"gtdbtk"/f"{stem}.gtdb.tsv")
        # r16
        row["R16_TopHit"] = read_first_value(results_dir/"16S"/f"{stem}.16S.tsv")
        # park
        row["Park_Score"] = read_first_value(results_dir/"park"/f"{stem}.park.tsv")
        # mimag
        row["MIMAG_Quality"] = read_first_value(results_dir/"mimag"/f"{stem}.mimag.tsv")
        rows.append(row)
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_tsv, 'w', newline='') as f:
        w = csv.DictWriter(f, delimiter='\t', fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)

if __name__ == "__main__":
    out = Path(sys.argv[1])
    results = Path(sys.argv[2])
    mags = sys.argv[3:]
    main(out, mags, results)
