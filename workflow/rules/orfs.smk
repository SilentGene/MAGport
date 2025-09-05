# Module 7: ORFs via Prodigal

ORF_DIR = RESULTS / "orfs"

rule orfs_prodigal:
    conda: ENV["prodigal"]
    input:
        mag=lambda wc: SAMPLES[wc.sample]
    output:
        faa=str(ORF_DIR / "{sample}.proteins.faa"),
        gff=str(ORF_DIR / "{sample}.prodigal.gff"),
        tsv=str(ORF_DIR / "{sample}.orfs.tsv")
    threads: 1
    shell:
        r"""
        mkdir -p {ORF_DIR}
        prodigal -i {input.mag} -a {output.faa} -o {output.gff} -p meta || true
        count=$(grep -c '^>' {output.faa} || true)
        echo -e "orf_count" > {output.tsv}
        echo -e "$count" >> {output.tsv}
        """

# No aggregate rule
