# Module 2: Quality via CheckM2

QUALITY_DIR = get_dir("checkm", "03_quality/checkm")
ORF_DIR = get_dir("orfs", "02_genes/orfs")


if INPUT_QUALITY:
    rule import_checkm2_quality:
        conda: ENV["python"]
        input:
            quality=INPUT_QUALITY
        output:
            summary=QUALITY_DIR / "checkm2_summary.tsv"
        benchmark:
            str(BENCHMARKS / "checkm2.benchmark.txt")
        shell:
            r"""
            python {workflow.basedir}/scripts/import_external_results.py \
                --kind quality \
                --input {input.quality} \
                --output {output.summary}
            """
else:
    rule run_checkm2:
        conda: ENV["checkm2"]
        input:
            orfs=lambda wc: expand(str(ORF_DIR / "faa" / "{sample}.faa"), sample=get_active_samples(wc))
        output:
            summary=QUALITY_DIR / "checkm2_summary.tsv"
        benchmark:
            str(BENCHMARKS / "checkm2.benchmark.txt")
        params:
            indir=ORF_DIR / "faa",
            db=str(CHECKM2_DB / "uniref100.KO.1.dmnd"),
        log:
            str(LOGS / "checkm2.log")
        threads: min(config.get("max_threads", {}).get("checkm2", 8), THREADS)
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



# No aggregate rule; Snakefile top-level expands per-sample outputs.


"""checkm2 sample output
Name	Completeness	Contamination	Completeness_Model_Used	Translation_Table_Used	Coding_Density	Contig_N50	Average_Gene_Length	Genome_Size	GC_Content	Total_Coding_Sequences	Total_Contigs	Max_Contig_Length	Additional_Notes
IH01-17_maxbin.101_sub	62.73	8.44	Gradient Boost (General Model)	11	0.882	2030	233.5892644	1991969	0.52	2515	919	15651	None
IH01-17_maxbin.117_sub	55.82	11.31	Gradient Boost (General Model)	11	0.894	2023	232.7997242	2261022	0.55	2901	1077	6646	None
"""
