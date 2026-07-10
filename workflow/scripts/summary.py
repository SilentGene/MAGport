import argparse
import csv
from pathlib import Path
from collections import defaultdict

""" example
python workflow/scripts/summary.py \
            --mags /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/input_MAGs.txt \
            --seqkit /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/01_stats/seqkit/GCF_024346955.1_vmangrovi.seqkit.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/01_stats/seqkit/MAG1.seqkit.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/01_stats/seqkit/MAG209.seqkit.tsv \
            --checkm /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/03_quality/checkm/checkm2_summary.tsv \
            --gunc /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/03_quality/gunc/GUNC_summary.tsv \
            --mimag /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/03_quality/mimag/GCF_024346955.1_vmangrovi.MIMAG_level.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/03_quality/mimag/MAG1.MIMAG_level.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/03_quality/mimag/MAG209.MIMAG_level.tsv \
            --park /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/03_quality/park/GCF_024346955.1_vmangrovi.park.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/03_quality/park/MAG1.park.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/03_quality/park/MAG209.park.tsv \
            --orfs /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/02_genes/orfs/GCF_024346955.1_vmangrovi.orfs.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/02_genes/orfs/MAG1.orfs.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/02_genes/orfs/MAG209.orfs.tsv \
            --trnas /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/02_genes/trna/GCF_024346955.1_vmangrovi.tRNA.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/02_genes/trna/MAG1.tRNA.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/02_genes/trna/MAG209.tRNA.tsv \
            --rrnas /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/02_genes/rrna/GCF_024346955.1_vmangrovi.rRNA.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/02_genes/rrna/MAG1.rRNA.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/02_genes/rrna/MAG209.rRNA.tsv \
            --gtdb /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/04_taxonomy/gtdbtk/gtdb.merged_summary.tsv \
            --16s /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/04_taxonomy/16S/GCF_024346955.1_vmangrovi.16S.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/04_taxonomy/16S/MAG1.16S.tsv /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/04_taxonomy/16S/MAG209.16S.tsv \
            --output /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output/MAGport_summary.tsv \
            --results /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output
"""

