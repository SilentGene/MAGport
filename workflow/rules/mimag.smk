# Module 10: MIMAG classification

MIMAG_DIR = get_dir("mimag", "03_quality/mimag")

rule mimag_classify:
    conda: ENV["python"]
    input:
        checkm2=get_dir("checkm", "03_quality/checkm") / "checkm2_summary.tsv" if USE_CHECKM == "checkm2" else [],
        checkm1=get_dir("checkm", "03_quality/checkm") / "checkm1_summary.tsv" if USE_CHECKM == "checkm1" else [],
        trna=lambda wc: get_dir("trna", "02_genes/trna") / (wc.sample + ".tRNA.tsv"),
        rrna=lambda wc: get_dir("rrna", "02_genes/rrna") / (wc.sample + ".rRNA.tsv")
    output:
        tsv=str(MIMAG_DIR / "{sample}.MIMAG_level.tsv")
    params:
        quality_input=lambda wildcards, input: input.checkm2 if USE_CHECKM == "checkm2" else input.checkm1
    shell:
        r"""
        mkdir -p {MIMAG_DIR}
        python workflow/scripts/mimag.py \
            {params.quality_input} \
            {input.trna} \
            {input.rrna} \
            {output.tsv} \
            --mag {wildcards.sample} \
            --method {USE_CHECKM}
        """

# No aggregate rule
