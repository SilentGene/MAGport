# Module 7: ORFs via Prodigal

ORF_DIR = get_dir("orfs", "02_genes/orfs")
GENE_INFO_TSV = OUTPUT_DIR / "02_genes" / "gene_info.tsv"

rule orfs_prodigal:
    conda: ENV["prodigal"]
    input:
        mag=get_genome_path
    output:
        faa=str(ORF_DIR / "faa" / "{sample}.faa"),
        gff=str(ORF_DIR / "gff" / "{sample}.gff"),
        ffn=str(ORF_DIR / "ffn" / "{sample}.ffn"),
        tsv=str(ORF_DIR / "orf_count" / "{sample}.orfs.tsv")
    threads: 1
    shell:
        r"""
        mkdir -p {ORF_DIR}/faa {ORF_DIR}/gff {ORF_DIR}/ffn {ORF_DIR}/orf_count
        prodigal -q -p meta -i {input.mag} -f gff -o {output.gff} -a {output.faa} -d {output.ffn}
        count=$(grep -c '^>' {output.faa})
        echo -e "orf_count" > {output.tsv}
        echo -e "$count" >> {output.tsv}
        """

rule gene_info:
    conda: ENV["python"]
    input:
        gff=lambda wc: expand(str(ORF_DIR / "gff" / "{sample}.gff"), sample=get_active_samples(wc)),
        faa=lambda wc: expand(str(ORF_DIR / "faa" / "{sample}.faa"), sample=get_active_samples(wc))
    output:
        tsv=str(GENE_INFO_TSV)
    shell:
        r"""
        python {workflow.basedir}/scripts/gene_info.py \
            --gff {input.gff} \
            --faa {input.faa} \
            --output {output.tsv}
        """
