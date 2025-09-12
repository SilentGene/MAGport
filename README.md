# MAGport 🧬

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Snakemake pipeline for comprehensive characterization of Metagenome-Assembled Genomes (MAGs).

The name "MAGport" has multiple meaningful interpretations:
   - **Ports** MAGs through various analysis tools for characterization
   - **Reports** the results in an integrated, interactive format
   - **Passport**: Creates a comprehensive "passport" for each MAG


## 🔍 Overview

MAGport is a modular workflow that provides:

1. Basic genome statistics (SeqKit)
2. Gene prediction (Prodigal)
3. Quality assessment (CheckM2/CheckM1)
4. Chimerism detection (GUNC)
5. rRNA prediction (barrnap)
6. tRNA scanning (tRNAscan-SE)
7. Taxonomic classification (GTDB-Tk)
8. 16S-based taxonomy (BLAST)
9. Park score calculation
10. MIMAG quality classification

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

### Required Databases

- **CheckM2**: For genome quality assessment
- **GUNC**: For chimerism detection
- **GTDB-Tk**: For taxonomic classification
- **NCBI 16S**: For 16S rRNA-based taxonomy

### Configuration Methods

`MAGport` requires several databases described above. If you already have these databases, you can specify their paths using either of the following methods:

1. **Set it and forget it** (recommended):
   ```bash
   magport database --checkm2 /path/to/checkm2_db \
                    --gunc /path/to/gunc_db \
                    --gtdb /path/to/gtdbtk_db \
                    --ncbi16s /path/to/ncbi_16s
   ```
   This command modifies the default configuration file located at `MAGport/config/config.yaml`, and the specified paths will be used for all future runs.

2. Manually edit the YAML config file
   You can find it at `MAGport/config/config.yaml`:
   ```yaml
   # Database paths (absolute paths recommended)
   checkm2_db_dir: "/path/to/checkm2_db"
   gunc_db_dir: "/path/to/gunc_db"
   gtdbtk_db_dir: "/path/to/gtdbtk_db"
   ncbi16s_dir: "/path/to/ncbi_16s"
   ```

3. Database configuration via Environment Variables

After downloading the databases, you can set database paths using environment variables:
```bash
export CHECKM2_DB_PATH="/path/to/checkm2_db"
export GUNC_DB_PATH="/path/to/gunc_db"
export GTDBTK_DB_PATH="/path/to/gtdbtk_db"
export NCBI16S_DB_PATH="/path/to/ncbi_16s"
```

4. Using command line during execution
   You can override database paths for a single run using `--snake_args`. I don't see why you would want to do this unless you have multiple versions of a database, but here it is:
   ```bash
   magport ... --snake_args "--config checkm2_db_dir=/path/to/checkm2_db"
   ```

### Database Download

If you don't have the required databases, `MAGport` can help you download and set them up.

#### Easy Setup: Using the Download Command

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

> [!NOTE]
> While MAGport can download multiple databases using a single command, it is advisable to download each database separately to avoid potential issues with network interruptions or timeouts.

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

> [!NOTE]
> For shared computing environments, it's recommended to install databases in a shared location to avoid redundant downloads.


### Database Verification

The pipeline automatically verifies database integrity before each running.

If a database is missing or invalid, you'll receive notifications with specific instructions on how to configure it.

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
├── 01_stats/             # Basic statistics
│   └── seqkit/           # Genome statistics (length, GC%, etc.)
├── 02_genes/             # Gene predictions
│   ├── orfs/            # Predicted protein-coding genes
│   ├── rrna/            # Predicted rRNAs
│   └── trna/            # Predicted tRNAs
├── 03_quality/           # Quality assessment
│   ├── checkm/          # CheckM2/CheckM1 results
│   ├── gunc/            # Contamination assessment
│   ├── park/            # MIMAG quality score
│   └── mimag/           # MIMAG compliance report
├── 04_taxonomy/          # Taxonomic classification
│   ├── gtdbtk/          # GTDB-Tk results
│   └── 16S/             # 16S rRNA-based taxonomy
└── logs/                # Runtime logs
```

## 📝 Notes

- First run creates Conda environments under `.snakemake/conda/`

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
