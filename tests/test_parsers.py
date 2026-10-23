from pathlib import Path

import pytest

from streamstats.errors import InvalidTimestampError
from streamstats.parsers import read_csv, read_files, read_jsonl


def test_read_csv():
    events = list(read_csv(Path("tests/files/valid.csv")))

    assert len(events) == 12
    assert events[0].source == "authentication"


def test_read_jsonl():
    events = list(read_jsonl(Path("tests/files/valid.jsonl")))

    assert len(events) == 12
    assert events[0].level == "INFO"


def test_empty_files():
    csv_events = list(read_csv(Path("tests/files/empty.csv")))
    jsonl_events = list(read_jsonl(Path("tests/files/empty.jsonl")))

    assert csv_events == []
    assert jsonl_events == []


def test_csv_skip_invalid():
    stats = {"skipped_lines": 0}

    events = list(
        read_csv(Path("tests/files/invalid.csv"), skip_invalid=True, stats=stats)
    )

    assert len(events) == 12
    assert stats["skipped_lines"] == 1


def test_csv_invalid_without_skip():
    with pytest.raises(InvalidTimestampError, match=r"invalid\.csv at line 7"):
        list(read_csv(Path("tests/files/invalid.csv")))


def test_jsonl_skip_invalid():
    stats = {"skipped_lines": 0}

    events = list(
        read_jsonl(Path("tests/files/invalid.jsonl"), skip_invalid=True, stats=stats)
    )

    assert len(events) == 12
    assert stats["skipped_lines"] == 1


def test_jsonl_invalid_without_skip():
    with pytest.raises(
        InvalidTimestampError,
        match=r"invalid\.jsonl at line 6",
    ):
        list(read_jsonl(Path("tests/files/invalid.jsonl")))


def test_read_multiple_files():
    events = read_files(
        [
            Path("tests/files/valid.csv"),
            Path("tests/files/valid_2.csv"),
        ],
        format="csv",
    )

    assert len(events) == 14


def test_unicode():
    csv_events = list(read_csv(Path("tests/files/unicode.csv")))
    jsonl_events = list(read_jsonl(Path("tests/files/unicode.jsonl")))

    assert csv_events[0].source == "authorization"
    assert jsonl_events[0].message == "user logged in"
