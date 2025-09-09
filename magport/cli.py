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
