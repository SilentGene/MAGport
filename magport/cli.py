from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False, help="MAGport CLI")
console = Console()

DEFAULT_MODULES = "stats,quality,park,gunc,rrna,trna,orfs,gtdb,rrna16S,mimag"


def _abs(p: str) -> str:
    return str(Path(p).expanduser().resolve())


@app.command()
def main(
    input_dir: str = typer.Option(..., "--input_dir", "-i", help="Directory with MAG FASTA files"),
    output_dir: str = typer.Option(..., "--output_dir", "-o", help="Output directory"),
    file_extension: str = typer.Option(".fasta", "--file_extension", "-e", help="FASTA extension (e.g. .fa,.fna,.fasta)"),
    threads: int = typer.Option(8, "--threads", "-t", help="Max threads"),
    modules: str = typer.Option(DEFAULT_MODULES, "--modules", help="Comma-separated modules to run"),
    force_rerun: bool = typer.Option(False, "--force_rerun", "-f", help="Force re-execution"),
    snake_args: Optional[str] = typer.Option(None, "--snake_args", help="Extra Snakemake args, e.g. --snake_args '--unlock'"),
):
    """Run MAGport Snakemake workflow."""
    input_dir = _abs(input_dir)
    output_dir = _abs(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    # Build snakemake command
    snakefile = str(Path(__file__).parent.parent / "workflow" / "Snakefile")
    config_args = [
        f"input_dir={shlex.quote(input_dir)}",
        f"output_dir={shlex.quote(output_dir)}",
        f"file_extension={shlex.quote(file_extension)}",
        f"threads={threads}",
        f"modules={shlex.quote(modules)}",
    ]

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
        "--config",
        "--nolock",  # Added to avoid lock issues
        *config_args,
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


if __name__ == "__main__":
    app()
