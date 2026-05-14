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

def get_summary_inputs(wildcards):
    inputs = {}
    active_samples = get_active_samples(wildcards)
    
    if "stats" in SELECTED:
        inputs["seqkit"] = expand(get_dir("seqkit", "01_stats/seqkit") / "{sample}.seqkit.tsv", sample=active_samples)
    if "quality" in SELECTED:
        inputs["checkm2"] = get_dir("checkm", "03_quality/checkm") / "checkm2_summary.tsv"
    if "gunc" in SELECTED:
        inputs["gunc"] = get_dir("gunc", "03_quality/gunc") / "GUNC_summary.tsv"
    if "mimag" in SELECTED:
        inputs["mimag"] = expand(get_dir("mimag", "03_quality/mimag") / "{sample}.MIMAG_level.tsv", sample=active_samples)
    if "park" in SELECTED:
        inputs["park"] = expand(get_dir("park", "03_quality/parks_score") / "{sample}.parks.tsv", sample=active_samples)
    if "orfs" in SELECTED:
        inputs["orfs"] = expand(get_dir("orfs", "02_genes/orfs") / "{sample}.orfs.tsv", sample=active_samples)
    if "trna" in SELECTED:
        inputs["trnas"] = expand(get_dir("trna", "02_genes/trna") / "{sample}.tRNA.tsv", sample=active_samples)
    if "rrna" in SELECTED:
        inputs["rrnas"] = expand(get_dir("rrna", "02_genes/rrna") / "{sample}.rRNA.tsv", sample=active_samples)
    if "gtdb" in SELECTED:
        inputs["gtdb"] = get_dir("gtdbtk", "04_taxonomy/gtdbtk") / "gtdb.merged_summary.tsv"
        inputs["gtdb_log"] = get_dir("logs", "logs") / "gtdbtk.log"
    if "rrna16S" in SELECTED:
        inputs["r16s"] = expand(get_dir("r16s", "04_taxonomy/16S") / "{sample}.16S.tsv", sample=active_samples)
    
    return inputs

rule collect_summary:
    conda: ENV["python"]
    input:
        unpack(get_summary_inputs)
    output:
        tsv=SUMMARY_TSV
    params:
        result_dir=OUTPUT_DIR,
        args=lambda wc, input: " ".join([
            f"--seqkit {input.seqkit}" if hasattr(input, "seqkit") else "",
            f"--checkm {input.checkm2}" if hasattr(input, "checkm2") else "",
            f"--gunc {input.gunc}" if hasattr(input, "gunc") else "",
            f"--mimag {input.mimag}" if hasattr(input, "mimag") else "",
            f"--park {input.park}" if hasattr(input, "park") else "",
            f"--orfs {input.orfs}" if hasattr(input, "orfs") else "",
            f"--trnas {input.trnas}" if hasattr(input, "trnas") else "",
            f"--rrnas {input.rrnas}" if hasattr(input, "rrnas") else "",
            f"--gtdb {input.gtdb}" if hasattr(input, "gtdb") else "",
            f"--gtdb-log {input.gtdb_log}" if hasattr(input, "gtdb_log") else "",
            f"--16s {input.r16s}" if hasattr(input, "r16s") else "",
        ])
    shell:
        r"""
        python {workflow.basedir}/scripts/summary.py \
            {params.args} \
            --output {output.tsv} \
            --results {params.result_dir}
        """
