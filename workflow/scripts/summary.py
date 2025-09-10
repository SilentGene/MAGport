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
            --results /mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_output \
            --checkm-method checkm2
"""

class DataLoader:
    def __init__(self, args):
        self.args = args
        # 加载共享文件数据
        self.checkm_data = self._load_checkm()
        self.gunc_data = self._load_gunc()
        self.gtdb_data = self._load_gtdb()
        # 加载每个MAG的文件数据
        self.seqkit_data = self._load_multiple_files(args.seqkit, self._parse_seqkit, ".seqkit.tsv")
        self.orfs_data = self._load_multiple_files(args.orfs, self._parse_orfs, ".orfs.tsv")
        self.park_data = self._load_multiple_files(args.park, self._parse_park, ".park.tsv")
        self.mimag_data = self._load_multiple_files(args.mimag, self._parse_mimag, ".MIMAG_level.tsv")
        self.trnas_data = self._load_multiple_files(args.trnas, self._parse_trnas, ".tRNA.tsv")
        self.rrnas_data = self._load_multiple_files(args.rrnas, self._parse_rrnas, ".rRNA.tsv")
        self.s16_data = self._load_multiple_files(args._16s, self._parse_16s, ".16S.tsv")

    def _load_checkm(self):
        data = {}
        with open(self.args.checkm) as f:
            rdr = csv.DictReader(f, delimiter='\t')
            for row in rdr:
                if self.args.checkm_method == "checkm2":
                    key = row.get("Name")
                else:
                    key = row.get("Bin Id")
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
        with open(self.args.gtdb) as f:
            rdr = csv.DictReader(f, delimiter='\t')
            for row in rdr:
                genome = row.get("user_genome")
                if genome:
                    data[genome] = {"GTDB_taxonomy": row.get("classification", "")}
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
                "MAG": row[0],
                "num_contigs": row[4],
                "genome_size_bp": row[5],
                "N50": row[13],
                "GC": row[18],
                "sum_ambiguous_bases": row[19]
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
                return {"Park_Score": next(f).strip()}
        except Exception:
            return {"Park_Score": ""}

    @staticmethod
    def _parse_mimag(path):
        try:
            with open(path) as f:
                next(f)
                return {"MIMAG_level": next(f).strip()}
        except Exception:
            return {"MIMAG_level": ""}

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
                    "num_5S_rRNAs": vals[0] if len(vals) > 0 else "",
                    "num_16S_rRNAs": vals[1] if len(vals) > 1 else "",
                    "num_23S_rRNAs": vals[2] if len(vals) > 2 else ""
                }
        except Exception:
            return {
                "num_5S_rRNAs": "",
                "num_16S_rRNAs": "",
                "num_23S_rRNAs": ""
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

    def get_mag_data(self, mag, seqkit_data):
        """获取单个MAG的所有数据"""
        
        data = {}
        data.update(seqkit_data)
        data.update(self.orfs_data.get(mag, {}))
        data.update(self.checkm_data.get(mag, {}))
        data.update(self.gunc_data.get(mag, {}))
        data.update(self.park_data.get(mag, {}))
        data.update(self.mimag_data.get(mag, {}))
        data.update(self.trnas_data.get(mag, {}))
        data.update(self.rrnas_data.get(mag, {}))
        data.update(self.gtdb_data.get(mag, {}))
        data.update(self.s16_data.get(mag, {}))
        return data

def main(args):
    # 初始化数据加载器
    loader = DataLoader(args)
    
    mags = []
    with open(args.mags) as f:
        for line in f:
            mag = line.strip().split('\t')[0]
            mags.append(loader.get_mag_data(mag, loader.seqkit_data.get(mag, {"MAG": mag})))

    # 输出
    columns = [
        "ID", "num_contigs", "genome_size_bp", "N50", "GC", "sum_ambiguous_bases",
        "num_ORFs", "Completeness", "Contamination", "pass_GUNC", "Park_Score", "MIMAG_level",
        "num_tRNAs", "num_16S_rRNAs", "num_23S_rRNAs", "num_5S_rRNAs", "16S_NCBI_taxonomy", "16S_blastn_identity", "GTDB_taxonomy", "GTDB_novelty"
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

    with open(args.output, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=columns, delimiter='\t')
        w.writeheader()
        for row in mags:
            taxonomy = row.get("GTDB_taxonomy", "")
            row["GTDB_novelty"] = get_gtdb_novelty(taxonomy)
            # 将MAG字段重命名为ID
            if "MAG" in row:
                row["ID"] = row.pop("MAG")
            w.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge MAG summary tables")
    parser.add_argument("--mags", required=True, help="input_MAGs.txt file")
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
