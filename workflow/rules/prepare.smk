# Module 0: Prepare Genomes

GENOME_DIR = OUTPUT_DIR / "00_input_genomes"

rule check_contig_duplicates:
    input:
        mags=list(SAMPLES.values())
    output:
        checked=temp(OUTPUT_DIR / "00_input_genomes" / ".contig_check_done")
    run:
        import gzip
        import sys

        def get_contig_names(fasta_path):
            is_gzip = fasta_path.endswith('.gz')
            open_func = gzip.open if is_gzip else open
            mode = 'rt' if is_gzip else 'r'
            contigs = []
            try:
                with open_func(fasta_path, mode, encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if line.startswith(">"):
                            contig = line[1:].strip().split()[0]
                            contigs.append(contig)
            except Exception:
                pass
            return contigs

        contig_to_genomes = {}
        for sample_name, filepath in SAMPLES.items():
            contigs = get_contig_names(filepath)
            for contig in contigs:
                if contig not in contig_to_genomes:
                    contig_to_genomes[contig] = set()
                contig_to_genomes[contig].add(sample_name)

        duplicates = {}
        for contig, genomes in contig_to_genomes.items():
            if len(genomes) > 1:
                duplicates[contig] = sorted(list(genomes))

        if duplicates:
            print("\n" + "="*80)
            print("[MAGport Error] Duplicate contig names detected across different genomes!")
            for contig, genomes in sorted(duplicates.items()):
                if len(genomes) == 2:
                    genomes_phrase = f"'{genomes[0]}' and '{genomes[1]}'"
                else:
                    genomes_phrase = ", ".join(f"'{g}'" for g in genomes[:-1]) + f", and '{genomes[-1]}'"
                print(f"We detected that contig '{contig}' is present in both genome {genomes_phrase}. Please rename your contigs to avoid conflict.")
            print("="*80 + "\n")
            sys.exit(1)

        with open(output.checked, "w") as f:
            f.write("OK")

rule prepare_genomes:
    input:
        mag=lambda wc: SAMPLES[wc.sample],
        checked=OUTPUT_DIR / "00_input_genomes" / ".contig_check_done"
    output:
        mag=GENOME_DIR / f"{{sample}}{EXT}"
    run:
        import os
        import shutil
        dest = output.mag
        src = input.mag
        dest_dir = os.path.dirname(dest)
        os.makedirs(dest_dir, exist_ok=True)
        if not os.path.exists(dest):
            try:
                os.symlink(src, dest)
            except OSError:
                shutil.copy2(src, dest)
