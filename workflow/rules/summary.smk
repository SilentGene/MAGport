# Collect all per-MAG TSVs into a consolidated summary
# stats.smk: Genome_Size_bp, num_Contigs, N50, %GC, num_ambiguous_bases
# orfs.smk: num_ORFs
# checkm.smk: Completeness, Contamination
# gunc.smk: GUNC_status
# park.smk: Park_Score
# mimag.smk: MIMAG_level
# trnas.smk: num_tRNAs
# rnas.smk: 16S, 23S, 5S
# gtdb.smk: GTDB_taxonomy
# 16s.smk: 16S_taxonomy

# output columns:
# MAG	num_contigs	genome_size_bp	N50	GC	Ambiguous_bases	num_ORFs	Completeness	Contamination	GUNC_status	Park_Score	MIMAG_level	num_tRNAs	16S	23S	5S	16S_taxonomy	GTDB_taxonomy

rule collect_summary:
    conda: ENV["python"]
    input:
        # Basic stats
        seqkit=lambda wc: expand(get_dir("seqkit", "01_stats/seqkit") / "{sample}.seqkit.tsv", sample=get_active_samples(wc)),
        # Quality assessment
        checkm2=get_dir("checkm", "03_quality/checkm") / "checkm2_summary.tsv",
        gunc=get_dir("gunc", "03_quality/gunc") / "GUNC_summary.tsv",
        mimag=lambda wc: expand(get_dir("mimag", "03_quality/mimag") / "{sample}.MIMAG_level.tsv", sample=get_active_samples(wc)),
        park=lambda wc: expand(get_dir("park", "03_quality/parks_score") / "{sample}.parks.tsv", sample=get_active_samples(wc)),
        # Gene content
        orfs=lambda wc: expand(get_dir("orfs", "02_genes/orfs") / "{sample}.orfs.tsv", sample=get_active_samples(wc)),
        trnas=lambda wc: expand(get_dir("trna", "02_genes/trna") / "{sample}.tRNA.tsv", sample=get_active_samples(wc)),
        rrnas=lambda wc: expand(get_dir("rrna", "02_genes/rrna") / "{sample}.rRNA.tsv", sample=get_active_samples(wc)),
        # Taxonomy
        gtdb=get_dir("gtdbtk", "04_taxonomy/gtdbtk") / "gtdb.merged_summary.tsv",
        gtdb_log=get_dir("logs", "logs") / "gtdbtk.log",
        r16s=lambda wc: expand(get_dir("r16s", "04_taxonomy/16S") / "{sample}.16S.tsv", sample=get_active_samples(wc))
        
    output:
        tsv=SUMMARY_TSV
    params:
        result_dir=OUTPUT_DIR
    shell:
        r"""
        python {workflow.basedir}/scripts/summary.py \
            --seqkit {input.seqkit} \
            --checkm {input.checkm2} \
            --gunc {input.gunc} \
            --mimag {input.mimag} \
            --park {input.park} \
            --orfs {input.orfs} \
            --trnas {input.trnas} \
            --rrnas {input.rrnas} \
            --gtdb {input.gtdb} \
            --gtdb-log {input.gtdb_log} \
            --16s {input.r16s} \
            --output {output.tsv} \
            --results {params.result_dir}
        """
