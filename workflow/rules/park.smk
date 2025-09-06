# Module 3: Park Score (Python)

PARK_DIR = get_dir("park", "03_quality/park")

rule park_score:
    conda: ENV["python"]
    input:
        stats=lambda wc: get_dir("seqkit", "01_stats/seqkit") / (wc.sample + ".seqkit.tsv"),
        checkm2=get_dir("checkm", "03_quality/checkm") / "checkm2_summary.tsv" if USE_CHECKM == "checkm2" else [],
        checkm1=get_dir("checkm", "03_quality/checkm") / "checkm1_summary.tsv" if USE_CHECKM == "checkm1" else []
    output:
        tsv=str(PARK_DIR / "{sample}.park.tsv")
    params:
        quality_input=lambda wildcards, input: input.checkm2 if USE_CHECKM == "checkm2" else input.checkm1
    shell:
        r"""
        mkdir -p {PARK_DIR}
        python workflow/scripts/park_score.py \
            {input.stats} \
            {params.quality_input} \
            {output.tsv} \
            --mag {wildcards.sample} \
            --method {USE_CHECKM}
        """

# No aggregate rule; top-level targets are expanded in Snakefile
