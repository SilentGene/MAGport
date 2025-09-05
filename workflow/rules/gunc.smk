# Module 4: GUNC chimerism

GUNC_DIR = RESULTS / "gunc"

rule gunc_run:
    conda: ENV["gunc"]
    input:
        mag=lambda wc: SAMPLES[wc.sample],
        db=GUNC_DB
    output:
        tsv=str(GUNC_DIR / "{sample}.gunc.tsv")
    params:
        db=GUNC_DB
    threads: THREADS
    shell:
        r"""
        mkdir -p {GUNC_DIR}
    gunc run --threads {threads} --db {params.db} --genomes {input.mag} --out {GUNC_DIR} --prefix {wildcards.sample}
        # Convert summary to per-MAG TSV (placeholder)
        echo -e "gunc_score\tgunc_pass" > {output.tsv}
        echo -e "\t" >> {output.tsv}
        """

# No aggregate rule; top-level handles targets
