# Collect all per-MAG TSVs into a consolidated summary
# stats.smk: Genome_Size_bp, num_Contigs, N50, %GC, num_ambiguous_bases
# orfs.smk: num_ORFs
# checkm.smk: Completeness, Contamination
# gunc.smk: GUNC_status
# trnas.smk: num_tRNAs
# rnas.smk: num_16S_rRNAs, num_23S_rRNAs, num_5S_rRNAs
# gtdb.smk: GTDB_taxonomy
# 16s.smk: 16S_taxonomy

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
        # Gene content
        orfs=expand(get_dir("orfs", "02_genes/orfs") / "{sample}.orfs.tsv", sample=SAMPLE_LIST),
        trnas=expand(get_dir("trna", "02_genes/trna") / "{sample}.tRNA.tsv", sample=SAMPLE_LIST),
        rrnas=expand(get_dir("rrna", "02_genes/rrna") / "{sample}.rRNA.tsv", sample=SAMPLE_LIST),
        # Taxonomy
        gtdb=get_dir("gtdbtk", "04_taxonomy/gtdbtk") / "gtdb.merged_summary.tsv",
        r16s=expand(get_dir("r16s", "04_taxonomy/16S") / "{sample}.16S.tsv", sample=SAMPLE_LIST)
        # MIMAG quality
        
    output:
        tsv=SUMMARY_TSV
    params:
        result_dir=OUTPUT_DIR,
        use_checkm=USE_CHECKM
    shell:
        r"""
        python workflow/scripts/summary.py \
            --output {output.tsv} \
            --results {params.result_dir} \
            --checkm {params.use_checkm}
        """