class DataLoader:
    def __init__(self, args):
        self.args = args
        # 加载共享文件数据
        self.checkm_data = self._load_checkm() if args.checkm else {}
        self.gunc_data = self._load_gunc() if args.gunc else {}
        self.gtdb_data = self._load_gtdb() if args.gtdb else {}
        # 加载每个MAG的文件数据
        self.seqkit_data = self._load_multiple_files(args.seqkit, self._parse_seqkit, ".seqkit.tsv") if args.seqkit else {}
        self.orfs_data = self._load_multiple_files(args.orfs, self._parse_orfs, ".orfs.tsv") if args.orfs else {}
        self.park_data = self._load_multiple_files(args.park, self._parse_park, ".parks.tsv") if args.park else {}
        self.mimag_data = self._load_multiple_files(args.mimag, self._parse_mimag, ".MIMAG_level.tsv") if args.mimag else {}
        self.trnas_data = self._load_multiple_files(args.trnas, self._parse_trnas, ".tRNA.tsv") if args.trnas else {}
        self.rrnas_data = self._load_multiple_files(args.rrnas, self._parse_rrnas, ".rRNA.tsv") if args.rrnas else {}
        self.s16_data = self._load_multiple_files(args._16s, self._parse_16s, ".16S.tsv") if args._16s else {}
        self.coding_density_data = self._load_multiple_files(args.coding_density, self._parse_coding_density, ".coding_density.tsv") if args.coding_density else {}

    def _load_checkm(self):
        data = {}
        with open(self.args.checkm) as f:
            rdr = csv.DictReader(f, delimiter='\t')
            for row in rdr:
                key = row.get("Name")
                if key:
                    data[key] = {
                        "Completeness": row.get("Completeness", ""),
                        "Contamination": row.get("Contamination", "")
                    }
        return data

    def _load_gunc(self):
        data = {}
        with open(self.args.gunc) as f:
            rdr = csv.DictReader(f, delimiter='\t')
            for row in rdr:
                genome = row.get("genome")
                if genome:
                    data[genome] = {"pass_GUNC": row.get("pass.GUNC", "")}
        return data

    def _load_gtdb(self):
        data = {}
        try:
            with open(self.args.gtdb) as f:
                rdr = csv.DictReader(f, delimiter='\t')
                has_new_id = "ID_new" in rdr.fieldnames if rdr.fieldnames else False
                for row in rdr:
                    key = row.get("ID_new") if has_new_id and row.get("ID_new") else row.get("user_genome")
                    if key:
                        data[key] = {"GTDB_taxonomy": row.get("classification", "")}
        except Exception:
            pass
        return data

    def _load_multiple_files(self, paths, parser_func, suffix):
        result = {}
        for path in paths:
            filename = Path(path).name
            mag_id = filename.removesuffix(suffix)
            result[mag_id] = parser_func(path)
        return result

    @staticmethod
    def _parse_seqkit(path):
        with open(path) as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)  # Skip header
            row = next(reader)  # Read data row
            return {
                "num_contigs": row[4],
                "genome_size_bp": row[5],
                "N50": row[13],
                "GC": row[18],
                "Ambiguous_bases": row[19]
            }

    @staticmethod
    def _parse_orfs(path):
        with open(path) as f:
            next(f)
            return {"num_ORFs": next(f).strip()}

    @staticmethod
    def _parse_park(path):
        try:
            with open(path) as f:
                next(f)
                return {"Parks_score_reduced": next(f).strip()}
        except Exception:
            return {"Parks_score_reduced": ""}

    @staticmethod
    def _parse_mimag(path):
        try:
            with open(path) as f:
                reader = csv.DictReader(f, delimiter='\t')
                row = next(reader)
                return {
                    "MIMAG_reduced_level": row.get("MIMAG_reduced_level", ""),
                    "MIMAG_full_level": row.get("MIMAG_full_level", "")
                }
        except Exception:
            return {"MIMAG_reduced_level": "", "MIMAG_full_level": ""}

    @staticmethod
    def _parse_trnas(path):
        try:
            with open(path) as f:
                next(f)
                return {"num_tRNAs": next(f).strip()}
        except Exception:
            return {"num_tRNAs": ""}

    @staticmethod
    def _parse_rrnas(path):
        try:
            with open(path) as f:
                next(f)
                vals = next(csv.reader(f, delimiter='\t'))
                return {
                    "5S": vals[0] if len(vals) > 0 else "",
                    "16S": vals[1] if len(vals) > 1 else "",
                    "23S": vals[2] if len(vals) > 2 else ""
                }
        except Exception:
            return {
                "5S": "",
                "16S": "",
                "23S": ""
            }

    @staticmethod
    def _parse_16s(path):
        try:
            with open(path) as f:
                line = f.readline()
                if not line:
                    return {"16S_NCBI_taxonomy": "", "16S_blastn_identity": ""}
                fields = line.strip().split('\t')
                identity = fields[2] if len(fields) >= 3 else ""
                taxonomy = fields[-1] if fields else ""
                return {"16S_NCBI_taxonomy": taxonomy, "16S_blastn_identity": identity}
        except Exception:
            return {"16S_NCBI_taxonomy": "", "16S_blastn_identity": ""}

    @staticmethod
    def _parse_coding_density(path):
        try:
            with open(path) as f:
                reader = csv.DictReader(f, delimiter='\t')
                row = next(reader)
                return {"coding_density": row.get("coding_density", "")}
        except Exception:
            return {"coding_density": ""}

    def get_mag_data(self, mag):
        """获取单个MAG的所有数据"""
        
        data = {"ID": mag}
        data.update(self.seqkit_data.get(mag, {}))
        data.update(self.orfs_data.get(mag, {}))
        data.update(self.coding_density_data.get(mag, {}))
        data.update(self.checkm_data.get(mag, {}))
        data.update(self.gunc_data.get(mag, {}))
        data.update(self.park_data.get(mag, {}))
        data.update(self.mimag_data.get(mag, {}))
        data.update(self.trnas_data.get(mag, {}))
        data.update(self.rrnas_data.get(mag, {}))
        data.update(self.gtdb_data.get(mag, {}))
        data.update(self.s16_data.get(mag, {}))
        return data

