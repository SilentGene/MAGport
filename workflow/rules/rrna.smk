# Module 5: rRNA via barrnap

RRNA_DIR = get_dir("rrna", "02_genes/rrna")

rule rrna_barrnap:
    conda: ENV["barrnap"]
    input:
        mag=lambda wc: SAMPLES[wc.sample],
        gtdb=GTDB_DIR / "gtdb.merged_summary.tsv"
    output:
        gff=str(RRNA_DIR / "{sample}.rRNA.gff"),
        rna_fasta=str(RRNA_DIR / "{sample}.rRNA.fna"),
        tsv=str(RRNA_DIR / "{sample}.rRNA.tsv")
    log:
        str(LOGS / "barrnap.{sample}.log")
    threads: 1
    shell:
        r"""
        mkdir -p {RRNA_DIR}
        # Determine kingdom from GTDB lineage (default to bacteria if not found)
        domain=$(awk -v mag="{wildcards.sample}" 'BEGIN{{FS="\t"}} $1==mag {{print $2}}' {input.gtdb})
        echo "Domain for {wildcards.sample}: $domain"
        # Run barrnap for rRNA prediction
        if echo "$domain" | grep -qi "Archaea"; then
            barrnap --quiet --threads {threads} --kingdom arc --outseq {output.rna_fasta} {input.mag} > {output.gff} 2> {log}
        else
            barrnap --quiet --threads {threads} --kingdom bac --outseq {output.rna_fasta} {input.mag} > {output.gff} 2> {log}
        fi

        # Count rRNAs by type
        five=$(grep -c "5S" {output.gff} || true)
        sixteen=$(grep -c "16S" {output.gff} || true)
        twentythree=$(grep -c "23S" {output.gff} || true)
        total=$((five + sixteen + twentythree))
        # Write counts to TSV
        echo -e "5S\t16S\t23S\ttotal" > {output.tsv}
        echo -e "$five\t$sixteen\t$twentythree\t$total" >> {output.tsv}
        """

# Extract the longest 16S rRNA sequence for downstream taxonomy analysis
rule extract_longest_16s:
    input:
        rna_fasta=RRNA_DIR / "{sample}.rRNA.fna"
    output:
        fasta=RRNA_DIR / "{sample}.16S.fasta"
    shell:
        r"""
        awk '/^>16S_rRNA/ {{
            header=$0
            getline seq
            if(length(seq) > maxlen) {{
                maxlen=length(seq)
                maxh=header
                maxs=seq
            }}
        }}
        END {{
            if(maxlen > 0) {{
                print maxh
                print maxs
            }}
        }}' {input.rna_fasta} > {output.fasta}
        """


