# Module 7: ORFs via Prodigal

ORF_DIR = get_dir("orfs", "02_genes/orfs")

rule orfs_prodigal:
    conda: ENV["prodigal"]
    input:
        mag=lambda wc: SAMPLES[wc.sample]
    output:
        faa=str(ORF_DIR / "{sample}.faa"),
        gff=str(ORF_DIR / "{sample}.gff"),
        fna=str(ORF_DIR / "{sample}.fna"),
        tsv=str(ORF_DIR / "{sample}.orfs.tsv")
    threads: 1
    shell:
        r"""
        mkdir -p {ORF_DIR}
        prodigal -q -p meta -i {input.mag} -f gff -o {output.gff} -a {output.faa} -d {output.fna}
        count=$(grep -c '^>' {output.faa})
        echo -e "orf_count" > {output.tsv}
        echo -e "$count" >> {output.tsv}
        """

# No aggregate rule
