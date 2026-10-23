import csv
import json
import logging
from pathlib import Path

from pydantic import ValidationError

from .errors import (
    InvalidEventError,
    InvalidTimestampError,
    UnsupportedFormatError,
)
from .models import Event

logger = logging.getLogger(__name__)


def parse(data: dict, filename: str, line_num: int) -> Event:
    if not isinstance(data, dict):
        raise InvalidEventError(
            f"Invalid event in {filename} at line {line_num}: expected a JSON object"
        )

    required_fields = {"timestamp", "level", "source", "message"}

    for field in required_fields:
        if field not in data:
            raise InvalidEventError(
                f"Missing required field '{field}' in {filename} at line {line_num}"
            )

    try:
        return Event(
            timestamp=data["timestamp"],
            level=data["level"],
            source=data["source"],
            message=data["message"],
        )

    except ValidationError as error:
        for err in error.errors():
            if err["loc"][0] == "timestamp":
                raise InvalidTimestampError(
                    f"Invalid timestamp in {filename} at line {line_num}: "
                    f"{data['timestamp']}"
                )

        raise InvalidEventError(
            f"Validation error in {filename} at line {line_num}: {error}"
        )


def read_csv(
    path: Path,
    skip_invalid: bool = False,
    stats: dict | None = None,
):
    if stats is None:
        stats = {"skipped_lines": 0}

    with path.open("r", encoding="utf-8", newline="") as file:
        csv_reader = csv.reader(file)

        for line_num, line in enumerate(csv_reader, start=1):
            if line_num == 1:
                required_headers = [
                    "timestamp",
                    "level",
                    "source",
                    "message",
                ]

                if line != required_headers:
                    raise InvalidEventError(
                        f"Invalid CSV header in {path.name} at line {line_num}: {line}"
                    )

                continue

            if len(line) != 4:
                if skip_invalid:
                    stats["skipped_lines"] += 1
                    logger.warning(
                        "Skipping invalid line in %s at line %d: "
                        "expected 4 fields, got %d",
                        path.name,
                        line_num,
                        len(line),
                    )
                    continue

                raise InvalidEventError(
                    f"Invalid number of fields in {path.name} at line {line_num}: "
                    f"{len(line)}"
                )

            data = {
                "timestamp": line[0],
                "level": line[1],
                "source": line[2],
                "message": line[3],
            }

            try:
                event = parse(data, path.name, line_num)
            except InvalidEventError as error:
                if skip_invalid:
                    stats["skipped_lines"] += 1
                    logger.warning(
                        "Skipping invalid line in %s at line %d: %s",
                        path.name,
                        line_num,
                        error,
                    )

                    continue

                raise

            yield event


def read_jsonl(
    path: Path,
    skip_invalid: bool = False,
    stats: dict | None = None,
):
    if stats is None:
        stats = {"skipped_lines": 0}

    with path.open("r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, start=1):
            try:
                jsonl_data = json.loads(line)
                event = parse(jsonl_data, path.name, line_num)

            except (json.JSONDecodeError, InvalidEventError) as error:
                if skip_invalid:
                    stats["skipped_lines"] += 1
                    logger.warning(
                        "Skipping invalid line in %s at line %d: %s",
                        path.name,
                        line_num,
                        error,
                    )

                    continue

                if isinstance(error, json.JSONDecodeError):
                    raise InvalidEventError(
                        f"Invalid JSON format in {path.name} at line {line_num}"
                    ) from error

                raise

            yield event


def read_file(
    path: Path,
    skip_invalid: bool = False,
    stats: dict | None = None,
    format: str | None = None,
):
    if format == "csv":
        return read_csv(path, skip_invalid, stats)

    if format == "jsonl":
        return read_jsonl(path, skip_invalid, stats)

    raise UnsupportedFormatError(
        f"Unsupported file format: {path.suffix}. Supported formats are .csv and .jsonl"
    )


def read_files(
    paths: list[Path],
    skip_invalid: bool = False,
    stats: dict | None = None,
    format: str | None = None,
) -> list[Event]:
    if stats is None:
        stats = {"skipped_lines": 0}

    events = []

    for path in paths:
        read = read_file(path, skip_invalid=skip_invalid, stats=stats, format=format)
        events.extend(read)

    return events
