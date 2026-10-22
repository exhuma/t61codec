"""
Loader for the golden T.61 (11/1988) reference data.

The data lives in ``tests/data/t61_golden.tsv``: one row per mapping,
hand-transcribed from the specification (see the header of that file for
the sources and the column meanings). It is an independent copy of the
code tables and must never be generated from :mod:`t61codec`, so that a
refactoring cannot silently change a mapping without a test failing.

To review the table, read the TSV file directly: each row names the
bytes, the code point and the place in the specification it comes from.
This module only parses the file (strictly: any malformed row is
rejected with its line number) and derives the helper structures used
by the tests.
"""

import re
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "t61_golden.tsv"

COLUMNS = ("kind", "bytes", "codepoints", "direction", "reference", "note")
KINDS = (
    "control",
    "g0",
    "g2",
    "combination",
    "spacing_accent",
    "alias_encode",
)
DIRECTIONS = ("both", "decode", "encode")

_HEX_RE = re.compile(r"[0-9A-F]{2}( [0-9A-F]{2})*")
_CODEPOINT_RE = re.compile(r"U\+[0-9A-F]{4,6}( U\+[0-9A-F]{4,6})*")


class GoldenFormatError(ValueError):
    """
    Raised when the golden TSV file contains a malformed row.
    """

    def __init__(self, path: Path, line_number: int, message: str) -> None:
        super().__init__(f"{path}:{line_number}: {message}")


class _Row:
    """
    One validated data row of the golden file.
    """

    def __init__(
        self, kind: str, data: bytes, text: str, direction: str, line_number: int
    ) -> None:
        self.kind = kind
        self.data = data
        self.text = text
        self.direction = direction
        self.line_number = line_number


def _parse_row(path: Path, line_number: int, fields: list[str]) -> _Row:
    """
    Validate one split data line and convert it to a :class:`_Row`.
    """

    def fail(message: str) -> GoldenFormatError:
        return GoldenFormatError(path, line_number, message)

    if len(fields) != len(COLUMNS):
        raise fail(f"expected {len(COLUMNS)} tab-separated columns, got {len(fields)}")
    kind, hex_bytes, codepoints, direction, reference, _note = fields
    if kind not in KINDS:
        raise fail(f"unknown kind {kind!r}")
    if direction not in DIRECTIONS:
        raise fail(f"unknown direction {direction!r}")
    if not reference.strip():
        raise fail("empty reference")
    if not _HEX_RE.fullmatch(hex_bytes):
        raise fail(f"bad hex bytes {hex_bytes!r} (want e.g. 'C2 65')")
    if not _CODEPOINT_RE.fullmatch(codepoints):
        raise fail(f"bad code points {codepoints!r} (want e.g. 'U+00E9')")
    data = bytes.fromhex(hex_bytes)
    chars = [int(item[2:], 16) for item in codepoints.split()]
    if any(c > 0x10FFFF or 0xD800 <= c <= 0xDFFF for c in chars):
        raise fail(f"invalid Unicode scalar value in {codepoints!r}")
    if len(chars) != 1:
        raise fail("exactly one code point per row is expected")
    text = chr(chars[0])
    if (kind == "alias_encode") != (direction == "encode"):
        raise fail("direction 'encode' is for, and only for, kind alias_encode")
    expected_length = 2 if kind in ("combination", "spacing_accent") else None
    if kind == "alias_encode":
        if len(data) > 2:
            raise fail("alias bytes must be one or two bytes")
    elif len(data) != (expected_length or 1):
        raise fail(f"kind {kind} needs {expected_length or 1} byte(s) per row")
    if kind == "g0" and not 0x20 <= data[0] <= 0x7E:
        raise fail("g0 byte outside 0x20-0x7E")
    if kind == "g2" and not 0xA0 <= data[0] <= 0xFF:
        raise fail("g2 byte outside 0xA0-0xFF")
    if kind == "combination" and not 0xC1 <= data[0] <= 0xCF:
        raise fail("combination prefix outside 0xC1-0xCF")
    if kind == "spacing_accent" and data[1] != 0x20:
        raise fail("spacing_accent must be a diacritic followed by 20 (SPACE)")
    return _Row(kind, data, text, direction, line_number)


