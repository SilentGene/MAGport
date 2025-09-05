# Module 3: Park Score (Python)

PARK_DIR = RESULTS / "park"

rule park_score:
    conda: ENV["python"]
    input:
        stats=lambda wc: RESULTS / "seqkit" / (wc.sample + ".seqkit.tsv"),
        qual=lambda wc: RESULTS / "quality" / (wc.sample + f".{ 'checkm2' if USE_CHECKM=='checkm2' else 'checkm1' }.tsv"),
    output:
        tsv=str(PARK_DIR / "{sample}.park.tsv")
    shell:
        r"""
        mkdir -p {PARK_DIR}
        python workflow/scripts/park_score.py {input.stats} {input.qual} {output.tsv}
        """

# No aggregate rule; top-level targets are expanded in Snakefile
