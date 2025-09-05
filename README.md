MAGport: A Snakemake Pipeline for MAG Characterization

Overview

MAGport is a modular Snakemake workflow to characterize Metagenome-Assembled Genomes (MAGs): basic stats, quality (CheckM2/CheckM1), chimerism (GUNC), rRNA (barrnap), tRNA (tRNAscan-SE), ORFs (Prodigal), taxonomy (GTDB-Tk), 16S-based taxonomy (DIAMOND), Park score, and MIMAG classification. It produces an interactive HTML report and a consolidated TSV.

Quick start

Prereqs: Conda/Mamba (recommended) or Pixi. Pip install is provided for the Python CLI, while bio tools are resolved via per-rule Conda envs in Snakemake.

Install (recommended)

- Using Conda/Mamba for environments created by Snakemake (no manual env creation required):

  - Option A: Use the CLI without installing the package (local run):
    1. Ensure mamba/conda is available on PATH.
    2. Run the CLI via Python: python -m magport --help

  - Option B: Install the CLI:
    pip install -e .

Pixi (optional)

If you prefer Pixi, you can create a project environment and run Snakemake; however, per-rule envs are still created by Snakemake.

Run

magport --input_dir <mags_dir> --output_dir <results_dir> --threads 16 --file_extension .fa

Tip: test a dry run first:

magport -i <mags_dir> -o <results_dir> --threads 4 --snake_args "-n"

Modules

--modules can restrict execution (comma-separated). Default runs all:
stats,quality,park,gunc,rrna,trna,orfs,gtdb,rrna16S,mimag

Databases

- CheckM2 DB: auto-download rule (config.checkm2_db_dir).
- GUNC DB: auto-download rule (config.gunc_db_dir).
- GTDB-Tk DB: requires manual acceptance; rule provided but may need user action (config.gtdbtk_db_dir).
- NCBI 16S DB: auto-download, convert to FASTA, and build DIAMOND DB (config.ncbi16s_dir).

Outputs

- MAGport_report.html – interactive report.
- MAGport_summary.tsv – consolidated table.
- results/... – per-tool outputs.

Notes

- On first run, Snakemake will create per-rule Conda envs under .snakemake/conda.
- Windows users: Prefer running in an Anaconda Prompt or Mamba PowerShell; Snakemake shells will execute in POSIX-compatible environments within Conda where needed.
