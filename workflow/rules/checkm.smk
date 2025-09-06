# Module 2: Quality via CheckM2 (default) or CheckM1

QUALITY_DIR = get_dir("checkm", "03_quality/checkm")
ORF_DIR = get_dir("orfs", "02_genes/orfs")


rule run_checkm2:
    conda: ENV["checkm2"]
    input:
        orfs=expand(str(ORF_DIR / "{sample}.faa"), sample=SAMPLE_LIST)
    output:
        summary=QUALITY_DIR / "checkm2_summary.tsv"
    params:
        indir=ORF_DIR,
        db=str(CHECKM2_DB / "uniref100.KO.1.dmnd"),
    log:
        str(LOGS / "checkm2.log")
    threads: THREADS
    shell:
        r"""
        mkdir -p {QUALITY_DIR}
        (checkm2 predict --genes --threads {threads} \
            --input {params.indir} \
            -x .faa \
            --output-directory {QUALITY_DIR} \
            --database_path {params.db} --force) &> {log}
        mv {QUALITY_DIR}/quality_report.tsv {output.summary}
        """

rule run_checkm1:
    conda: ENV["checkm1"]
    input:
        orfs=expand(str(ORF_DIR / "{sample}.faa"), sample=SAMPLE_LIST)
    output:
        summary=QUALITY_DIR / "checkm1_summary.tsv",
    params:
        indir=ORF_DIR,
        db=CHECKM1_DB
    threads: THREADS
    shell:
        r"""
        mkdir -p {QUALITY_DIR}
        checkm lineage_wf -t {threads} -x .faa {params.indir} {QUALITY_DIR}
        checkm qa -o 2 -t {threads} --tab_table --quiet \
            --file {output.summary} \
            {QUALITY_DIR}/lineage.ms {QUALITY_DIR}
        """

# No aggregate rule; Snakefile top-level expands per-sample outputs.


"""checkm2 sample output
Name	Completeness	Contamination	Completeness_Model_Used	Translation_Table_Used	Coding_Density	Contig_N50	Average_Gene_Length	Genome_Size	GC_Content	Total_Coding_Sequences	Total_Contigs	Max_Contig_Length	Additional_Notes
IH01-17_maxbin.101_sub	62.73	8.44	Gradient Boost (General Model)	11	0.882	2030	233.5892644	1991969	0.52	2515	919	15651	None
IH01-17_maxbin.117_sub	55.82	11.31	Gradient Boost (General Model)	11	0.894	2023	232.7997242	2261022	0.55	2901	1077	6646	None
"""