# Module 10: MIMAG classification

MIMAG_DIR = get_dir("mimag", "03_quality/mimag")

rule mimag_classify:
    conda: ENV["python"]
    input:
        checkm2=get_dir("checkm", "03_quality/checkm") / "checkm2_summary.tsv",
        trna=lambda wc: get_dir("trna", "02_genes/trna") / (wc.sample + ".tRNA.tsv"),
        rrna=lambda wc: get_dir("rrna", "02_genes/rrna") / (wc.sample + ".rRNA.tsv")
    output:
        tsv=str(MIMAG_DIR / "{sample}.MIMAG_level.tsv")
    shell:
        r"""
        mkdir -p {MIMAG_DIR}
        python workflow/scripts/mimag.py \
            {input.checkm2} \
            {input.trna} \
            {input.rrna} \
            {output.tsv} \
            --mag {wildcards.sample}
        """

# No aggregate rule
