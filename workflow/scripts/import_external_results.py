import argparse
import csv
from pathlib import Path


GENOME_COLUMNS = ("user_genome", "genome", "name")
TAXONOMY_COLUMNS = ("classification", "taxonomy", "gtdb")


def find_column(fieldnames, candidates, label):
    lookup = {name.lower(): name for name in fieldnames or []}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    raise SystemExit(
        f"Could not find {label} column. Expected one of: {', '.join(candidates)}"
    )


def import_taxonomy(input_path, output_path):
    with open(input_path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source, delimiter="\t")
        genome_col = find_column(reader.fieldnames, GENOME_COLUMNS, "genome name")
        taxonomy_col = find_column(reader.fieldnames, TAXONOMY_COLUMNS, "taxonomy")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as dest:
            writer = csv.DictWriter(dest, fieldnames=["user_genome", "classification"], delimiter="\t")
            writer.writeheader()
            for row in reader:
                genome = (row.get(genome_col) or "").strip()
                if genome:
                    writer.writerow({
                        "user_genome": genome,
                        "classification": (row.get(taxonomy_col) or "").strip(),
                    })


def import_quality(input_path, output_path):
    with open(input_path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source, delimiter="\t")
        genome_col = find_column(reader.fieldnames, GENOME_COLUMNS, "genome name")
        completeness_col = find_column(reader.fieldnames, ("Completeness",), "Completeness")
        contamination_col = find_column(reader.fieldnames, ("Contamination",), "Contamination")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as dest:
            writer = csv.DictWriter(dest, fieldnames=["Name", "Completeness", "Contamination"], delimiter="\t")
            writer.writeheader()
            for row in reader:
                genome = (row.get(genome_col) or "").strip()
                if genome:
                    writer.writerow({
                        "Name": genome,
                        "Completeness": (row.get(completeness_col) or "").strip(),
                        "Contamination": (row.get(contamination_col) or "").strip(),
                    })


def main():
    parser = argparse.ArgumentParser(description="Normalize user-provided MAGport TSV inputs")
    parser.add_argument("--kind", choices=("taxonomy", "quality"), required=True)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.kind == "taxonomy":
        import_taxonomy(args.input, args.output)
    else:
        import_quality(args.input, args.output)


if __name__ == "__main__":
    main()
