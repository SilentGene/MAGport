import argparse
import csv
import os
import re
import shutil
from pathlib import Path

def parse_taxonomy(taxonomy_str):
    """
    Parses GTDB taxonomy string into a dictionary.
    Example: d__Archaea;p__Thermoproteota;...
    Returns {'domain': 'Archaea', 'phylum': 'Thermoproteota', ...}
    """
    ranks = {
        'd': 'domain', 'p': 'phylum', 'c': 'class', 'o': 'order',
        'f': 'family', 'g': 'genus', 's': 'species'
    }
    parsed = {v: "" for v in ranks.values()}
    if taxonomy_str.startswith("Unclassified Bacteria"):
        parsed['unclassified'] = 'UncBac'
        return parsed
    elif taxonomy_str.startswith("Unclassified Archaea"):
        parsed['unclassified'] = 'UncArc'
        return parsed

    fields = taxonomy_str.split(';')
    for field in fields:
        if len(field) > 3 and field[1:3] == '__':
            prefix = field[0]
            if prefix in ranks:
                val = field[3:]
                parsed[ranks[prefix]] = val
    return parsed

def get_level_abbr(level):
    """Returns the single letter abbreviation for novLevel."""
    mapping = {
        'domain': 'D', 'phylum': 'P', 'class': 'C', 'order': 'O',
        'family': 'F', 'genus': 'G', 'species': 'S'
    }
    return mapping.get(level.lower(), 'Level')

def resolve_pattern(pattern, tax_dict, increnum):
    """
    Resolves the rename pattern for a specific MAG.
    Replaces [taxonomy_levelX] and [increnum].
    """
    if 'unclassified' in tax_dict:
        # All [taxonomy_levelX] become UncBac or UncArc
        def repl_unclass(match):
            return tax_dict['unclassified']
        resolved = re.sub(r'\[([a-zA-Z]+)(\d*)\]', repl_unclass, pattern)
    else:
        def repl_tax(match):
            level = match.group(1).lower()
            num_chars = match.group(2)
            if level == 'increnum':
                return str(increnum)
            
            val = tax_dict.get(level, "")
            if not val:
                val = f"nov{get_level_abbr(level)}"
            
            if num_chars:
                val = val[:int(num_chars)]
            return val
            
        resolved = re.sub(r'\[([a-zA-Z]+)(\d*)\]', repl_tax, pattern)
        
    resolved = resolved.replace('[increnum]', str(increnum))
    return resolved

def main():
    parser = argparse.ArgumentParser(description="Rename genomes based on GTDB classification")
    parser.add_argument("--gtdb", required=True, help="GTDB-Tk merged summary TSV")
    parser.add_argument("--input-dir", required=True, help="Input directory containing original genomes")
    parser.add_argument("--output-dir", required=True, help="Output directory for renamed genomes")
    parser.add_argument("--map-out", required=True, help="Output mapping TSV file")
    parser.add_argument("--pattern", required=True, help="Rename pattern")
    parser.add_argument("--ext", required=True, help="File extension (e.g. .fasta)")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read GTDB summary
    mags_data = []
    header = []
    with open(args.gtdb, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        try:
            header = next(reader)
        except StopIteration:
            pass
        for row in reader:
            if not row:
                continue
            mag = row[0]
            classification = row[1] if len(row) > 1 else ""
            mags_data.append({'row': row, 'mag': mag, 'classification': classification})
            
    # Sort by classification
    mags_data.sort(key=lambda x: x['classification'])
    
    # Add ID_new to header if not present
    if header and 'ID_new' not in header:
        header.append('ID_new')
        
    id_new_idx = header.index('ID_new') if 'ID_new' in header else len(header) - 1

    mapping = []
    increnum = 1
    
    with open(args.gtdb + ".tmp", 'w', encoding='utf-8', newline='') as f_out:
        writer = csv.writer(f_out, delimiter='\t')
        if header:
            writer.writerow(header)
            
        for item in mags_data:
            tax_dict = parse_taxonomy(item['classification'])
            new_name = resolve_pattern(args.pattern, tax_dict, increnum)
            
            # Map extensions
            old_file = input_dir / f"{item['mag']}{args.ext}"
            new_file = output_dir / f"{new_name}{args.ext}"
            
            if not old_file.exists() and item['mag'].endswith('.'):
                # Fallback for IDs with trailing dot (caused by previous bug)
                alt_mag = item['mag'][:-1]
                alt_file = input_dir / f"{alt_mag}{args.ext}"
                if alt_file.exists():
                    old_file = alt_file

            if old_file.exists():
                if not new_file.exists():
                    shutil.copy2(old_file, new_file)
            
            mapping.append((item['mag'], new_name))
            
            # Update GTDB row
            row = item['row']
            while len(row) <= id_new_idx:
                row.append("")
            row[id_new_idx] = new_name
            writer.writerow(row)
            
            increnum += 1
            
    # Replace original GTDB summary with updated one
    shutil.move(args.gtdb + ".tmp", args.gtdb)
    
    # Check if there are any MAGs in input_dir that were NOT in GTDB summary
    # (e.g. failed GTDB). They should also be copied/linked over to avoid breaking the pipeline?
    # Actually GTDB runs on all genomes. If a genome fails GTDB, it might not be in the summary.
    # To be safe, we check all genomes in input_dir.
    gtdb_mags = {m['mag'] for m in mags_data}
    for file_path in input_dir.glob(f"*{args.ext}"):
        mag = file_path.name
        if mag.endswith(args.ext):
            mag = mag[:-len(args.ext)]
            
        if mag in gtdb_mags or (mag + ".") in gtdb_mags:
            continue
            
        new_name = f"Unclassified_MAG_{increnum}"
        mapping.append((mag, new_name))
        
        new_file = output_dir / f"{new_name}{args.ext}"
        if not new_file.exists():
            shutil.copy2(file_path, new_file)
        increnum += 1

    # Write mapping file
    with open(args.map_out, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["original_id", "new_id"])
        for old_id, new_id in mapping:
            writer.writerow([old_id, new_id])

if __name__ == "__main__":
    main()
