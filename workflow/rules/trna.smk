# Module 6: tRNA via tRNAscan-SE

TRNA_DIR = get_dir("trna", "02_genes/trna")

rule trna_scan:
    conda: ENV["trnascan"]
    input:
        mag=lambda wc: SAMPLES[wc.sample],
        gtdb=GTDB_DIR / "gtdb.merged_summary.tsv"
    output:
        tsv=str(TRNA_DIR / "{sample}.tRNA.tsv")
    log:
        str(LOGS / "{sample}.trnascan.log")
    threads: 1
    shell:
        r"""
        mkdir -p {TRNA_DIR}

        #get domain from gtdb summary. find the line for this mag, find "Archaea" or "Bacteria" in the 2nd column. if no line can be found, default to "Bacteria" for this MAG
        domain=$(awk -v mag="{wildcards.sample}" 'BEGIN{{FS="\t"}} $1==mag {{print $2}}' {input.gtdb})
        # if domain contains "Archaea" (case insensitive), set to "Archaea", else "Bacteria"
        if echo "$domain" | grep -qi "Archaea"; then
            tRNAscan-SE -A -o {TRNA_DIR}/{wildcards.sample}.trnascan.txt {input.mag} --log {log} --quiet --thread {threads}
        else
            tRNAscan-SE -B -o {TRNA_DIR}/{wildcards.sample}.tranascan.txt {input.mag} --log {log} --quiet --thread {threads}
        fi

        count=$(grep -vc '^#' {TRNA_DIR}/{wildcards.sample}.trnascan.txt)
        echo -e "trna_count" > {output.tsv}
        echo -e "$count" >> {output.tsv}
        """
