import argparse
import csv
from pathlib import Path

def parse_seqkit(path):
    # MAG, file, format, type, num_seqs, sum_len, min_len, avg_len, max_len, Q1, Q2, Q3, sum_gap, N50, N50_num, Q20(%), Q30(%), AvgQual, GC(%), sum_n
    with open(path) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip header
        row = next(reader) # Read data row
        return {
            "MAG": row[0],
            "num_contigs": row[4],
            "genome_size_bp": row[5],
            "N50": row[13],
            "GC": row[18],
            "sum_ambiguous_bases": row[19]
        }

def parse_orfs(path):
    # orf_count
    with open(path) as f:
        next(f)
        return {"num_ORFs": next(f).strip()}

def parse_checkm(path, mag, method):
    with open(path) as f:
        rdr = csv.DictReader(f, delimiter='\t')
        for row in rdr:
            if method == "checkm2" and row.get("Name") == mag:
                return {"Completeness": row.get("Completeness", ""), "Contamination": row.get("Contamination", "")}
            elif method == "checkm1" and row.get("Bin Id") == mag:
                return {"Completeness": row.get("Completeness", ""), "Contamination": row.get("Contamination", "")}
    return {"Completeness": "", "Contamination": ""}

def parse_gunc(path, mag):
    with open(path) as f:
        rdr = csv.DictReader(f, delimiter='\t')
        for row in rdr:
            if row.get("genome") == mag:
                return {"GUNC_status": row.get("pass.GUNC", "")}
    return {"GUNC_status": ""}

def parse_park(path):
    with open(path) as f:
        next(f)
        return {"Park_Score": next(f).strip()}

def parse_mimag(path):
    with open(path) as f:
        next(f)
        return {"MIMAG_level": next(f).strip()}

def parse_trnas(path):
    with open(path) as f:
        next(f)
        return {"num_tRNAs": next(f).strip()}

def parse_rrnas(path):
    with open(path) as f:
        next(f)
        vals = next(csv.reader(f, delimiter='\t'))
        return {
            "num_5S_rRNAs": vals[0],
            "num_16S_rRNAs": vals[1],
            "num_23S_rRNAs": vals[2]
        }

def parse_gtdb(path, mag):
    with open(path) as f:
        rdr = csv.DictReader(f, delimiter='\t')
        for row in rdr:
            if row.get("user_genome") == mag:
                return {"GTDB_taxonomy": row.get("classification", "")}
    return {"GTDB_taxonomy": ""}

def parse_16s(path):
    """
    Parses the 16S BLAST output file.
    - If the file is empty, returns "NA" for both taxonomy and identity.
    - If the file has content, returns the last field for taxonomy and the 3rd field for identity.
    """
    with open(path) as f:
        line = f.readline()
        if not line:
            return {"16S_NCBI_taxonomy": "NA", "16S_blastn_identity": "NA"}
        
        fields = line.strip().split('\t')
        
        identity = fields[2] if len(fields) >= 3 else "NA"
        taxonomy = fields[-1] if fields else "NA"

        return {"16S_NCBI_taxonomy": taxonomy, "16S_blastn_identity": identity}

def main(args):
    mags = []
    # 以seqkit文件为主，遍历所有MAG
    for i, seqkit_path in enumerate(args.seqkit):
        mag = parse_seqkit(seqkit_path)["MAG"]
        row = {}
        row.update(parse_seqkit(seqkit_path))
        row.update(parse_orfs(args.orfs[i]))
        row.update(parse_checkm(args.checkm, mag, args.checkm_method))
        row.update(parse_gunc(args.gunc, mag))
        row.update(parse_park(args.park[i]))
        row.update(parse_mimag(args.mimag[i]))
        row.update(parse_trnas(args.trnas[i]))
        row.update(parse_rrnas(args.rrnas[i]))
        row.update(parse_gtdb(args.gtdb, mag))
        row.update(parse_16s(args._16s[i]))
        mags.append(row)

    # 输出
    columns = [
        "ID", "num_contigs", "genome_size_bp", "N50", "GC", "sum_ambiguous_bases",
        "num_ORFs", "Completeness", "Contamination", "GUNC_status", "Park_Score", "MIMAG_level",
        "num_tRNAs", "num_16S_rRNAs", "num_23S_rRNAs", "num_5S_rRNAs", "16S_NCBI_taxonomy", "16S_blastn_identity", "GTDB_taxonomy"
    ]
    with open(args.output, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=columns, delimiter='\t')
        w.writeheader()
        for row in mags:
            w.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge MAG summary tables")
    parser.add_argument("--seqkit", nargs='+', required=True, help="SeqKit stats TSV files")
    parser.add_argument("--checkm", required=True, help="CheckM summary TSV file")
    parser.add_argument("--checkm-method", choices=["checkm1", "checkm2"], required=True, help="CheckM version used")
    parser.add_argument("--gunc", required=True, help="GUNC summary TSV file")
    parser.add_argument("--mimag", nargs='+', required=True, help="MIMAG classification TSV files")
    parser.add_argument("--park", nargs='+', required=True, help="Park score TSV files")
    parser.add_argument("--orfs", nargs='+', required=True, help="ORFs count TSV files")
    parser.add_argument("--trnas", nargs='+', required=True, help="tRNA count TSV files")
    parser.add_argument("--rrnas", nargs='+', required=True, help="rRNA count TSV files")
    parser.add_argument("--gtdb", required=True, help="GTDB-tk merged taxonomy TSV file")
    parser.add_argument("--16s", dest="_16s", nargs='+', required=True, help="16S BLAST taxonomy TSV files")
    parser.add_argument("--output", required=True, help="Output summary TSV file")
    parser.add_argument("--results", required=True, help="Results directory")
    args = parser.parse_args()
    main(args)