def _load_previous_summary(path):
    if not path:
        return [], []

    previous_path = Path(path)
    if not previous_path.exists():
        return [], []

    with open(previous_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = [dict(row) for row in reader]
        return reader.fieldnames or [], rows


def main(args):
    # 解析 GTDB_VERSION
    gtdb_version = args.gtdb_version or ""
    if gtdb_version:
        gtdb_version = gtdb_version.removeprefix("R").removeprefix("r")
    else:
        try:
            with open(args.gtdb_log, 'r') as f:
                for line in f:
                    if "Using GTDB-Tk reference data version " in line:
                        import re
                        match = re.search(r'version r([^:]+):?', line)
                        if match:
                            gtdb_version = match.group(1)
                        break
        except Exception:
            pass
    
    gtdb_col_name = f"Taxonomy_GTDB_R{gtdb_version}" if gtdb_version else "GTDB_taxonomy"

    # 初始化数据加载器
    loader = DataLoader(args)
    
    # 收集所有出现过的 MAG ID
    all_mag_ids = set()
    for d in [loader.seqkit_data, loader.orfs_data, loader.park_data, 
              loader.mimag_data, loader.trnas_data, loader.rrnas_data, loader.s16_data,
              loader.coding_density_data]:
        all_mag_ids.update(d.keys())
    
    # 也要从共享数据中收集（如果有 ID_new 或 user_genome）
    all_mag_ids.update(loader.checkm_data.keys())
    all_mag_ids.update(loader.gunc_data.keys())
    all_mag_ids.update(loader.gtdb_data.keys())

    mags = []
    for mag in sorted(all_mag_ids):
        mags.append(loader.get_mag_data(mag))

    # 输出
    columns = [
        "ID", "num_contigs", "genome_size_bp", "N50", "GC", "Ambiguous_bases",
        "num_ORFs", "Completeness", "Contamination", "coding_density", "pass_GUNC", "Parks_score_reduced", "MIMAG_reduced_level", "MIMAG_full_level",
        "num_tRNAs", "16S", "23S", "5S", "16S_NCBI_taxonomy", "16S_blastn_identity", gtdb_col_name, "GTDB_novelty"
    ]
    
    def get_gtdb_novelty(taxonomy):
        # 判断novel等级
        if taxonomy.startswith("d__"):
            fields = taxonomy.split(';')
            for rank, prefix in zip([
                "domain", "phylum", "class", "order", "family", "genus", "species"],
                ["d__", "p__", "c__", "o__", "f__", "g__", "s__"]):
                
                # 判断该等级是否缺失
                for f in fields:
                    if f.startswith(prefix) and (f == prefix):
                        return rank
            else:
                return "known species"
        elif taxonomy.startswith("Unclassified"):
            """
            Genomes that cannot be assigned to a domain (e.g. genomes with no bacterial or archaeal markers or genomes with no genes called by Prodigal) are now reported in the gtdbtk.bac120.summary.tsv as 'Unclassified'
            Genomes filtered out during the alignment step are now reported in the gtdbtk.bac120.summary.tsv or gtdbtk.ar53.summary.tsv as 'Unclassified Bacteria/Archaea'
            """
            return "Unclassified"
        else:
            return "NA"

    previous_columns, previous_rows = _load_previous_summary(args.previous_summary)
    output_rows = []
    seen_ids = set()

    for row in previous_rows:
        mag_id = row.get("ID")
        if mag_id:
            output_rows.append(row)
            seen_ids.add(mag_id)

    for row in mags:
        taxonomy = row.get("GTDB_taxonomy", "")
        row["GTDB_novelty"] = get_gtdb_novelty(taxonomy)
        # 将GTDB_taxonomy改名为动态版本名
        if gtdb_col_name != "GTDB_taxonomy":
            row[gtdb_col_name] = row.pop("GTDB_taxonomy", "")

        mag_id = row.get("ID")
        if mag_id in seen_ids:
            output_rows = [existing for existing in output_rows if existing.get("ID") != mag_id]
        elif mag_id:
            seen_ids.add(mag_id)
        output_rows.append(row)

    output_columns = list(columns)
    for col in previous_columns:
        if col not in output_columns:
            output_columns.append(col)

    with open(args.output, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=output_columns, delimiter='\t', extrasaction='ignore')
        w.writeheader()
        for row in output_rows:
            w.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge MAG summary tables")
    parser.add_argument("--seqkit", nargs='+', required=False, help="SeqKit stats TSV files")
    parser.add_argument("--checkm", required=False, help="CheckM summary TSV file")
    parser.add_argument("--gunc", required=False, help="GUNC summary TSV file")
    parser.add_argument("--mimag", nargs='+', required=False, help="MIMAG classification TSV files")
    parser.add_argument("--park", nargs='+', required=False, help="Park score TSV files")
    parser.add_argument("--orfs", nargs='+', required=False, help="ORFs count TSV files")
    parser.add_argument("--coding-density", nargs='+', required=False, help="Coding density TSV files")
    parser.add_argument("--trnas", nargs='+', required=False, help="tRNA count TSV files")
    parser.add_argument("--rrnas", nargs='+', required=False, help="rRNA count TSV files")
    parser.add_argument("--gtdb", required=False, help="GTDB-tk merged taxonomy TSV file")
    parser.add_argument("--gtdb-log", required=False, help="GTDB-tk log file")
    parser.add_argument("--gtdb-version", required=False, help="GTDB release/version, e.g. R232")
    parser.add_argument("--16s", dest="_16s", nargs='+', required=False, help="16S BLAST taxonomy TSV files")
    parser.add_argument("--output", required=True, help="Output summary TSV file")
    parser.add_argument("--results", required=True, help="Results directory")
    parser.add_argument("--previous-summary", required=False, help="Previous MAGport_summary.tsv to merge with new results")
    args = parser.parse_args()
    main(args)
