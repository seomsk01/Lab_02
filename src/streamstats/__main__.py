import sys
from pathlib import Path
from typing import Annotated, Literal

import typer

from .errors import CLIConfigError, StreamStatsError
from .parsers import read_files
from .report import json_report, report_construction

app = typer.Typer()


@app.command("analyze")
def analyze(
    inputs: list[Path],
    format: Annotated[Literal["csv", "jsonl"], typer.Option(...)],
    output: Annotated[Path, typer.Option()] = Path("report.json"),
    skip_invalid: bool = False,
):
    for input_path in inputs:
        if not input_path.is_file():
            raise CLIConfigError(f"Input file does not exist: {input_path}")

        if not output.parent.is_dir():
            raise CLIConfigError(f"Output directory does not exist: {output.parent}")

        if output.is_dir():
            raise CLIConfigError(f"Output path is a directory: {output}")

    stats = {"skipped_lines": 0}

    try:
        events = read_files(
            inputs, skip_invalid=skip_invalid, stats=stats, format=format
        )
        report = report_construction(events, skipped_lines=stats["skipped_lines"])
        json_report(report, output)

    except StreamStatsError as error:
        typer.echo(f"Error: {error}", err=True)
        sys.exit(2)


@app.callback()
def empty_command():
    pass


if __name__ == "__main__":
    app()
