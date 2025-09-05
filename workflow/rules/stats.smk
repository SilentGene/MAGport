# Module 1: Basic statistics via SeqKit

STATS_DIR = RESULTS / "seqkit"

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
        # Use ( ) instead of {{ }} for command grouping
        (
            echo -e "mag\tfile\tformat\ttype\tnum_seqs\tsum_len\tmin\tavg\tmax\tQ1\tN50\tQ3\tGC\tNpct"
            seqkit stats -a {input.mag} | sed '1d' | awk -v OFS='\t' -v mag={wildcards.sample} '{{print mag,$0}}'
        ) > {output.tsv}
        """
