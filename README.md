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

## 🗄️ Database Configuration

### Default Behavior
By default, databases are stored in `resources/` under your output directory:
```
resources/
├── checkm2_db/     # CheckM2 database
├── gunc_db/        # GUNC database
├── gtdbtk/         # GTDB-Tk reference data
└── ncbi_16s/       # NCBI 16S BLAST database
```

### Configuration Methods

1. **Using config.yaml** (recommended):
   Create `config.yaml` in your working directory:
   ```yaml
   # Database paths (absolute paths recommended)
   checkm2_db_dir: "/path/to/checkm2_db"
   gunc_db_dir: "/path/to/gunc_db"
   gtdbtk_db_dir: "/path/to/gtdbtk_db"
   ncbi16s_dir: "/path/to/ncbi_16s"
   ```

2. **Using command line**:
   ```bash
   magport ... --snake_args "--config checkm2_db_dir=/path/to/checkm2_db"
   ```

### Database Setup

#### Easy Setup: Using the Download Command

The simplest way to set up databases is using the `magport download` command:

```bash
# Download all databases to specific locations
magport download \
  --gtdb-path /path/to/gtdb/ \
  --checkm2-db-path /path/to/checkm2db/ \
  --gunc-path /path/to/gunc/ \
  --ncbi16s-path /path/to/ncbi16s/

# Or download specific databases
magport download --gtdb-path /opt/db/gtdb/
```

#### Manual Database download

```bash
# CheckM2
checkm2 database --download --path /path/to/checkm2_db

# GUNC
gunc download_db -d /path/to/gunc_db

# GTDB
wget https://data.gtdb.ecogenomic.org/releases/release220/220.0/auxillary_files/gtdbtk_package/full_package/gtdbtk_r220_data.tar.gz
tar -xzf gtdbtk_r220_data.tar.gz -C /path/to/gtdbtk_db

# NCBI 16S
wget "https://ftp.ncbi.nlm.nih.gov/blast/db/16S_ribosomal_RNA.tar.gz"
tar -xzf 16S_ribosomal_RNA.tar.gz -C /path/to/ncbi_16s
```

> **Note**: For shared computing environments, it's recommended to install databases in a shared location to avoid redundant downloads.

#### Database configuration via Environment Variables

After downloading the databases, you can set database paths using environment variables:
```bash
export CHECKM2_DB_PATH="/path/to/checkm2_db"
export GUNC_DB_PATH="/path/to/gunc_db"
export GTDBTK_DB_PATH="/path/to/gtdbtk_db"
export NCBI16S_DB_PATH="/path/to/ncbi_16s"
```

### Database Verification

The pipeline automatically verifies database integrity before running:

- Checks for required database files and directories
- Verifies database structure and completeness
- Provides clear error messages if databases are missing or incomplete

If a database is missing or invalid, you'll receive specific instructions on how to:
1. Set up the database manually, or
2. Use `magport download` to obtain the database

To verify your database configuration without running the pipeline:
```bash
# Do a dry run with verbose output
magport -i test/mags -o test/output --snake_args "-n -p"
```

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