def parse_rows(path: Path) -> list[_Row]:
    """
    Parse and validate every data row of a golden TSV file.
    """
    rows: list[_Row] = []
    seen_header = False
    seen_bytes: dict[bytes, int] = {}
    seen_aliases: dict[str, int] = {}
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise GoldenFormatError(path, 1, "file must not start with a BOM")
    if b"\r" in raw:
        raise GoldenFormatError(path, 1, "file must use LF line endings")
    text = raw.decode("utf-8")
    for line_number, line in enumerate(text.split("\n"), start=1):
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.split("\t")
        if not seen_header:
            if tuple(fields) != COLUMNS:
                raise GoldenFormatError(
                    path, line_number, f"expected header {'<TAB>'.join(COLUMNS)}"
                )
            seen_header = True
            continue
        row = _parse_row(path, line_number, fields)
        if row.kind == "alias_encode":
            first_seen = seen_aliases.setdefault(row.text, line_number)
        else:
            first_seen = seen_bytes.setdefault(row.data, line_number)
        if first_seen != line_number:
            raise GoldenFormatError(
                path, line_number, f"duplicate key (first seen on line {first_seen})"
            )
        rows.append(row)
    if not seen_header:
        raise GoldenFormatError(path, 1, "missing header line")
    return rows


def _single(kinds: tuple[str, ...], rows: list[_Row]) -> dict[int, str]:
    """
    Map the byte of every single-byte row of the given kinds to its text.
    """
    return {row.data[0]: row.text for row in rows if row.kind in kinds}


_ROWS = parse_rows(DATA_FILE)

#: Valid control functions (Fig. 3/T.61), identity-mapped on decode.
#: BS, LF, FF, CR, SUB, PLD, PLU, CSI.
CONTROLS = _single(("control",), _ROWS)

#: Primary set G0 (Table 1/T.61, Fig. 2 Note 4).
G0 = _single(("g0",), _ROWS)

#: Supplementary set G2, spacing characters (Table 2/T.61).
G2 = _single(("g2",), _ROWS)

#: Every byte that decodes to a character on its own.
SINGLE_BYTES = {**CONTROLS, **G0, **G2}

#: Bytes decoded on receipt but never produced by the encoder, with the
#: canonical byte the encoder uses instead (None: not encodable at all).
#: Derived: rows with direction ``decode``; the canonical byte is the
#: ``both`` row of the same code point, if there is one.
RECEIVE_ONLY: dict[int, int | None] = {
    row.data[0]: next(
        (
            other.data[0]
            for other in _ROWS
            if other.kind in ("control", "g0", "g2")
            and other.direction == "both"
            and other.text == row.text
        ),
        None,
    )
    for row in _ROWS
    if row.kind in ("control", "g0", "g2") and row.direction == "decode"
}

#: Diacritic + SPACE: the spacing accents (§4.1.3.1 d, §3.2.3.8).
SPACING = {row.data[0]: row.text for row in _ROWS if row.kind == "spacing_accent"}

#: Diacritic prefix bytes (excluding the 0xC9 alias and 0xCC underline).
#: Kept explicit as a cross-check: it must equal the prefixes found in
#: the table (asserted below).
DIACRITICS = (
    0xC1,
    0xC2,
    0xC3,
    0xC4,
    0xC5,
    0xC6,
    0xC7,
    0xC8,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
)

#: All 155 Figure B-1 combinations: bytes -> precomposed character.
LETTER_COMBINATIONS = {row.data: row.text for row in _ROWS if row.kind == "combination"}

#: The 13 diacritic + SPACE forms: bytes -> spacing character.
SPACING_COMBINATIONS = {
    row.data: row.text for row in _ROWS if row.kind == "spacing_accent"
}

#: Every valid two-byte diacritic sequence (canonical encodings).
COMBINATIONS = {**LETTER_COMBINATIONS, **SPACING_COMBINATIONS}

#: Encode-only aliases (D2, D3) and NFC singletons.
ENCODE_ALIASES = {row.text: row.data for row in _ROWS if row.kind == "alias_encode"}

assert tuple(sorted({data[0] for data in COMBINATIONS})) == DIACRITICS, (
    "DIACRITICS constant disagrees with the prefixes in " + str(DATA_FILE)
)
