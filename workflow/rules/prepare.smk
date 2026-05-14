# Module 0: Prepare Genomes

GENOME_DIR = OUTPUT_DIR / "00_input_genomes"

rule prepare_genomes:
    input:
        mag=lambda wc: SAMPLES[wc.sample]
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
