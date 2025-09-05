# Collect all per-MAG TSVs into a consolidated summary

rule collect_summary:
    conda: ENV["python"]
    input:
        mags=MAGS
    output:
        SUMMARY_TSV
    params:
        mag_list=lambda w: " ".join(MAGS)
    shell:
        r"""
        python workflow/scripts/collect.py {output} {RESULTS} {params.mag_list}
        """
