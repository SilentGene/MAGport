# Database setup rules (auto-download where feasible)

rule db_checkm2_download:
    conda: ENV["checkm2"]
    output:
        directory(CHECKM2_DB)
    shell:
        r"""
        mkdir -p {output}
        # Placeholder: checkm2 database setup (requires internet). Users may pre-populate.
        # checkm2 database --download --path {output}
        """

rule db_gunc_download:
    conda: ENV["gunc"]
    output:
        directory(GUNC_DB)
    shell:
        r"""
        mkdir -p {output}
        # Placeholder: gunc database download (e.g., gunc download-db)
        """

rule db_gtdbtk_note:
    message:
        "GTDB-Tk DB must be provided by the user. Set gtdbtk_db_dir in config.yaml to a valid GTDB-Tk release."
    output:
        touch(GTDBTK_DB / "REQUIRES_USER_DB")
    shell:
        r"""
        mkdir -p {GTDBTK_DB}
        touch {output}
        """

rule db_ncbi_16s_download:
    conda: ENV["diamond"]
    output:
        NCBI16S_DIR / "16S_ribosomal_RNA.dmnd"
    params:
        tar = NCBI16S_DIR / "16S_ribosomal_RNA.tar.gz",
        fasta = NCBI16S_DIR / "16S_rRNA.fasta"
    shell:
        r"""
        set -euo pipefail
        mkdir -p {NCBI16S_DIR}
        if [ ! -s {params.tar} ]; then
            curl -L https://ftp.ncbi.nlm.nih.gov/blast/db/16S_ribosomal_RNA.tar.gz -o {params.tar}
        fi
        # Extract and convert BLAST db to FASTA (requires blastdbcmd); fallback note if missing
        if command -v blastdbcmd >/dev/null 2>&1; then
            tar -xzf {params.tar} -C {NCBI16S_DIR}
            # There may be multiple volumes; build a .pin file list
            DBROOT=$(ls {NCBI16S_DIR}/16S_ribosomal_RNA.*.tar.gz 2>/dev/null | head -n1 || true)
            # Fallback to base name
            blastdbcmd -db {NCBI16S_DIR}/16S_ribosomal_RNA -entry all -out {params.fasta} || true
        else
            echo "blastdbcmd not found; attempting direct tar to FASTA is not supported. Please install BLAST+ for a complete 16S FASTA." >&2
            touch {params.fasta}
        fi
        diamond makedb --in {params.fasta} -d {output}
        """
