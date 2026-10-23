import json
from pathlib import Path

from .analysis import (
    count_events,
    count_levels,
    count_sources,
    get_time,
    top5_errors,
)


def report_construction(events: list, skipped_lines: int = 0) -> dict:
    first_timestamp, last_timestamp = get_time(events)

    report = {
        "total_events": count_events(events),
        "levels": count_levels(events),
        "sources": count_sources(events),
        "top5_errors": top5_errors(events),
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "skipped_lines": skipped_lines,
    }

    return report


def json_report(report: dict, output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, default=str)
