# Build interactive HTML report and ensure consolidated TSV exists

rule report_html:
    conda: ENV["python"]
    input:
        summary=SUMMARY_TSV,
        template=f"{workflow.basedir}/scripts/report_template.html"
    output:
        REPORT_HTML
    benchmark:
        str(BENCHMARKS / "report_html.benchmark.txt")
    params:
        title=config.get("report_title", "MAGport Report"),
        input_dir=str(INPUT_DIR)
    shell:
        r"""
        python {workflow.basedir}/scripts/report.py \
            --summary {input.summary} \
            --template {input.template} \
            --output {output} \
            --title "{params.title}" \
            --input-dir "{params.input_dir}"
        """
