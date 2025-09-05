# Module 2: Quality via CheckM2 (default) or CheckM1

QUALITY_DIR = RESULTS / "quality"

rule quality_checkm2:
    conda: ENV["checkm2"]
    input:
        mag=lambda wc: SAMPLES[wc.sample]
    output:
        tsv=str(QUALITY_DIR / "{sample}.checkm2.tsv")
    params:
        db=str(CHECKM2_DB / "uniref100.KO.1.dmnd")
    threads: THREADS
    run:
        shell(r"""
        mkdir -p {QUALITY_DIR}
        checkm2 predict --threads {threads} --input {input.mag} --output-directory {QUALITY_DIR} --database {params.db} --force
        # Convert CheckM2 JSON/TSV to a simple TSV per MAG
        python - <<'PY'
import json, csv, os
from pathlib import Path
mag = Path("{input.mag}") 
outdir = Path("{QUALITY_DIR}")
stem = Path("{input.mag}").stem  
# Expect a summary.tsv; if not present, create minimal
summary_tsv = outdir/"summary.tsv"
row = {"mag": stem, "completeness": "", "contamination": ""}
if summary_tsv.exists():
    import pandas as pd
    df = pd.read_csv(summary_tsv, sep='\t')
    m = df[df['genome'].astype(str).str.contains(stem, na=False)]
    if not m.empty:
        r = m.iloc[0]
        row["completeness"] = r.get("Completeness", r.get("completeness", ""))
        row["contamination"] = r.get("Contamination", r.get("contamination", ""))
with open("{output.tsv}", 'w', newline='') as f:
    w = csv.writer(f, delimiter='\t')
    w.writerow(["mag","checkm_completeness","checkm_contamination"]) 
    w.writerow([row['mag'], row['completeness'], row['contamination']])
PY
        """)

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
