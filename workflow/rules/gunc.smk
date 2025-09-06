# Module 4: GUNC chimerism

GUNC_DIR = get_dir("gunc", "03_quality/gunc")
ORF_DIR = get_dir("orfs", "02_genes/orfs")

rule gunc_run_all:
    conda: ENV["gunc"]
    input:
        orfs=expand(str(ORF_DIR / "{sample}.faa"), sample=SAMPLE_LIST)
    output:
        summary=GUNC_DIR / "GUNC_summary.tsv",
        diamond=GUNC_DIR / "diamond_output"
    params:
        indir=ORF_DIR,
        db=str(GUNC_DB / "gunc_db_gtdb95.dmnd")
    log:
        str(LOGS / "gunc.log")
    threads: THREADS
    shell:
        r"""
        mkdir -p {GUNC_DIR}
        (gunc run --gene_calls \
            --input_dir {params.indir} \
            --file_suffix .faa \
            --db_file {params.db} \
            --threads {threads} \
            --out_dir {GUNC_DIR}) &> {log}

        # rename GUNC result
        mv {GUNC_DIR}/GUNC.gtdb_95.maxCSS_level.tsv {output.summary}
        mv {GUNC_DIR}/diamond_output {output.diamond}
        """

# No aggregate rule; top-level handles targets

"""Gunc result sample
genome	n_genes_called	n_genes_mapped	n_contigs	taxonomic_level	proportion_genes_retained_in_major_clades	genes_retained_index	clade_separation_score	contamination_portion	n_effective_surplus_clades	mean_hit_identity	reference_representation_score	pass.GUNC
Abisko_HL_MAG1	1825	1709	302	kingdom	1	0.94	0.22	0.05	0.1	0.73	0.68	TRUE
Abisko_HL_MAG10	2870	2641	32	kingdom	1	0.92	0.08	0.07	0.15	0.75	0.69	TRUE

"""