import argparse
import csv
from pathlib import Path


def parse_cds_bp(gff_path: Path) -> int:
    cds_bp = 0
    with open(gff_path, encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 5 or fields[2] != "CDS":
                continue
            try:
                start = int(fields[3])
                end = int(fields[4])
            except ValueError:
                continue
            cds_bp += abs(end - start) + 1
    return cds_bp


def parse_genome_bp(seqkit_tsv: Path) -> int:
    with open(seqkit_tsv, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            value = row.get("sum_len")
            if value:
                return int(value.replace(",", ""))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Calculate coding density from Prodigal GFF and seqkit stats")
    parser.add_argument("--gff", required=True, type=Path)
    parser.add_argument("--seqkit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    cds_bp = parse_cds_bp(args.gff)
    genome_bp = parse_genome_bp(args.seqkit)
    coding_density = (cds_bp / genome_bp * 100) if genome_bp else 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["coding_density", "cds_bp", "genome_bp"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerow({
            "coding_density": f"{coding_density:.2f}",
            "cds_bp": cds_bp,
            "genome_bp": genome_bp,
        })


if __name__ == "__main__":
    main()
