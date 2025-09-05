# Module 2: Quality via CheckM2 (default) or CheckM1

QUALITY_DIR = RESULTS / "quality"

# 运行 CheckM2 分析整个文件夹
rule run_checkm2:
    conda: ENV["checkm2"]
    input:
        mags=MAGS  # 使用所有MAG文件
    output:
        summary=QUALITY_DIR / "summary.tsv"
    params:
        db=str(CHECKM2_DB / "uniref100.KO.1.dmnd"),
        input_dir=INPUT_DIR
    threads: THREADS
    shell:
        r"""
        mkdir -p {QUALITY_DIR}
        checkm2 predict --threads {threads} --input {params.input_dir} --output-directory {QUALITY_DIR} --database_path {params.db}
        """

# 为每个MAG从summary文件提取结果
rule quality_checkm2:
    input:
        summary=QUALITY_DIR / "summary.tsv"
    output:
        tsv=str(QUALITY_DIR / "{sample}.checkm2.tsv")
    run:
        import pandas as pd
        import csv
        
        # 读取summary文件
        df = pd.read_csv(input.summary, sep='\t')
        
        # 获取当前MAG的结果
        mag_name = wildcards.sample
        row = {"mag": mag_name, "completeness": "", "contamination": ""}
        
        # 在summary中查找当前MAG
        m = df[df['genome'].astype(str).str.contains(mag_name, na=False)]
        if not m.empty:
            r = m.iloc[0]
            row["completeness"] = r.get("Completeness", r.get("completeness", ""))
            row["contamination"] = r.get("Contamination", r.get("contamination", ""))
        
        # 写入单个MAG的结果文件
        with open(output.tsv, 'w', newline='') as f:
            w = csv.writer(f, delimiter='\t')
            w.writerow(["mag","checkm_completeness","checkm_contamination"])
            w.writerow([row['mag'], row['completeness'], row['contamination']])

rule quality_checkm1:
    conda: ENV["checkm1"]
    input:
        mag=lambda wc: SAMPLES[wc.sample]
    output:
        tsv=str(QUALITY_DIR / "{sample}.checkm1.tsv")
    params:
        db=CHECKM1_DB
    threads: THREADS
    shell:
        r"""
        mkdir -p {QUALITY_DIR}
        checkm lineage_wf -x fa -t {threads} {INPUT_DIR} {QUALITY_DIR} || true
        # Extract per-MAG metrics
        # Placeholder: user may refine to exact CheckM1 outputs.
        echo -e "mag\tcheckm_completeness\tcheckm_contamination" > {output.tsv}
        """

# No aggregate rule; Snakefile top-level expands per-sample outputs.
