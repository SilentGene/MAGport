# Module 3: Park Score (Python)

PARK_DIR = get_dir("park", "03_quality/parks_score")

rule park_score:
    conda: ENV["python"]
    input:
        stats=lambda wc: get_dir("seqkit", "01_stats/seqkit") / (wc.sample + ".seqkit.tsv"),
        checkm2=get_dir("checkm", "03_quality/checkm") / "checkm2_summary.tsv"
    output:
        tsv=str(PARK_DIR / "{sample}.parks.tsv")
    shell:
        r"""
        mkdir -p {PARK_DIR}
        python {workflow.basedir}/scripts/parks_score.py \
            {input.stats} \
            {input.checkm2} \
            {output.tsv} \
            --mag {wildcards.sample}
        """

