"""
Pin the complete T.61 code table against the independent golden data.
"""

import unicodedata

import pytest
from golden import (
    COMBINATIONS,
    DIACRITICS,
    ENCODE_ALIASES,
    LETTER_COMBINATIONS,
    RECEIVE_ONLY,
    SINGLE_BYTES,
    SPACING_COMBINATIONS,
)


def _decode_or_error(data: bytes) -> str | None:
    """
    Decode strictly; return None on a decode error.
    """
    try:
        return data.decode("t.61")
    except UnicodeDecodeError:
        return None


def test_golden_counts_match_figure_b1() -> None:
    """
    Ensure the transcription has 155 letter and 13 spacing combinations.
    """
    assert len(LETTER_COMBINATIONS) == 155
    assert len(SPACING_COMBINATIONS) == 13


@pytest.mark.parametrize("byte", range(256), ids=lambda b: f"{b:02X}")
def test_decode_single_byte(byte: int) -> None:
    """
    Ensure each byte on its own decodes to its character, or is an error.
    """
    expected = SINGLE_BYTES.get(byte)

    result = _decode_or_error(bytes([byte]))

    assert result == expected


@pytest.mark.parametrize(
    "byte",
    sorted(set(range(256)) - set(SINGLE_BYTES)),
    ids=lambda b: f"{b:02X}",
)
def test_single_byte_error_span(byte: int) -> None:
    """
    Ensure an invalid single byte is reported with a one-byte span.
    """
    with pytest.raises(UnicodeDecodeError) as info:
        bytes([byte]).decode("t.61")

    assert (info.value.start, info.value.end) == (0, 1)


@pytest.mark.parametrize(
    "byte",
    sorted(set(SINGLE_BYTES) - set(RECEIVE_ONLY)),
    ids=lambda b: f"{b:02X}",
)
def test_encode_single_byte(byte: int) -> None:
    """
    Ensure each sendable single-byte character encodes to its byte.
    """
    assert SINGLE_BYTES[byte].encode("t.61") == bytes([byte])


@pytest.mark.parametrize(
    "data, expected", sorted(COMBINATIONS.items()), ids=lambda v: repr(v)
)
def test_decode_combination(data: bytes, expected: str) -> None:
    """
    Ensure each Fig. B-1 combination and spacing form decodes correctly.
    """
    assert data.decode("t.61") == expected


@pytest.mark.parametrize(
    "data, char", sorted(COMBINATIONS.items()), ids=lambda v: repr(v)
)
def test_encode_combination(data: bytes, char: str) -> None:
    """
    Ensure each combination encodes from its precomposed character.
    """
    assert char.encode("t.61") == data


@pytest.mark.parametrize(
    "data, char", sorted(LETTER_COMBINATIONS.items()), ids=lambda v: repr(v)
)
def test_encode_decomposed_combination(data: bytes, char: str) -> None:
    """
    Ensure decomposed (NFD) input encodes like the precomposed character.
    """
    decomposed = unicodedata.normalize("NFD", char)

    assert decomposed.encode("t.61") == data


@pytest.mark.parametrize(
    "data, char",
    sorted(item for item in COMBINATIONS.items() if item[0][0] == 0xC8),
    ids=lambda v: repr(v),
)
def test_umlaut_alias_c9(data: bytes, char: str) -> None:
    """
    Ensure 0xC9 decodes exactly like 0xC8 (decode-only alias, D5).
    """
    assert bytes([0xC9, data[1]]).decode("t.61") == char


@pytest.mark.parametrize("prefix", [*DIACRITICS, 0xC9], ids=hex)
def test_every_other_second_byte_is_invalid(prefix: int) -> None:
    """
    Ensure a diacritic followed by any byte outside Fig. B-1 is an error.
    """
    canonical = 0xC8 if prefix == 0xC9 else prefix
    valid = {data[1] for data in COMBINATIONS if data[0] == canonical}
    accepted = [
        second
        for second in range(256)
        if second not in valid and _decode_or_error(bytes([prefix, second])) is not None
    ]

    assert accepted == []


@pytest.mark.parametrize("char, expected", sorted(ENCODE_ALIASES.items()), ids=repr)
def test_encode_alias(char: str, expected: bytes) -> None:
    """
    Ensure the encode-only aliases map to their canonical bytes.
    """
    assert char.encode("t.61") == expected


@pytest.mark.parametrize("byte, canonical", sorted(RECEIVE_ONLY.items()), ids=repr)
def test_receive_only_bytes_are_never_emitted(byte: int, canonical: int | None) -> None:
    """
    Ensure 0x23, 0x24 and SUB decode but encode to their canonical form.
    """
    char = bytes([byte]).decode("t.61")

    if canonical is None:
        with pytest.raises(UnicodeEncodeError):
            char.encode("t.61")
    else:
        assert char.encode("t.61") == bytes([canonical])


def _expected_encodings() -> dict[str, bytes]:
    """
    Build the golden character -> bytes map for single characters.
    """
    expected = {
        char: bytes([byte])
        for byte, char in SINGLE_BYTES.items()
        if byte not in RECEIVE_ONLY
    }
    expected.update({char: data for data, char in COMBINATIONS.items()})
    expected.update(ENCODE_ALIASES)
    return expected


def test_encodable_repertoire_is_exact() -> None:
    """
    Ensure exactly the golden repertoire is encodable, code point by
    code point over all of Unicode (after NFC).
    """
    expected = _expected_encodings()
    mismatches = []
    for code_point in range(0x110000):
        char = chr(code_point)
        if 0xD800 <= code_point <= 0xDFFF:
            continue
        want = expected.get(unicodedata.normalize("NFC", char))
        try:
            got = char.encode("t.61")
        except UnicodeEncodeError:
            got = None
        if got != want:
            mismatches.append((hex(code_point), got, want))

    assert mismatches == []
