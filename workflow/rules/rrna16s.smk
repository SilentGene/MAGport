# Module 9: 16S-based taxonomy with NCBI BLAST

R16_DIR = get_dir("r16s", "04_taxonomy/16S")

rule rrna16s_blast:
    conda: ENV["blast"]
    input:
        fasta=lambda wc: get_dir("rrna", "02_genes/rrna") / (wc.sample + ".16S.fasta")
    output:
        tsv=str(R16_DIR / "{sample}.16S.tsv")
    params:
        db=NCBI16S_DIR / "16S_ribosomal_RNA"  # Path to BLAST database without extension
    threads: min(4, THREADS)
    run:
        shell(r"""
        mkdir -p {R16_DIR}
        if [ -s {input.fasta} ]; then
            blastn -task megablast \
                -query {input.fasta} \
                -db {params.db} \
                -out {output.tsv} \
                -evalue 1e-5 \
                -outfmt '6 std qlen slen qcovs staxids stitle' \
                -max_target_seqs 1 \
                -num_threads {threads}
        else
            touch {output.tsv}
        fi
        """)

# No aggregate rule
