"""
Code tables of ITU-T Rec. T.61 (11/1988), 8-bit basic Teletex code.

This module holds data only. Sources: Figure 2/T.61 and Tables 1-2
(graphic characters), Figure 3/T.61 (control functions) and Figure
B-1/T.61 (valid diacritic and letter combinations).

All tables are private implementation details of :mod:`t61codec`.
"""

import unicodedata
from types import MappingProxyType

#: Non-spacing underline (Fig. 2 Note 3). Not a diacritical mark.
UNDERLINE = 0xCC

#: Unicode mark appended after the base character for 0xCC.
COMBINING_LOW_LINE = "\u0332"

#: Partial line down / partial line up. The only control functions
#: accepted between the non-spacing underline and its base (§4.1.3.1 e).
PLD = 0x8B
PLU = 0x8C

#: Substitute character. Interpreted on receipt but must never be sent
#: (§3.3.5).
SUB = 0x1A

#: Basic Teletex control functions (Fig. 3/T.61), mapped by identity.
#: BS, LF, FF, CR, SUB, PLD, PLU, CSI.
CONTROLS = frozenset({0x08, 0x0A, 0x0C, 0x0D, SUB, PLD, PLU, 0x9B})

#: Primary set G0 positions that are empty in T.61 (Table 1/T.61).
_G0_EMPTY = frozenset({0x5C, 0x5E, 0x60, 0x7B, 0x7D, 0x7E})

#: G0 positions interpreted on receipt only (Fig. 2 Note 4).
_G0_RECEIVE_ONLY = {0x23: "#", 0x24: "\u00a4"}

#: Supplementary set G2, spacing characters (Table 2/T.61).
_G2 = {
    0xA1: "\u00a1",  # INVERTED EXCLAMATION MARK
    0xA2: "\u00a2",  # CENT SIGN
    0xA3: "\u00a3",  # POUND SIGN
    0xA4: "$",  # DOLLAR SIGN
    0xA5: "\u00a5",  # YEN SIGN
    0xA6: "#",  # NUMBER SIGN
    0xA7: "\u00a7",  # SECTION SIGN
    0xA8: "\u00a4",  # CURRENCY SIGN
    0xAB: "\u00ab",  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    0xB0: "\u00b0",  # DEGREE SIGN
    0xB1: "\u00b1",  # PLUS-MINUS SIGN
    0xB2: "\u00b2",  # SUPERSCRIPT TWO
    0xB3: "\u00b3",  # SUPERSCRIPT THREE
    0xB4: "\u00d7",  # MULTIPLICATION SIGN
    0xB5: "\u00b5",  # MICRO SIGN
    0xB6: "\u00b6",  # PILCROW SIGN
    0xB7: "\u00b7",  # MIDDLE DOT
    0xB8: "\u00f7",  # DIVISION SIGN
    0xBB: "\u00bb",  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    0xBC: "\u00bc",  # VULGAR FRACTION ONE QUARTER
    0xBD: "\u00bd",  # VULGAR FRACTION ONE HALF
    0xBE: "\u00be",  # VULGAR FRACTION THREE QUARTERS
    0xBF: "\u00bf",  # INVERTED QUESTION MARK
    0xE0: "\u03a9",  # GREEK CAPITAL LETTER OMEGA (Ohm sign), D2
    0xE1: "\u00c6",  # LATIN CAPITAL LETTER AE
    0xE2: "\u0110",  # LATIN CAPITAL LETTER D WITH STROKE, D3
    0xE3: "\u00aa",  # FEMININE ORDINAL INDICATOR
    0xE4: "\u0126",  # LATIN CAPITAL LETTER H WITH STROKE
    0xE6: "\u0132",  # LATIN CAPITAL LIGATURE IJ
    0xE7: "\u013f",  # LATIN CAPITAL LETTER L WITH MIDDLE DOT
    0xE8: "\u0141",  # LATIN CAPITAL LETTER L WITH STROKE
    0xE9: "\u00d8",  # LATIN CAPITAL LETTER O WITH STROKE
    0xEA: "\u0152",  # LATIN CAPITAL LIGATURE OE
    0xEB: "\u00ba",  # MASCULINE ORDINAL INDICATOR
    0xEC: "\u00de",  # LATIN CAPITAL LETTER THORN
    0xED: "\u0166",  # LATIN CAPITAL LETTER T WITH STROKE
    0xEE: "\u014a",  # LATIN CAPITAL LETTER ENG
    0xEF: "\u0149",  # LATIN SMALL LETTER N PRECEDED BY APOSTROPHE
    0xF0: "\u0138",  # LATIN SMALL LETTER KRA
    0xF1: "\u00e6",  # LATIN SMALL LETTER AE
    0xF2: "\u0111",  # LATIN SMALL LETTER D WITH STROKE
    0xF3: "\u00f0",  # LATIN SMALL LETTER ETH
    0xF4: "\u0127",  # LATIN SMALL LETTER H WITH STROKE
    0xF5: "\u0131",  # LATIN SMALL LETTER DOTLESS I
    0xF6: "\u0133",  # LATIN SMALL LIGATURE IJ
    0xF7: "\u0140",  # LATIN SMALL LETTER L WITH MIDDLE DOT
    0xF8: "\u0142",  # LATIN SMALL LETTER L WITH STROKE
    0xF9: "\u00f8",  # LATIN SMALL LETTER O WITH STROKE
    0xFA: "\u0153",  # LATIN SMALL LIGATURE OE
    0xFB: "\u00df",  # LATIN SMALL LETTER SHARP S
    0xFC: "\u00fe",  # LATIN SMALL LETTER THORN
    0xFD: "\u0167",  # LATIN SMALL LETTER T WITH STROKE
    0xFE: "\u014b",  # LATIN SMALL LETTER ENG
}

