# Module 3: Park Score (Python)

PARK_DIR = get_dir("park", "03_quality/park")

rule park_score:
    conda: ENV["python"]
    input:
        stats=lambda wc: get_dir("seqkit", "01_stats/seqkit") / (wc.sample + ".seqkit.tsv"),
        checkm2=get_dir("checkm", "03_quality/checkm") / "checkm2_summary.tsv"
    output:
        tsv=str(PARK_DIR / "{sample}.park.tsv")
    shell:
        r"""
        mkdir -p {PARK_DIR}
        python workflow/scripts/park_score.py \
            {input.stats} \
            {input.checkm2} \
            {output.tsv} \
            --mag {wildcards.sample}
        """

# No aggregate rule; top-level targets are expanded in Snakefile
