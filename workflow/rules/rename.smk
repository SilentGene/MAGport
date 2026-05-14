# Module: Checkpoint for dynamically renaming genomes based on GTDB-Tk classification

RENAME_DIR = OUTPUT_DIR / "00_renamed_genomes"

checkpoint rename_genomes:
    input:
        gtdb = get_dir("gtdbtk", "04_taxonomy/gtdbtk") / "gtdb.merged_summary.tsv",
        genomes = expand(GENOME_DIR / f"{{sample}}{EXT}", sample=SAMPLE_LIST)
    output:
        map_out = OUTPUT_DIR / "rename_map.tsv",
        # Directory output forces snakemake to wait until it's generated
        out_dir = directory(RENAME_DIR)
    params:
        pattern = config.get("rename_pattern", ""),
        input_dir = GENOME_DIR,
        ext = EXT
    conda: ENV["python"]
    shell:
        r"""
        python {workflow.basedir}/scripts/rename_mags.py \
            --gtdb {input.gtdb} \
            --input-dir {params.input_dir} \
            --output-dir {output.out_dir} \
            --map-out {output.map_out} \
            --pattern "{params.pattern}" \
            --ext "{params.ext}"
        """
