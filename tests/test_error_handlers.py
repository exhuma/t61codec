"""
Tests for error handlers in both directions.
"""

import codecs

import pytest


def _decode_marker(error: UnicodeError) -> tuple[str, int]:
    """
    Custom decode handler: replace the span with ``<XX>`` hex bytes.
    """
    assert isinstance(error, UnicodeDecodeError)
    raw = error.object[error.start : error.end]
    return f"<{raw.hex()}>", error.end


def _encode_marker(error: UnicodeError) -> tuple[str, int]:
    """
    Custom encode handler: replace the span with ``[n]`` (its length).
    """
    assert isinstance(error, UnicodeEncodeError)
    return f"[{error.end - error.start}]", error.end


codecs.register_error("t61test.decode", _decode_marker)
codecs.register_error("t61test.encode", _encode_marker)


@pytest.mark.parametrize(
    "data, errors, expected",
    [
        (b"\xc2b", "replace", "\ufffdb"),
        (b"\xc2b", "ignore", "b"),
        (b"\xc2\n", "replace", "\ufffd\n"),
        (b"\xc2\n", "ignore", "\n"),
        (b"\xc2\xc2e", "replace", "\ufffd\u00e9"),
        (b"ab\xc2", "replace", "ab\ufffd"),
        (b"a\x5cb\x7f", "replace", "a\ufffdb\ufffd"),
        (b"a\x09b", "ignore", "ab"),
        (b"\xc2b", "backslashreplace", "\\xc2b"),
        (b"\xc2b\xff", "t61test.decode", "<c2>b<ff>"),
        (b"a\xa0\xc2", "surrogateescape", "a\udca0\udcc2"),
    ],
    ids=repr,
)
def test_decode_error_handler(data: bytes, errors: str, expected: str) -> None:
    """
    Ensure decode error handlers see 1-byte spans and resume after them.
    """
    assert data.decode("t.61", errors) == expected


@pytest.mark.parametrize(
    "text, errors, expected",
    [
        ("\u20ac Hello", "replace", b"? Hello"),
        ("\u20ac Hello", "ignore", b" Hello"),
        ("q\u0301x", "replace", b"??x"),  # one "?" per code point
        ("e\u0301\u20ace\u0301", "replace", b"\xc2e?\xc2e"),
        ("\u20ac", "xmlcharrefreplace", b"&\xa68364;"),
        ("q\u0301\u20ac", "t61test.encode", b"[2][1]"),
        ("a\udca0\udcc2", "surrogateescape", b"a\xa0\xc2"),
    ],
    ids=repr,
)
def test_encode_error_handler(text: str, errors: str, expected: bytes) -> None:
    """
    Ensure encode error handlers work and replacements are encoded too.
    """
    assert text.encode("t.61", errors) == expected


def test_encode_error_position_in_original_text() -> None:
    """
    Ensure encode error positions refer to the non-normalised input.
    """
    text = "e\u0301e\u0301\u20ac"

    with pytest.raises(UnicodeEncodeError) as info:
        text.encode("t.61")

    assert (info.value.start, info.value.end) == (4, 5)
    assert info.value.object == text


def test_backslashreplace_on_encode_fails_cleanly() -> None:
    """
    Ensure backslashreplace raises the original error on encode, since
    T.61 has no backslash, and says why.
    """
    with pytest.raises(UnicodeEncodeError) as info:
        "a\u20ac".encode("t.61", "backslashreplace")

    error = info.value
    assert (error.start, error.end) == (1, 2)
    assert "not encodable in T.61 either" in error.reason


def test_error_handler_position_out_of_bounds() -> None:
    """
    Ensure an out-of-range resume position from a handler is rejected.
    """
    codecs.register_error("t61test.bad", lambda error: ("", len(error.object) + 5))

    with pytest.raises(IndexError):
        b"\xff".decode("t.61", "t61test.bad")
