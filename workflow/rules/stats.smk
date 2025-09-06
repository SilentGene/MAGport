# Module 1: Basic statistics via SeqKit

STATS_DIR = get_dir("seqkit", "01_stats/seqkit")

rule stats_seqkit:
    conda: ENV["seqkit"]
    input:
        mag=lambda wc: SAMPLES[wc.sample]
    output:
        tsv=str(STATS_DIR / "{sample}.seqkit.tsv")
    threads: 1
    shell:
        r"""
        mkdir -p {STATS_DIR}
        (
            seqkit stats -a {input.mag} -T | awk -v OFS='\t' -v mag={wildcards.sample} 'NR==1 {{print "MAG",$0}}; NR>1 {{print mag,$0}}'
        ) > {output.tsv}
        """
