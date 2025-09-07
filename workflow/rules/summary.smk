# Collect all per-MAG TSVs into a consolidated summary
# stats.smk: Genome_Size_bp, num_Contigs, N50, %GC, num_ambiguous_bases
# orfs.smk: num_ORFs
# checkm.smk: Completeness, Contamination
# gunc.smk: GUNC_status
# park.smk: Park_Score
# mimag.smk: MIMAG_level
# trnas.smk: num_tRNAs
# rnas.smk: num_16S_rRNAs, num_23S_rRNAs, num_5S_rRNAs
# gtdb.smk: GTDB_taxonomy
# 16s.smk: 16S_taxonomy

# output columns:
# MAG	num_contigs	genome_size_bp	N50	GC	sum_ambiguous_bases	num_ORFs	Completeness	Contamination	GUNC_status	Park_Score	MIMAG_level	num_tRNAs	num_16S_rRNAs	num_23S_rRNAs	num_5S_rRNAs	16S_taxonomy	GTDB_taxonomy

rule collect_summary:
    conda: ENV["python"]
    input:
        # Basic stats
        seqkit=expand(get_dir("seqkit", "01_stats/seqkit") / "{sample}.seqkit.tsv", sample=SAMPLE_LIST),
        # Quality assessment
        checkm2=get_dir("checkm", "03_quality/checkm") / "checkm2_summary.tsv" if USE_CHECKM == "checkm2" else [],
        checkm1=get_dir("checkm", "03_quality/checkm") / "checkm1_summary.tsv" if USE_CHECKM == "checkm1" else [],
        gunc=get_dir("gunc", "03_quality/gunc") / "GUNC_summary.tsv",
        mimag=expand(get_dir("mimag", "03_quality/mimag") / "{sample}.MIMAG_level.tsv", sample=SAMPLE_LIST),
        park=expand(get_dir("park", "03_quality/park") / "{sample}.park.tsv", sample=SAMPLE_LIST),
        # Gene content
        orfs=expand(get_dir("orfs", "02_genes/orfs") / "{sample}.orfs.tsv", sample=SAMPLE_LIST),
        trnas=expand(get_dir("trna", "02_genes/trna") / "{sample}.tRNA.tsv", sample=SAMPLE_LIST),
        rrnas=expand(get_dir("rrna", "02_genes/rrna") / "{sample}.rRNA.tsv", sample=SAMPLE_LIST),
        # Taxonomy
        gtdb=get_dir("gtdbtk", "04_taxonomy/gtdbtk") / "gtdb.merged_summary.tsv",
        r16s=expand(get_dir("r16s", "04_taxonomy/16S") / "{sample}.16S.tsv", sample=SAMPLE_LIST)
        
    output:
        tsv=SUMMARY_TSV
    params:
        result_dir=OUTPUT_DIR,
        use_checkm=USE_CHECKM,
        checkm_input=lambda w, input: input.checkm2 if USE_CHECKM == "checkm2" else input.checkm1
    shell:
        r"""
        python workflow/scripts/summary.py \
            --seqkit {input.seqkit} \
            --checkm {params.checkm_input} \
            --gunc {input.gunc} \
            --mimag {input.mimag} \
            --park {input.park} \
            --orfs {input.orfs} \
            --trnas {input.trnas} \
            --rrnas {input.rrnas} \
            --gtdb {input.gtdb} \
            --16s {input.r16s} \
            --output {output.tsv} \
            --results {params.result_dir} \
            --checkm-method {params.use_checkm}
        """
