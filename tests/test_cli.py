import json
from pathlib import Path

from typer.testing import CliRunner

from streamstats.__main__ import app

runner = CliRunner()


def test_cli_csv() -> None:
    try:
        result = runner.invoke(
            app,
            [
                "analyze",
                "tests/files/valid.csv",
                "--format",
                "csv",
                "--output",
                "tests/report.json",
            ],
        )

        assert result.exit_code == 0

        with open("tests/report.json", encoding="utf-8") as file:
            report = json.load(file)

        assert report["total_events"] == 12

    finally:
        Path("tests/report.json").unlink(missing_ok=True)


def test_cli_jsonl() -> None:
    try:
        result = runner.invoke(
            app,
            [
                "analyze",
                "tests/files/valid.jsonl",
                "--format",
                "jsonl",
                "--output",
                "tests/report_jsonl.json",
            ],
        )

        assert result.exit_code == 0

        with open("tests/report_jsonl.json", encoding="utf-8") as file:
            report = json.load(file)

        assert report["total_events"] == 12

    finally:
        Path("tests/report_jsonl.json").unlink(missing_ok=True)


def test_cli_skip_invalid() -> None:
    try:
        result = runner.invoke(
            app,
            [
                "analyze",
                "tests/files/invalid.jsonl",
                "--format",
                "jsonl",
                "--output",
                "tests/skip_report.json",
                "--skip-invalid",
            ],
        )

        assert result.exit_code == 0

        with open("tests/skip_report.json", encoding="utf-8") as file:
            report = json.load(file)

        assert report["total_events"] == 12
        assert report["skipped_lines"] == 1

    finally:
        Path("tests/skip_report.json").unlink(missing_ok=True)


def test_cli_invalid_without_skip():
    try:
        result = runner.invoke(
            app,
            [
                "analyze",
                "tests/files/invalid.jsonl",
                "--format",
                "jsonl",
                "--output",
                "tests/error_report.json",
            ],
        )

        assert result.exit_code == 2
        assert "invalid.jsonl" in result.output
        assert "line 6" in result.output

    finally:
        Path("tests/error_report.json").unlink(missing_ok=True)
