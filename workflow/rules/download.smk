# Database download rules
from pathlib import Path

# Common URLs
GTDBTK_URL = "https://data.gtdb.ecogenomic.org/releases/release220/220.0/auxillary_files/gtdbtk_package/full_package/gtdbtk_r220_data.tar.gz"
NCBI16S_URL = "https://ftp.ncbi.nlm.nih.gov/blast/db/16S_ribosomal_RNA.tar.gz"

# Download checkpoint rules
rule download_checkm2_db:
    output:
        directory(config.get("checkm2_download_path"))
    conda:
        ENV["checkm2"]
    message:
        "Downloading CheckM2 database..."
    shell:
        """
        mkdir -p {output}
        checkm2 database --download --path {output}
        touch {output}/.downloaded
        """

rule download_gunc_db:
    output:
        directory(config.get("gunc_download_path"))
    conda:
        ENV["gunc"]
    message:
        "Downloading GUNC database..."
    shell:
        """
        mkdir -p {output}
        gunc download_db -d {output}
        touch {output}/.downloaded
        """

rule download_gtdbtk_db:
    output:
        directory(config.get("gtdb_download_path"))
    conda:
        ENV["gtdbtk"]  # For wget/curl and other tools
    message:
        "Downloading GTDB-Tk database..."
    shell:
        """
        set -euo pipefail
        mkdir -p {output}
        wget -c {GTDBTK_URL} -O {output}/gtdbtk_data.tar.gz
        cd {output}
        tar xzf gtdbtk_data.tar.gz
        rm gtdbtk_data.tar.gz
        touch .downloaded
        """

rule download_ncbi16s_db:
    output:
        directory(config.get("ncbi16s_download_path")),
        db=config.get("ncbi16s_download_path") + "/16S_ribosomal_RNA.dmnd",
        fasta=config.get("ncbi16s_download_path") + "/16S_rRNA.fasta"
    conda:
        ENV["diamond"]
    message:
        "Downloading and preparing NCBI 16S database..."
    params:
        tar=lambda wildcards, output: str(Path(output[0]) / "16S_ribosomal_RNA.tar.gz")
    shell:
        """
        set -euo pipefail
        mkdir -p {output[0]}
        
        # Download BLAST DB
        if [ ! -s {params.tar} ]; then
            echo "Downloading NCBI 16S rRNA database..."
            wget -c {NCBI16S_URL} -O {params.tar}
        fi
        
        # Extract and convert to FASTA
        if command -v blastdbcmd >/dev/null 2>&1; then
            echo "Converting BLAST DB to FASTA..."
            cd {output[0]}
            tar -xzf {params.tar}
            blastdbcmd -db 16S_ribosomal_RNA -entry all -out {output.fasta}
        else
            echo "WARNING: blastdbcmd not found. Creating empty FASTA. Install BLAST+ for complete 16S database." >&2
            touch {output.fasta}
        fi
        
        # Build DIAMOND database
        echo "Building DIAMOND database..."
        diamond makedb --in {output.fasta} --db {output.db}
        touch {output[0]}/.downloaded
        """

# Master rule for database downloads
rule download_databases:
    input:
        lambda wildcards: [
            config.get("checkm2_download_path") if config.get("checkm2_download_path") else [],
            config.get("gunc_download_path") if config.get("gunc_download_path") else [],
            config.get("gtdb_download_path") if config.get("gtdb_download_path") else [],
            config.get("ncbi16s_download_path") if config.get("ncbi16s_download_path") else []
        ]
    message:
        "All requested databases have been downloaded successfully."
