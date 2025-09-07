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

"""sample output
MAG	file	format	type	num_seqs	sum_len	min_len	avg_len	max_len	Q1	Q2	Q3	sum_gap	N50	N50_num	Q20(%)	Q30(%)	AvgQual	GC(%)	sum_n
MAG1	test_input_MAGs/MAG1.fna	FASTA	DNA	28	903669	1924	32273.9	189547	5686	14622	43754	0	68826	4	0	0	0	38.27	0
"""