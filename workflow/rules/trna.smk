# Module 6: tRNA via tRNAscan-SE

TRNA_DIR = RESULTS / "trna"

rule trna_scan:
    conda: ENV["trnascan"]
    input:
    mag=lambda wc: SAMPLES[wc.sample]
    output:
    tsv=str(TRNA_DIR / "{sample}.trna.tsv")
    threads: 1
    shell:
        r"""
        mkdir -p {TRNA_DIR}
        tRNAscan-SE -o {TRNA_DIR}/{Path(input.mag).stem}.trnascan.txt {input.mag} || true
        count=$(grep -vc '^#' {TRNA_DIR}/{Path(input.mag).stem}.trnascan.txt || true)
        echo -e "trna_count" > {output.tsv}
        echo -e "$count" >> {output.tsv}
        """

# No aggregate rule
