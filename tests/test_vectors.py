"""
Golden test vectors from the spec research report, §7.
"""

import pytest

DECODE_VECTORS = [
    # Diacritic composition (§4.1.3.1 b, Fig. B-1)
    (b"Caf\xc2e", "Caf\u00e9"),
    (b"\xc8A\xc8o\xc8u", "\u00c4\u00f6\u00fc"),
    (b"\xc8Y", "\u0178"),
    (b"\xc8y", "\u00ff"),
    (b"\xceA\xcea", "\u0104\u0105"),
    (b"\xcfz\xcfS", "\u017e\u0160"),
    (b"\xcdo\xcdU", "\u0151\u0170"),
    (b"\xcaA\xcau", "\u00c5\u016f"),
    (b"\xc7I", "\u0130"),
    (b"\xcbG", "\u0122"),
    (b"\xc2g", "\u01f5"),
    (b"\xc6g\xc3w\xc4n", "\u011f\u0175\u00f1"),
    # Spacing diacritics (§4.1.3.1 d, §3.2.3.8)
    (b"\xc1 ", "`"),
    (b"\xc2 ", "\u00b4"),
    (b"\xc3 ", "^"),
    (b"\xc4 ", "~"),
    (b"\xc5 \xc6 \xc7 \xc8 ", "\u00af\u02d8\u02d9\u00a8"),
    (b"\xca \xcb \xcd \xce \xcf ", "\u02da\u00b8\u02dd\u02db\u02c7"),
    # Underline (§4.1.3.1 e, §3.2.3.9)
    (b"\xcca", "a\u0332"),
    (b"\xcc\xc2e", "\u00e9\u0332"),
    (b"\xcc ", " \u0332"),
    (b"\xcc\x8ba", "\x8ba\u0332"),
    # Single bytes and aliases (Fig. 2 Note 4, Table 2)
    (b"\x23", "#"),
    (b"\x24", "\u00a4"),
    (b"\xe9\xf8\xfb\xef\xf5\xe7", "\u00d8\u0142\u00df\u0149\u0131\u013f"),
    (b"\xb4\xb8\xb5", "\u00d7\u00f7\u00b5"),
    (b"\xe0", "\u03a9"),
    (b"\xe2", "\u0110"),
    (b"\xc9a", "\u00e4"),
    # Controls
    (b"\r\n", "\r\n"),
    (b"\x0c", "\x0c"),
    (b"\x08", "\x08"),
    (b"\x9b4m", "\x9b4m"),
    (b"\x8b\x8c", "\x8b\x8c"),
    (b"\x1a", "\x1a"),
]

ENCODE_VECTORS = [
    ("#", b"\xa6"),
    ("\u00a4", b"\xa8"),
    ("$", b"\xa4"),
    ("\u2126", b"\xe0"),
    ("\u03a9", b"\xe0"),
    ("\u0110", b"\xe2"),
    ("\u00d0", b"\xe2"),
    ("\u212b", b"\xcaA"),
    ("\u00e9", b"\xc2e"),
    ("e\u0301", b"\xc2e"),
    ("\x8ba\u0332", b"\x8b\xcca"),
    ("\u00e9\u0332", b"\xcc\xc2e"),
    ("e\u0301\u0332", b"\xcc\xc2e"),
    ("e\u0332\u0301", b"\xcc\xc2e"),
    ("\u00a8", b"\xc8 "),
]

UNDEFINED_BYTES = [
    b"\x5c",
    b"\x5e",
    b"\x60",
    b"\x7b",
    b"\x7d",
    b"\x7e",
    b"\x7f",
    b"\xa0",
    b"\xff",
    b"\xa9",
    b"\xd0",
    b"\xe5",
    b"\xc0 ",
    b"\x09",
    b"\x00",
    b"\x85",
    b"\x1b",
    b"\x0e",
    b"\x0f",
    b"\x19",
    b"\x1d",
    b"\x8d",
]


@pytest.mark.parametrize("data, expected", DECODE_VECTORS, ids=repr)
def test_decode_vector(data: bytes, expected: str) -> None:
    """
    Ensure each golden byte string decodes to its golden text.
    """
    assert data.decode("t.61") == expected


@pytest.mark.parametrize("text, expected", ENCODE_VECTORS, ids=repr)
def test_encode_vector(text: str, expected: bytes) -> None:
    """
    Ensure each golden text encodes to its canonical bytes.
    """
    assert text.encode("t.61") == expected


@pytest.mark.parametrize(
    "data",
    [
        data
        for data, _ in DECODE_VECTORS
        if not {0x23, 0x24, 0x1A, 0xC9} & set(data) and data != b"\xcc\x8ba"
    ],
    ids=repr,
)
def test_canonical_bytes_round_trip(data: bytes) -> None:
    """
    Ensure canonical byte strings survive decode then encode unchanged.
    """
    assert data.decode("t.61").encode("t.61") == data


@pytest.mark.parametrize("data", UNDEFINED_BYTES, ids=repr)
def test_undefined_position_is_error(data: bytes) -> None:
    """
    Ensure undefined positions and controls raise with a 1-byte span.
    """
    with pytest.raises(UnicodeDecodeError) as info:
        data.decode("t.61")

    assert (info.value.start, info.value.end) == (0, 1)


@pytest.mark.parametrize(
    "text, span",
    [
        ("\u0301e", (0, 1)),
        ("q\u0301", (0, 2)),
        ("\u01d8", (0, 1)),
        ("\u20ac", (0, 1)),
        ("\x1a", (0, 1)),
        ("\t", (0, 1)),
        ("\x00", (0, 1)),
        ("\x7f", (0, 1)),
        ("\xa0", (0, 1)),
        ("\\", (0, 1)),
        ("{", (0, 1)),
        ("\u0332", (0, 1)),
        ("\n\u0332", (0, 2)),
        ("e\u0301\u0302", (0, 3)),
        ("\u0123", (0, 1)),
    ],
    ids=repr,
)
def test_unencodable_text(text: str, span: tuple[int, int]) -> None:
    """
    Ensure unencodable clusters raise with their span in the input.
    """
    with pytest.raises(UnicodeEncodeError) as info:
        text.encode("t.61")

    assert (info.value.start, info.value.end) == span


@pytest.mark.parametrize(
    "data",
    [b"\xc7i", b"\xcbg", b"\xc2b", b"\xc2\n", b"\xc2\xc2", b"\xc2\xe0"],
    ids=repr,
)
def test_invalid_combination_is_error(data: bytes) -> None:
    """
    Ensure combinations outside Fig. B-1 raise, spanning the prefix only.
    """
    with pytest.raises(UnicodeDecodeError) as info:
        data.decode("t.61")

    assert (info.value.start, info.value.end) == (0, 1)


@pytest.mark.parametrize(
    "data, start",
    [(b"\xc2", 0), (b"ab\xc2", 2), (b"\xcc", 0), (b"x\xcc\x8b", 1)],
    ids=repr,
)
def test_trailing_prefix_is_error(data: bytes, start: int) -> None:
    """
    Ensure a prefix at the end of the input is an "unexpected end" error
    spanning the prefix byte only.
    """
    with pytest.raises(UnicodeDecodeError) as info:
        data.decode("t.61")

    error = info.value
    assert (error.start, error.end) == (start, start + 1)
    assert error.reason == "unexpected end of data"


def test_sub_is_not_transmitted() -> None:
    """
    Ensure encoding SUB fails with a reason naming T.61 §3.3.5.
    """
    with pytest.raises(UnicodeEncodeError, match="SUB"):
        "\x1a".encode("t.61")
