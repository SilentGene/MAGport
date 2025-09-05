# Module 9: 16S-based taxonomy with DIAMOND blastn

R16_DIR = RESULTS / "16S"

rule rrna16s_diamond:
    conda: ENV["diamond"]
    input:
        fasta=lambda wc: RESULTS / "rrna" / (wc.sample + ".16S.fasta")
    output:
        tsv=str(R16_DIR / "{sample}.16S.tsv")
    params:
        db=NCBI16S_DIR / "16S_ribosomal_RNA.dmnd"  # Moved to params
    threads: THREADS
    run:
        shell(r"""
        mkdir -p {R16_DIR}
        if [ -s {input.fasta} ]; then
            diamond blastn -q {input.fasta} -d {params.db} -o {output.tsv} -f 6 qseqid sseqid pident length evalue bitscore stitle -k 1 --threads {threads}
        else
            echo -e "qseqid\tsseqid\tpident\tlength\tevalue\tbitscore\tstitle" > {output.tsv}
        fi
        """)

# No aggregate rule
