# Module 10: MIMAG classification

MIMAG_DIR = RESULTS / "mimag"

rule mimag_classify:
    conda: ENV["python"]
    input:
    qual=lambda wc: RESULTS / "quality" / (wc.sample + f".{ 'checkm2' if USE_CHECKM=='checkm2' else 'checkm1' }.tsv"),
    trna=lambda wc: RESULTS / "trna" / (wc.sample + ".trna.tsv"),
    rrna=lambda wc: RESULTS / "rrna" / (wc.sample + ".rrna.tsv"),
    output:
    tsv=str(MIMAG_DIR / "{sample}.mimag.tsv")
    shell:
        r"""
        mkdir -p {MIMAG_DIR}
        python workflow/scripts/mimag.py {input.qual} {input.trna} {input.rrna} {output.tsv}
        """

# No aggregate rule
