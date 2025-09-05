# Module 8: GTDB-Tk taxonomy

GTDB_DIR = RESULTS / "gtdbtk"

# 运行 GTDB-Tk 分析整个文件夹
rule run_gtdbtk:
    conda: ENV["gtdbtk"]
    input:
        mags=MAGS  # 使用所有MAG文件
    output:
        bac_summary=GTDB_DIR / "run.bac120.summary.tsv",
        ar_summary=GTDB_DIR / "run.ar53.summary.tsv"
    params:
        pplacer=3,
        suffix=EXT,
        input_dir=INPUT_DIR
    threads: THREADS
    shell:
        r"""
        mkdir -p {GTDB_DIR}
        # Set GTDBTK_DATA_PATH environment variable
        export GTDBTK_DATA_PATH={GTDBTK_DB}
        # Run GTDB-Tk classify_wf on all genomes
        gtdbtk classify_wf --genome_dir {params.input_dir} --out_dir {GTDB_DIR} \
            --prefix run --cpus {threads} --pplacer {params.pplacer} \
            -x {params.suffix} --skip_ani_screen || true
        # Create empty summary files if they don't exist
        touch {output.bac_summary} {output.ar_summary}
        """

# 为每个MAG从summary文件提取结果
rule gtdbtk_classify:
    input:
        bac_summary=GTDB_DIR / "run.bac120.summary.tsv",
        ar_summary=GTDB_DIR / "run.ar53.summary.tsv"
    output:
        tsv=str(GTDB_DIR / "{sample}.gtdb.tsv")
    run:
        import pandas as pd
        import os
        
        # 初始化结果
        lineage = ""
        mag_name = wildcards.sample
        
        # 依次检查细菌和古菌的结果文件
        for summary_file in [input.bac_summary, input.ar_summary]:
            if os.path.getsize(summary_file) > 0:  # 如果文件不为空
                df = pd.read_csv(summary_file, sep='\t')
                m = df[df.iloc[:,0].astype(str) == mag_name]  # 第一列是基因组名
                if not m.empty:
                    lineage = m.iloc[0,1]  # 第二列是分类信息
                    break
        
        # 写入结果
        with open(output.tsv, 'w') as f:
            f.write("lineage\n")
            f.write(f"{lineage}\n")
