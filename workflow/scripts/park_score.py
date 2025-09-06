from __future__ import annotations

from pathlib import Path
import csv
import argparse

# Usage: python park_score.py stats.tsv quality.tsv out.tsv --mag MAG1 --method checkm2

"""
Compute Park score:
Score = Completeness - (5 * Contamination) - (5 * num_contigs / 100) - (5 * amb_bases / 100000)
Inputs: join from stats and checkm outputs.

Completeness: checkm2 column 2, checkm1 column 6
Contamination: checkm2 column 3, checkm1 column 7
num_contigs: seqkit column 5
amb_bases: seqkit column 20
"""

"""stats_tsv sample
MAG	file	format	type	num_seqs	sum_len	min_len	avg_len	max_len	Q1	Q2	Q3	sum_gap	N50	N50_num	Q20(%)	Q30(%)	AvgQual	GC(%)	sum_n
MAG1	/mnt/hpccs01/work/microbiome/users/heyu/MAGport/test/test_input_MAGs/MAG1.fna	FASTA	DNA	28	903669	1924	32273.9	189547	5686	14622	43754	0	68826	4	0	0	0	38.27	0
"""

"""checkm2 sample
Name	Completeness	Contamination	Completeness_Model_Used	Additional_Notes
GCF_024346955.1_vmangrovi	100	0	Neural Network (Specific Model)	None
MAG1	93.95	0	Gradient Boost (General Model)	None
MAG209	91.26	1.88	Gradient Boost (General Model)	None
"""

"""checkm1 sample
Bin Id	Marker lineage	# genomes	# markers	# marker sets	Completeness	Contamination	Strain heterogeneity	Genome size (bp)	# ambiguous bases	# scaffolds	# contigs	N50 (scaffolds)	N50 (contigs)	Mean scaffold length (bp)	Mean contig length (bp)	Longest scaffold (bp)	Longest contig (bp)	GC	GC std (scaffolds > 1kbp)	Coding density	Translation table	# predicted genes	0	1	2	3	4	5+
Methanoperedens	p__Euryarchaeota (UID49)	95	228	153	99.67	0.65	0	3117687	1	60	60	68150	68150	51961	51961	212233	212233	43.3	1.53	88.78	11	3367	1	226	1	0	0	0
v-ANME2d	p__Euryarchaeota (UID49)	95	228	153	99.67	0.65	0	3042452	0	73	73	64364	64364	41677	41677	173556	173556	43.3	1.39	88.82	11	3282	1	226	1	0	0	0
"""

def main(stats_tsv: Path, quality_tsv: Path, out_tsv: Path, mag_name: str, method: str) -> None:
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

        # park_score.py (rewritten per user prompt)


def parse_seqkit(stats_tsv: Path) -> tuple[int, int]:
    """
    Extract num_contigs (column 5) and amb_bases (column 20) from seqkit TSV.
    """
    with open(stats_tsv) as f:
        rdr = csv.reader(f, delimiter='\t')
        header = next(rdr)
        row = next(rdr)
        num_contigs = int(row[4]) if len(row) > 4 else 0
        amb_bases = int(row[19]) if len(row) > 19 else 0
        print(f"seqkit stats: num_contigs={num_contigs}, amb_bases={amb_bases}")
    return num_contigs, amb_bases

def parse_checkm(quality_tsv: Path, mag_name: str, method: str) -> tuple[float, float]:
    """
    Extract Completeness and Contamination from checkm output.
    checkm2: columns 2,3; checkm1: columns 6,7
    """
    with open(quality_tsv) as f:
        rdr = csv.reader(f, delimiter='\t')
        header = next(rdr)
        for row in rdr:
            if method == "checkm2":
                # Completeness: col 2, Contamination: col 3
                if row[0] == mag_name and len(row) > 3:
                    comp = float(row[1])
                    cont = float(row[2])
                    print(f"quality for {mag_name}: comp={comp}, cont={cont}")
                    return comp, cont
            else:
                # Completeness: col 6, Contamination: col 7
                if row[0] == mag_name and len(row) > 7:
                    comp = float(row[5])
                    cont = float(row[6])
                    print(f"quality for {mag_name}: comp={comp}, cont={cont}")
                    return comp, cont
    return 0.0, 0.0

def main(stats_tsv: Path, quality_tsv: Path, out_tsv: Path, mag_name: str, method: str) -> None:
    num_contigs, amb_bases = parse_seqkit(stats_tsv)
    comp, cont = parse_checkm(quality_tsv, mag_name, method)
    score = comp - (5 * cont) - (5 * num_contigs / 100) - (5 * amb_bases / 100000)
    print(f"Park score for {mag_name}: {score:.3f}")
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_tsv, 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(["park_score"])
        w.writerow([f"{score:.3f}"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Park score for a MAG")
    parser.add_argument("stats_tsv", type=Path, help="Seqkit stats TSV file")
    parser.add_argument("quality_tsv", type=Path, help="CheckM quality TSV file")
    parser.add_argument("out_tsv", type=Path, help="Output TSV file")
    parser.add_argument("--mag", required=True, help="MAG name to process")
    parser.add_argument("--method", choices=["checkm1", "checkm2"], default="checkm2", help="CheckM version used")
    args = parser.parse_args()
    main(args.stats_tsv, args.quality_tsv, args.out_tsv, args.mag, args.method)
