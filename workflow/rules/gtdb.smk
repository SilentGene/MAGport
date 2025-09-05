# Module 8: GTDB-Tk taxonomy

GTDB_DIR = RESULTS / "gtdbtk"

rule gtdbtk_classify:
    conda: ENV["gtdbtk"]
    input:
        mag=lambda wc: SAMPLES[wc.sample],
        db_marker="resources/gtdbtk/REQUIRES_USER_DB"
    output:
        tsv=str(GTDB_DIR / "{sample}.gtdb.tsv")
    params:
        db=GTDBTK_DB
    threads: THREADS
    shell:
        r"""
        mkdir -p {GTDB_DIR}
        # Get just the filename without path
        mag_name=$(basename "{input.mag}")
        # Run GTDB-Tk classify_wf on a single genome (may be inefficient; for many MAGs, batch externally)
        gtdbtk classify_wf --genome_dir {INPUT_DIR} --out_dir {GTDB_DIR} --prefix run --cpus {threads} --data_dir {params.db} || true
        # Extract lineage for this MAG
        echo -e "lineage" > {output.tsv}
        if [ -s {GTDB_DIR}/run.bac120.summary.tsv ]; then
            awk -F '\t' -v s="$mag_name" '$1==s{{print $2}}' {GTDB_DIR}/run.bac120.summary.tsv >> {output.tsv}
        elif [ -s {GTDB_DIR}/run.ar53.summary.tsv ]; then
            awk -F '\t' -v s="$mag_name" '$1==s{{print $2}}' {GTDB_DIR}/run.ar53.summary.tsv >> {output.tsv}
        else
            echo "" >> {output.tsv}
        fi
        """

# No aggregate rule
