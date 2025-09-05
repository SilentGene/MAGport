# MAGport 🧬

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Snakemake pipeline for comprehensive characterization of Metagenome-Assembled Genomes (MAGs).

The name "MAGport" has multiple meaningful interpretations:
   - **Ports** MAGs through various analysis tools for characterization
   - **Reports** the results in an integrated, interactive format
   - **Passport**: Creates a comprehensive "passport" for each MAG


## 🔍 Overview

MAGport is a modular workflow that provides:

- Basic genome statistics (SeqKit)
- Quality assessment (CheckM2/CheckM1)
- Chimerism detection (GUNC)
- rRNA prediction (barrnap)
- tRNA scanning (tRNAscan-SE)
- Gene prediction (Prodigal)
- Taxonomic classification (GTDB-Tk)
- 16S-based taxonomy (DIAMOND)
- Park score calculation
- MIMAG quality classification

**Outputs:** Interactive HTML report and consolidated TSV summary.

## 🚀 Quick Start

### Prerequisites

- **Recommended:** Conda/Mamba for environment management
- **Alternative:** Pixi (note: Snakemake will still create per-rule Conda envs)
- Python 3.9 or later

### Installation

Choose one of these methods:

1. **Direct Use** (no installation):
   ```bash
   # Ensure conda/mamba is in PATH
   python -m magport --help
   ```

2. **CLI Installation**:
   ```bash
   pip install -e .
   ```

3. **Pixi** (optional):
   ```bash
   # Create and activate pixi environment
   pixi run snakemake
   ```

### Basic Usage

Run the pipeline:
```bash
magport --input_dir <mags_dir> \
        --output_dir <results_dir> \
        --threads 16 \
        --file_extension .fa
```

Start with a dry run:
```bash
magport -i <mags_dir> -o <results_dir> --threads 4 --snake_args "-n"
```

## 📦 Modules

Select specific modules with `--modules` (comma-separated):

| Category | Modules |
|----------|---------|
| Stats    | `stats` |
| Quality  | `quality`, `park`, `gunc`, `mimag` |
| Features | `rrna`, `trna`, `orfs` |
| Taxonomy | `gtdb`, `rrna16S` |

Default: All modules enabled.

## 🗄️ Databases

| Database | Setup | Configuration |
|----------|-------|---------------|
| CheckM2  | Auto-download | `config.checkm2_db_dir` |
| GUNC     | Auto-download | `config.gunc_db_dir` |
| GTDB-Tk  | Manual setup required | `config.gtdbtk_db_dir` |
| NCBI 16S | Auto-download & build | `config.ncbi16s_dir` |

## 📊 Outputs

```
results/
├── MAGport_report.html    # Interactive visualization
├── MAGport_summary.tsv    # Consolidated results
└── results/              
    ├── seqkit/           # Genome statistics
    ├── quality/          # CheckM2/CheckM1 results
    ├── gunc/            # Contamination assessment
    ├── rrna/            # Predicted rRNAs
    ├── trna/            # Predicted tRNAs
    ├── orfs/            # Predicted genes
    ├── gtdbtk/          # Taxonomic classification
    ├── 16S/             # 16S-based taxonomy
    ├── park/            # Park scores
    └── mimag/           # Quality classification
```

## 📝 Notes

- First run creates Conda environments under `.snakemake/conda/`

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
