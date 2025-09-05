# Module 5: rRNA via barrnap

RRNA_DIR = RESULTS / "rrna"

rule rrna_barrnap:
    conda: ENV["barrnap"]
    input:
    mag=lambda wc: SAMPLES[wc.sample],
    lineage=lambda wc: RESULTS / "gtdbtk" / f"{wc.sample}.gtdb.tsv"
    output:
    gff=str(RRNA_DIR / "{sample}.barrnap.gff"),
    fasta=str(RRNA_DIR / "{sample}.16S.fasta"),
    tsv=str(RRNA_DIR / "{sample}.rrna.tsv")
    threads: 1
    shell:
        r"""
        mkdir -p {RRNA_DIR}
        # domain selection could use GTDB results; for now, try bacteria first then archaea
    mkdir -p {LOGS}
    kingdom=$(awk 'NR==2{print $1}' {input.lineage} 2>/dev/null | grep -qi archaea && echo arc || echo bac)
    barrnap --kingdom "$kingdom" < {input.mag} > {output.gff} 2> {LOGS}/barrnap_{wildcards.sample}.log || true
        # Extract 16S features to FASTA (build a BED file)
        awk '$3=="rRNA" && $9 ~ /16S/' {output.gff} | awk 'BEGIN{OFS="\t"}{print $1,$4-1,$5,"16S_"NR,0,$7}' > {RRNA_DIR}/{wildcards.sample}.16S.bed
        if [ -s {RRNA_DIR}/{wildcards.sample}.16S.bed ]; then
            bedtools getfasta -fi {input.mag} -bed {RRNA_DIR}/{wildcards.sample}.16S.bed -fo {output.fasta} || true
        else
            : > {output.fasta}
        fi
        # Count
        five=$(grep -c "5S" {output.gff} || true)
        sixteen=$(grep -c "16S" {output.gff} || true)
        twentythree=$(grep -c "23S" {output.gff} || true)
        total=$((five + sixteen + twentythree))
        echo -e "5S\t16S\t23S\ttotal" > {output.tsv}
        echo -e "$five\t$sixteen\t$twentythree\t$total" >> {output.tsv}
        """

# No aggregate rule
