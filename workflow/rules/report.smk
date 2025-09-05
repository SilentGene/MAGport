# Build interactive HTML report and ensure consolidated TSV exists

rule report_html:
    conda: ENV["python"]
    input:
        SUMMARY_TSV
    output:
        REPORT_HTML
    params:
        title=config.get("report_title", "MAGport Report"),
        input_dir=str(INPUT_DIR)
    shell:
        r"""
        python workflow/scripts/report.py {input} {output} "{params.title}" "{params.input_dir}"
        """
