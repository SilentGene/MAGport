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
        directory(config.get("ncbi16s_download_path"))
    conda:
        ENV["blast"]
    message:
        "Downloading NCBI 16S BLAST database..."
    shell:
        """
        set -euo pipefail
        mkdir -p {output}
        cd {output}
        
        # Download BLAST DB
        echo "Downloading NCBI 16S rRNA BLAST database..."
        wget -c {NCBI16S_URL} -O 16S_ribosomal_RNA.tar.gz
        tar -xzf 16S_ribosomal_RNA.tar.gz
        rm 16S_ribosomal_RNA.tar.gz
        touch .downloaded
        """
        
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
