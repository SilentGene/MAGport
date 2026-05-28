#!/usr/bin/env python3

import argparse
import csv
import re
from pathlib import Path


FIELDNAMES = [
    "gene_id",
    "contig_id",
    "genome_id",
    "nt_len",
    "aa_len",
    "order_in_contig",
]


def parse_fasta_lengths(path):
    lengths = {}
    current_id = None
    current_gene_id = None
    chunks = []

    def store_current():
        if current_id is None:
            return
        sequence = "".join(chunks).replace("*", "")
        lengths[current_id] = len(sequence)
        if current_gene_id is not None:
            lengths[current_gene_id] = len(sequence)

    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                store_current()
                header = line[1:]
                current_id = header.split()[0]
                id_match = re.search(r"\bID=([^;\s]+)", header)
                current_gene_id = id_match.group(1) if id_match else None
                chunks = []
            else:
                chunks.append(line)

    store_current()
    return lengths


def parse_attributes(attributes):
    parsed = {}
    for item in attributes.rstrip(";").split(";"):
        if not item or "=" not in item:
            continue
        key, value = item.split("=", 1)
        parsed[key] = value
    return parsed


def gene_suffix(gene_id):
    match = re.search(r"_(\d+)$", gene_id)
    if match:
        return match.group(1)
    return gene_id.rsplit("_", 1)[-1]


def matching_faa(gff_path, faa_paths):
    stem = gff_path.stem
    match = faa_paths.get(stem)
    if match is None:
        raise FileNotFoundError(f"No matching FAA file found for {gff_path}")
    return match


def parse_gff(gff_path, faa_lengths):
    genome_id = gff_path.stem

    with open(gff_path, "r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue

            parts = line.rstrip("\n").split("\t")
            if len(parts) != 9 or parts[2] != "CDS":
                continue

            contig_id = parts[0]
            start = int(parts[3])
            end = int(parts[4])
            attributes = parse_attributes(parts[8])
            prodigal_id = attributes.get("ID")
            if not prodigal_id:
                raise ValueError(f"Missing ID attribute in {gff_path}: {line.rstrip()}")

            order_in_contig = gene_suffix(prodigal_id)
            gene_id = f"{contig_id}_{order_in_contig}"
            aa_key = gene_id
            aa_len = faa_lengths.get(prodigal_id, faa_lengths.get(aa_key))
            if aa_len is None:
                raise ValueError(f"No amino acid sequence found for {aa_key} in {genome_id}")

            yield {
                "gene_id": gene_id,
                "contig_id": contig_id,
                "genome_id": genome_id,
                "nt_len": abs(end - start) + 1,
                "aa_len": aa_len,
                "order_in_contig": order_in_contig,
            }


def write_gene_info(gff_paths, faa_paths, output):
    faa_by_stem = {path.stem: path for path in faa_paths}
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()

        for gff_path in sorted(gff_paths):
            faa_path = matching_faa(gff_path, faa_by_stem)
            faa_lengths = parse_fasta_lengths(faa_path)
            for row in parse_gff(gff_path, faa_lengths):
                writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate Prodigal GFF gene metadata into one TSV."
    )
    parser.add_argument("--gff", nargs="+", required=True, type=Path)
    parser.add_argument("--faa", nargs="+", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    write_gene_info(args.gff, args.faa, args.output)


if __name__ == "__main__":
    main()
