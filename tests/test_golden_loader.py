"""
Tests for the strictness of the golden TSV loader.
"""

import re
from pathlib import Path

import pytest
from golden import COLUMNS, GoldenFormatError, parse_rows

HEADER = "\t".join(COLUMNS) + "\n"
GOOD_ROW = "g2\tA1\tU+00A1\tboth\tTable 2\tINVERTED EXCLAMATION MARK\n"


def _write(tmp_path: Path, content: str) -> Path:
    """
    Write a sample golden file and return its path.
    """
    path = tmp_path / "sample.tsv"
    path.write_bytes(content.encode("utf-8"))
    return path


def test_loader_accepts_a_wellformed_file(tmp_path: Path) -> None:
    """
    Ensure comments, blank lines and a valid row are accepted.
    """
    path = _write(tmp_path, "# comment\n\n" + HEADER + GOOD_ROW)

    rows = parse_rows(path)

    assert [(row.kind, row.data, row.text) for row in rows] == [("g2", b"\xa1", "¡")]


@pytest.mark.parametrize(
    "bad_row, message",
    [
        ("nope\tA1\tU+00A1\tboth\tTable 2\t\n", "unknown kind"),
        ("g2\tA1\tU+00A1\tsideways\tTable 2\t\n", "unknown direction"),
        ("g2\ta1\tU+00A1\tboth\tTable 2\t\n", "bad hex"),
        ("g2\tA1 G1\tU+00A1\tboth\tTable 2\t\n", "bad hex"),
        ("g2\tA1\t00A1\tboth\tTable 2\t\n", "bad code points"),
        ("g2\tA1\tU+110000\tboth\tTable 2\t\n", "invalid Unicode scalar"),
        ("g2\tA1\tU+D800\tboth\tTable 2\t\n", "invalid Unicode scalar"),
        ("g2\tA1\tU+00A1\tboth\tTable 2\n", "expected 6"),
        ("g2\tA1\tU+00A1\tboth\t \t\n", "empty reference"),
        ("g2\t41\tU+0041\tboth\tTable 2\t\n", "g2 byte outside"),
        ("g2\tA1\tU+00A1\tencode\tTable 2\t\n", "only for, kind alias_encode"),
        ("spacing_accent\tC2 41\tU+00B4\tboth\tx\t\n", "followed by 20"),
        ("g2\tA1\tU+00A1\tboth\tTable 2\t\n" + GOOD_ROW, "duplicate key"),
    ],
)
def test_loader_rejects_malformed_rows(
    tmp_path: Path, bad_row: str, message: str
) -> None:
    """
    Ensure a malformed row is rejected with a message naming its line.
    """
    path = _write(tmp_path, HEADER + bad_row)

    with pytest.raises(GoldenFormatError, match=message) as info:
        parse_rows(path)

    assert re.search(r"sample\.tsv:[23]:", str(info.value))


def test_loader_reports_the_line_number(tmp_path: Path) -> None:
    """
    Ensure the error names the exact line of the offending row.
    """
    path = _write(tmp_path, "# c\n" + HEADER + GOOD_ROW + "g0\tZZ\tU+0041\tboth\tx\t\n")

    with pytest.raises(GoldenFormatError, match=r"sample\.tsv:4:"):
        parse_rows(path)


@pytest.mark.parametrize(
    "content, message",
    [
        ("# only comments\n", "missing header"),
        ("kind\tbytes\n", "expected header"),
        ("﻿" + HEADER, "BOM"),
        (HEADER.replace("\n", "\r\n") + GOOD_ROW, "LF"),
    ],
)
def test_loader_rejects_bad_files(tmp_path: Path, content: str, message: str) -> None:
    """
    Ensure header, BOM and line-ending problems are rejected.
    """
    path = _write(tmp_path, content)

    with pytest.raises(GoldenFormatError, match=message):
        parse_rows(path)
