from __future__ import annotations


import os
import shlex
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
import yaml

app = typer.Typer(add_completion=False, help="MAGport CLI")
console = Console()

DEFAULT_MODULES = "stats,quality,park,gunc,rrna,trna,orfs,gtdb,rrna16S,mimag"


def _abs(p: str) -> str:
    return str(Path(p).expanduser().resolve())


@app.command(name="report")
def main(
    input_dir: str = typer.Option(..., "--input_dir", "-i", help="Directory with MAG FASTA files"),
    output_dir: str = typer.Option(..., "--output_dir", "-o", help="Output directory"),
    file_extension: str = typer.Option(".fasta", "--file_extension", "-e", help="FASTA extension (e.g. .fa,.fna,.fasta)"),
    threads: int = typer.Option(8, "--threads", "-t", help="Max threads"),
    modules: str = typer.Option(DEFAULT_MODULES, "--modules", help="Comma-separated modules to run"),
    force_rerun: bool = typer.Option(False, "--force_rerun", "-f", help="Force re-execution"),
    conda_prefix: str = typer.Option(str(Path.home() / ".snakemake" / "conda"), "--conda-prefix", help="Directory to store Conda environments"),
    rename_pattern: Optional[str] = typer.Option(None, "--rename_pattern", help="Pattern to rename genomes, e.g. MAGs_[phylum5]_[increnum]"),
    input_taxonomy: Optional[str] = typer.Option(None, "--input_taxonomy", help="Existing GTDB taxonomy TSV to use instead of running GTDB-Tk"),
    gtdb_version: Optional[str] = typer.Option(None, "--gtdb_version", help="GTDB release/version for --input_taxonomy, e.g. R232"),
    input_quality: Optional[str] = typer.Option(None, "--input_quality", help="Existing CheckM2 quality TSV to use instead of running CheckM2"),
    snake_args: Optional[str] = typer.Option(None, "--snake_args", help="Extra Snakemake args, e.g. --snake_args '--unlock'"),
):
    """Run MAGport Snakemake workflow."""

    if bool(input_taxonomy) != bool(gtdb_version):
        console.print("[red]--input_taxonomy and --gtdb_version must be provided together.[/red]")
        raise typer.Exit(1)

    input_dir = _abs(input_dir)
    output_dir = _abs(output_dir)
    if input_taxonomy:
        input_taxonomy = _abs(input_taxonomy)
    if input_quality:
        input_quality = _abs(input_quality)
    os.makedirs(output_dir, exist_ok=True)
    
    # Ensure file_extension starts with a dot
    if file_extension and not file_extension.startswith("."):
        file_extension = "." + file_extension

    # 1. 读取默认 config.yaml
    default_config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(default_config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # 2. 用 CLI 参数覆盖/补充
    config_data["input_dir"] = input_dir
    config_data["output_dir"] = output_dir
    config_data["file_extension"] = file_extension
    config_data["threads"] = threads
    config_data["modules"] = modules
    if rename_pattern:
        config_data["rename_pattern"] = rename_pattern
    if input_taxonomy:
        config_data["input_taxonomy"] = input_taxonomy
        config_data["gtdb_version"] = gtdb_version
    if input_quality:
        config_data["input_quality"] = input_quality

    # 3. 写入输出目录下的 config.yaml
    new_config_path = Path(output_dir) / "config.yaml"
    with open(new_config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_data, f, sort_keys=False, allow_unicode=True)

    # 4. 构建 snakemake 命令，使用新的 config.yaml
    snakefile = str(Path(__file__).parent.parent / "workflow" / "Snakefile")
    cmd = [
        sys.executable,
        "-m",
        "snakemake",
        "--snakefile",
        snakefile,
        "--cores",
        str(threads),
        "--use-conda",
        "--rerun-incomplete",
        "--printshellcmds",
        "--configfile",
        str(new_config_path),
        "--conda-prefix",
        _abs(conda_prefix),
    ]
    if force_rerun:
        cmd += ["--forceall"]
    if snake_args:
        cmd += shlex.split(snake_args)

    # Don't print extra info if generating DAG
    if not snake_args or "--dag" not in snake_args:
        console.print("[bold]Running Snakemake...[/bold]")
        console.print(" ".join(shlex.quote(c) for c in cmd))

    rc = os.spawnvp(os.P_WAIT, cmd[0], cmd)
    raise typer.Exit(code=rc)

@app.command(name="db-download")
def db_download(
    gtdb_path: Optional[str] = typer.Option(None, "--gtdb-path", help="Path to download GTDB-Tk database"),
    checkm2_db_path: Optional[str] = typer.Option(None, "--checkm2-db-path", help="Path to download CheckM2 database"),
    gunc_path: Optional[str] = typer.Option(None, "--gunc-path", help="Path to download GUNC database"),
    ncbi16s_path: Optional[str] = typer.Option(None, "--ncbi16s-path", help="Path to download NCBI 16S database"),
    threads: int = typer.Option(1, "--threads", "-t", help="Max threads"),
    conda_prefix: str = typer.Option(str(Path.home() / ".snakemake" / "conda"), "--conda-prefix", help="Directory to store Conda environments"),
):
    """Download databases to specified locations and configure them."""
    if not any([gtdb_path, checkm2_db_path, gunc_path, ncbi16s_path]):
        console.print("[red]No database paths provided for download.[/red]")
        raise typer.Exit(1)

    snakefile = str(Path(__file__).parent.parent / "workflow" / "Snakefile")
    cmd = [
        sys.executable,
        "-m",
        "snakemake",
        "--snakefile",
        snakefile,
        "--cores",
        str(threads),
        "--use-conda",
        "--conda-prefix",
        _abs(conda_prefix),
        "download_databases",
        "--config"
    ]
    
    config_args = ["skip_verify=True"]
    if checkm2_db_path:
        config_args.append(f"checkm2_download_path={_abs(checkm2_db_path)}")
    if gunc_path:
        config_args.append(f"gunc_download_path={_abs(gunc_path)}")
    if gtdb_path:
        config_args.append(f"gtdb_download_path={_abs(gtdb_path)}")
    if ncbi16s_path:
        config_args.append(f"ncbi16s_download_path={_abs(ncbi16s_path)}")

    cmd.extend(config_args)
    
    console.print("[bold]Running Snakemake to download databases...[/bold]")
    console.print(" ".join(shlex.quote(c) for c in cmd))
    
    rc = os.spawnvp(os.P_WAIT, cmd[0], cmd)
    if rc != 0:
        console.print("[red]Database download failed.[/red]")
        raise typer.Exit(code=rc)
        
    console.print("[green]Databases downloaded successfully![/green]")
    
    # Configure downloaded databases
    console.print("[bold]Configuring databases...[/bold]")
    db_config(
        checkm2=checkm2_db_path,
        gunc=gunc_path,
        gtdb=gtdb_path,
        ncbi16s=ncbi16s_path
    )

@app.command()
def db_config(
    checkm2: Optional[str] = typer.Option(None, "--checkm2", help="Path to CheckM2 database"),
    gunc: Optional[str] = typer.Option(None, "--gunc", help="Path to GUNC database"),
    gtdb: Optional[str] = typer.Option(None, "--gtdb", help="Path to GTDB-Tk database"),
    ncbi16s: Optional[str] = typer.Option(None, "--ncbi16s", help="Path to NCBI 16S database"),
):
    """Configure database paths in the global config.yaml."""
    default_config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(default_config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    updated = False
    if checkm2 is not None:
        config_data["checkm2_db_dir"] = _abs(checkm2)
        updated = True
    if gunc is not None:
        config_data["gunc_db_dir"] = _abs(gunc)
        updated = True
    if gtdb is not None:
        config_data["gtdbtk_db_dir"] = _abs(gtdb)
        updated = True
    if ncbi16s is not None:
        config_data["ncbi16s_dir"] = _abs(ncbi16s)
        updated = True

    if updated:
        with open(default_config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, sort_keys=False, allow_unicode=True)
        console.print("[green]Database configurations updated successfully![/green]")
        # Call db_check to show current status
        db_check()
    else:
        console.print("[yellow]No database paths provided. Configuration unchanged.[/yellow]")

@app.command()
def db_check():
    """Print the configured locations of the four databases."""
    default_config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(default_config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    table = Table(title="MAGport Database Configurations")
    table.add_column("Database", justify="left", style="cyan", no_wrap=True)
    table.add_column("Path", justify="left", style="magenta")

    databases = ["checkm2_db_dir", "gunc_db_dir", "ncbi16s_dir", "gtdbtk_db_dir"]
    for db in databases:
        path = config_data.get(db, "")
        if not path:
            path = "[red]Not configured[/red]"
        table.add_row(db, str(path))

    console.print(table)


if __name__ == "__main__":
    app()
