# Module 8: GTDB-Tk taxonomy

GTDB_DIR = get_dir("gtdbtk", "04_taxonomy/gtdbtk")
ORF_DIR = get_dir("orfs", "02_genes/orfs")


rule run_gtdbtk:
    conda: ENV["gtdbtk"]
    input:
        orfs=expand(str(ORF_DIR / "{sample}.faa"), sample=SAMPLE_LIST),
        genes=expand(str(ORF_DIR / "{sample}.fna"), sample=SAMPLE_LIST)
    output:
        summary=GTDB_DIR / "gtdb.merged_summary.tsv"
    benchmark:
        str(BENCHMARKS / "gtdbtk.benchmark.txt")
    params:
        indir=ORF_DIR,
        pplacer=lambda w: min(THREADS, 3),
        db=GTDBTK_DB
    log:
        str(LOGS / "gtdbtk.log")
    threads: THREADS
    shell:
        r"""
        mkdir -p {GTDB_DIR}
        # Set GTDBTK_DATA_PATH environment variable
        export GTDBTK_DATA_PATH={params.db}
        
        # Run GTDB-Tk classify_wf on all genomes
        (gtdbtk classify_wf \
            --genome_dir {params.indir} \
            --genes --skip_ani_screen \
            --out_dir {GTDB_DIR} \
            --cpus {threads} \
            --pplacer_cpus {params.pplacer} \
            -x .faa) &> {log}

        # if both summary files exist, merge them
        echo "Merging GTDB-Tk summary files..."
        if [ -s {GTDB_DIR}/gtdbtk.ar53.summary.tsv ] && [ -s {GTDB_DIR}/gtdbtk.bac120.summary.tsv ]; then
            awk 'FNR==1 && NR>1 {{next}} NF>0' {GTDB_DIR}/gtdbtk.ar53.summary.tsv {GTDB_DIR}/gtdbtk.bac120.summary.tsv > {output.summary}
        elif [ -s {GTDB_DIR}/gtdbtk.ar53.summary.tsv ]; then
            mv {GTDB_DIR}/gtdbtk.ar53.summary.tsv {output.summary}
        elif [ -s {GTDB_DIR}/gtdbtk.bac120.summary.tsv ]; then
            mv {GTDB_DIR}/gtdbtk.bac120.summary.tsv {output.summary}
        else
            touch {output.summary}
        fi
        """

"""GTDB-Tk merged summary sample
user_genome	classification	closest_genome_reference	closest_genome_reference_radius	closest_genome_taxonomy	closest_genome_ani	closest_genome_af	closest_placement_reference	closest_placement_radius	closest_placement_taxonomy	closest_placement_ani	closest_placement_af	pplacer_taxonomy	classification_method	note	other_related_references(genome_id,species_name,radius,ANI,AF)	msa_percent	translation_table	red_value	warnings
2013_MS1-MC_25cm_metaG.metabat_bins_sens.tsv.073	d__Archaea;p__Thermoproteota;c__Bathyarchaeia;o__RBG-16-48-13;f__GCA-020355125;g__JBGOZA01;s__	N/A	N/A	N/A	N/A	N/A	N/A	N/A	N/A	N/A	N/A	d__Archaea;p__Thermoproteota;c__Bathyarchaeia;o__RBG-16-48-13;f__GCA-020355125;g__;s__	taxonomic novelty determined using RED	N/A	N/A	80.87	11	0.87824	N/A
2014_IHSL_24cm_FD_concoct_bins.tsv.112	d__Archaea;p__Iainarchaeota;c__Iainarchaeia;o__Iainarchaeales;f__GCA-2688035;g__;s__	N/A	N/A	N/A	N/A	N/A	N/A	N/A	N/A	N/A	N/A	d__Archaea;p__Iainarchaeota;c__Iainarchaeia;o__Iainarchaeales;f__GCA-2688035;g__;s__	taxonomic novelty determined using RED	N/A	N/A	45.34	11	0.85573	N/A
"""