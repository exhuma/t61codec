"""
Tests for the non-spacing underline 0xCC (T.61 §3.2.3.9, §4.1.3.1 e).
"""

import pytest
from golden import COMBINATIONS, G0, G2

GRAPHIC_BYTES = {**G0, **G2}
SENDABLE_GRAPHICS = {
    byte: char for byte, char in GRAPHIC_BYTES.items() if byte not in (0x23, 0x24)
}


@pytest.mark.parametrize(
    "byte, char", sorted(GRAPHIC_BYTES.items()), ids=lambda v: repr(v)
)
def test_underline_single_byte_graphic(byte: int, char: str) -> None:
    """
    Ensure the underline applies to every single-byte graphic character.
    """
    assert bytes([0xCC, byte]).decode("t.61") == char + "\u0332"


@pytest.mark.parametrize(
    "byte, char", sorted(SENDABLE_GRAPHICS.items()), ids=lambda v: repr(v)
)
def test_underline_single_byte_graphic_encodes(byte: int, char: str) -> None:
    """
    Ensure base + U+0332 encodes with the underline first.
    """
    assert (char + "\u0332").encode("t.61") == bytes([0xCC, byte])


@pytest.mark.parametrize(
    "data, char", sorted(COMBINATIONS.items()), ids=lambda v: repr(v)
)
def test_underline_combination_round_trip(data: bytes, char: str) -> None:
    """
    Ensure an underlined accented letter round-trips, underline first.
    """
    encoded = b"\xcc" + data

    decoded = encoded.decode("t.61")

    assert decoded == char + "\u0332"
    assert decoded.encode("t.61") == encoded


@pytest.mark.parametrize(
    "data, expected",
    [
        (b"\xcc\x8b\x8cx", "\x8b\x8cx\u0332"),
        (b"\xcc\x8c\xc2e", "\x8c\u00e9\u0332"),
    ],
    ids=repr,
)
def test_pld_plu_may_intervene(data: bytes, expected: str) -> None:
    """
    Ensure PLD/PLU between the underline and its base are kept, before
    the underlined character.
    """
    assert data.decode("t.61") == expected


@pytest.mark.parametrize(
    "data",
    [b"\xcc\n", b"\xcc\xcca", b"\xcc\x9b", b"\xcc\x5c", b"\xcc\xc2b"],
    ids=repr,
)
def test_underline_without_graphic_is_error(data: bytes) -> None:
    """
    Ensure an underline not followed by a graphic is a 1-byte error.
    """
    with pytest.raises(UnicodeDecodeError) as info:
        data.decode("t.61")

    assert (info.value.start, info.value.end) == (0, 1)


def test_underline_error_resumes_at_next_byte() -> None:
    """
    Ensure decoding resumes right after an invalid underline byte.
    """
    assert b"\xcc\nx".decode("t.61", "replace") == "\ufffd\nx"