#: Non-spacing diacritical marks (Annex B, Fig. B-1/T.61):
#: prefix byte -> (combining mark, spacing form, valid base letters).
#: The spacing form is the meaning of "diacritic + SPACE" (§4.1.3.1 d).
_DIACRITICS = {
    0xC1: ("\u0300", "`", "AEIOUaeiou"),
    0xC2: ("\u0301", "\u00b4", "ACEILNORSUYZacegilnorsuyz"),
    0xC3: ("\u0302", "^", "ACEGHIJOSUWYaceghijosuwy"),
    0xC4: ("\u0303", "~", "AINOUainou"),
    0xC5: ("\u0304", "\u00af", "AEIOUaeiou"),
    0xC6: ("\u0306", "\u02d8", "AGUagu"),
    0xC7: ("\u0307", "\u02d9", "CEGIZcegz"),
    0xC8: ("\u0308", "\u00a8", "AEIOUYaeiouy"),
    0xCA: ("\u030a", "\u02da", "AUau"),
    0xCB: ("\u0327", "\u00b8", "CGKLNRSTcklnrst"),
    0xCD: ("\u030b", "\u02dd", "OUou"),
    0xCE: ("\u0328", "\u02db", "AEIUaeiu"),
    0xCF: ("\u030c", "\u02c7", "CDELNRSTZcdelnrstz"),
}

#: Umlaut mark of the 1980 edition: a decode-only alias of 0xC8 (D5).
_DIACRITIC_ALIASES = {0xC9: 0xC8}

#: Encode-only aliases (D2, D3).
_ENCODE_ALIASES = {"\u2126": 0xE0, "\u00d0": 0xE2}


def _build_graphics() -> dict[int, str]:
    """
    Single-byte graphic characters, including receive-only positions.
    """
    graphics = {byte: chr(byte) for byte in range(0x20, 0x7F) if byte not in _G0_EMPTY}
    graphics.update(_G0_RECEIVE_ONLY)
    graphics.update(_G2)
    return graphics


def _compose(base: str, mark: str) -> str:
    """
    Return the precomposed character for *base* + *mark*.

    :raises ValueError: If the pair has no single precomposed character.
    """
    composed = unicodedata.normalize("NFC", base + mark)
    if len(composed) != 1:
        raise ValueError(f"no precomposed form for {base!r} + {mark!r}")
    return composed


def _build_composites() -> dict[tuple[int, int], str]:
    """
    Two-byte sequences (prefix, second byte) for every Fig. B-1 entry.
    """
    composites = {}
    for prefix, (mark, spacing, bases) in _DIACRITICS.items():
        composites[prefix, 0x20] = spacing
        for base in bases:
            composites[prefix, ord(base)] = _compose(base, mark)
    for alias, target in _DIACRITIC_ALIASES.items():
        for (prefix, second), char in list(composites.items()):
            if prefix == target:
                composites[alias, second] = char
    return composites


def _build_encoding() -> dict[str, bytes]:
    """
    Unicode character -> canonical T.61 bytes.

    Receive-only positions (0x23, 0x24, 0xC9) and SUB are never emitted.
    """
    encoding: dict[str, bytes] = {}

    def add(char: str, seq: bytes) -> None:
        if char in encoding:
            raise ValueError(f"ambiguous encoding for {char!r}")
        encoding[char] = seq

    for byte in sorted(CONTROLS - {SUB}):
        add(chr(byte), bytes([byte]))
    for byte, char in _build_graphics().items():
        if byte not in _G0_RECEIVE_ONLY:
            add(char, bytes([byte]))
    for (prefix, second), char in _build_composites().items():
        if prefix not in _DIACRITIC_ALIASES:
            add(char, bytes([prefix, second]))
    for char, byte in _ENCODE_ALIASES.items():
        add(char, bytes([byte]))
    return encoding


#: Single-byte graphic characters, by byte value.
GRAPHICS = MappingProxyType(_build_graphics())

#: Bytes that start a two-byte diacritic sequence (including 0xC9).
DIACRITIC_PREFIXES = frozenset(_DIACRITICS) | frozenset(_DIACRITIC_ALIASES)

#: (diacritic byte, second byte) -> character, Fig. B-1 and §4.1.3.1 d.
COMPOSITES = MappingProxyType(_build_composites())

#: Character -> canonical T.61 byte sequence (without underline).
ENCODING = MappingProxyType(_build_encoding())

#: Characters that may carry the non-spacing underline: every graphic
#: character of the repertoire (Fig. 2 Note 3), but no control function.
UNDERLINABLE = frozenset(
    char for char, seq in ENCODING.items() if seq[0] not in CONTROLS
)
