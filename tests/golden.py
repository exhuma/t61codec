"""
Golden T.61 (11/1988) data, transcribed from the spec research report.

This is an independent copy of the code tables. It must never be derived
from :mod:`t61codec` so that a refactoring cannot silently change a
mapping without a test failing.
"""

#: Valid control functions (Fig. 3/T.61), identity-mapped on decode.
#: BS, LF, FF, CR, SUB, PLD, PLU, CSI.
CONTROLS = {
    0x08: "\x08",
    0x0A: "\n",
    0x0C: "\x0c",
    0x0D: "\r",
    0x1A: "\x1a",
    0x8B: "\x8b",
    0x8C: "\x8c",
    0x9B: "\x9b",
}

#: Primary set G0 (Table 1/T.61, Fig. 2 Note 4).
G0 = {
    0x20: " ",
    0x21: "!",
    0x22: '"',
    0x23: "#",  # receive only
    0x24: "\u00a4",  # receive only, CURRENCY SIGN
    0x25: "%",
    0x26: "&",
    0x27: "'",
    0x28: "(",
    0x29: ")",
    0x2A: "*",
    0x2B: "+",
    0x2C: ",",
    0x2D: "-",
    0x2E: ".",
    0x2F: "/",
    0x30: "0",
    0x31: "1",
    0x32: "2",
    0x33: "3",
    0x34: "4",
    0x35: "5",
    0x36: "6",
    0x37: "7",
    0x38: "8",
    0x39: "9",
    0x3A: ":",
    0x3B: ";",
    0x3C: "<",
    0x3D: "=",
    0x3E: ">",
    0x3F: "?",
    0x40: "@",
    0x41: "A",
    0x42: "B",
    0x43: "C",
    0x44: "D",
    0x45: "E",
    0x46: "F",
    0x47: "G",
    0x48: "H",
    0x49: "I",
    0x4A: "J",
    0x4B: "K",
    0x4C: "L",
    0x4D: "M",
    0x4E: "N",
    0x4F: "O",
    0x50: "P",
    0x51: "Q",
    0x52: "R",
    0x53: "S",
    0x54: "T",
    0x55: "U",
    0x56: "V",
    0x57: "W",
    0x58: "X",
    0x59: "Y",
    0x5A: "Z",
    0x5B: "[",
    0x5D: "]",
    0x5F: "_",
    0x61: "a",
    0x62: "b",
    0x63: "c",
    0x64: "d",
    0x65: "e",
    0x66: "f",
    0x67: "g",
    0x68: "h",
    0x69: "i",
    0x6A: "j",
    0x6B: "k",
    0x6C: "l",
    0x6D: "m",
    0x6E: "n",
    0x6F: "o",
    0x70: "p",
    0x71: "q",
    0x72: "r",
    0x73: "s",
    0x74: "t",
    0x75: "u",
    0x76: "v",
    0x77: "w",
    0x78: "x",
    0x79: "y",
    0x7A: "z",
    0x7C: "|",
}

#: Supplementary set G2, spacing characters (Table 2/T.61).
G2 = {
    0xA1: "\u00a1",
    0xA2: "\u00a2",
    0xA3: "\u00a3",
    0xA4: "$",
    0xA5: "\u00a5",
    0xA6: "#",
    0xA7: "\u00a7",
    0xA8: "\u00a4",
    0xAB: "\u00ab",
    0xB0: "\u00b0",
    0xB1: "\u00b1",
    0xB2: "\u00b2",
    0xB3: "\u00b3",
    0xB4: "\u00d7",
    0xB5: "\u00b5",
    0xB6: "\u00b6",
    0xB7: "\u00b7",
    0xB8: "\u00f7",
    0xBB: "\u00bb",
    0xBC: "\u00bc",
    0xBD: "\u00bd",
    0xBE: "\u00be",
    0xBF: "\u00bf",
    0xE0: "\u03a9",  # D2
    0xE1: "\u00c6",
    0xE2: "\u0110",  # D3
    0xE3: "\u00aa",
    0xE4: "\u0126",
    0xE6: "\u0132",
    0xE7: "\u013f",
    0xE8: "\u0141",
    0xE9: "\u00d8",
    0xEA: "\u0152",
    0xEB: "\u00ba",
    0xEC: "\u00de",
    0xED: "\u0166",
    0xEE: "\u014a",
    0xEF: "\u0149",
    0xF0: "\u0138",
    0xF1: "\u00e6",
    0xF2: "\u0111",
    0xF3: "\u00f0",
    0xF4: "\u0127",
    0xF5: "\u0131",
    0xF6: "\u0133",
    0xF7: "\u0140",
    0xF8: "\u0142",
    0xF9: "\u00f8",
    0xFA: "\u0153",
    0xFB: "\u00df",
    0xFC: "\u00fe",
    0xFD: "\u0167",
    0xFE: "\u014b",
}

#: Every byte that decodes to a character on its own.
SINGLE_BYTES = {**CONTROLS, **G0, **G2}

#: Bytes decoded on receipt but never produced by the encoder, with the
#: canonical byte the encoder uses instead (None: not encodable at all).
RECEIVE_ONLY = {0x23: 0xA6, 0x24: 0xA8, 0x1A: None}

#: Diacritic prefix bytes (excluding the 0xC9 alias and 0xCC underline).
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

#: Figure B-1/T.61: "<base letter><code point>" entries per prefix.
_FIGURE_B1 = {
    0xC1: "A00C0 E00C8 I00CC O00D2 U00D9 a00E0 e00E8 i00EC o00F2 u00F9",
    0xC2: (
        "A00C1 C0106 E00C9 I00CD L0139 N0143 O00D3 R0154 S015A U00DA "
        "Y00DD Z0179 a00E1 c0107 e00E9 g01F5 i00ED l013A n0144 o00F3 "
        "r0155 s015B u00FA y00FD z017A"
    ),
    0xC3: (
        "A00C2 C0108 E00CA G011C H0124 I00CE J0134 O00D4 S015C U00DB "
        "W0174 Y0176 a00E2 c0109 e00EA g011D h0125 i00EE j0135 o00F4 "
        "s015D u00FB w0175 y0177"
    ),
    0xC4: "A00C3 I0128 N00D1 O00D5 U0168 a00E3 i0129 n00F1 o00F5 u0169",
    0xC5: "A0100 E0112 I012A O014C U016A a0101 e0113 i012B o014D u016B",
    0xC6: "A0102 G011E U016C a0103 g011F u016D",
    0xC7: "C010A E0116 G0120 I0130 Z017B c010B e0117 g0121 z017C",
    0xC8: ("A00C4 E00CB I00CF O00D6 U00DC Y0178 a00E4 e00EB i00EF o00F6 u00FC y00FF"),
    0xCA: "A00C5 U016E a00E5 u016F",
    0xCB: (
        "C00C7 G0122 K0136 L013B N0145 R0156 S015E T0162 c00E7 k0137 "
        "l013C n0146 r0157 s015F t0163"
    ),
    0xCD: "O0150 U0170 o0151 u0171",
    0xCE: "A0104 E0118 I012E U0172 a0105 e0119 i012F u0173",
    0xCF: (
        "C010C D010E E011A L013D N0147 R0158 S0160 T0164 Z017D c010D "
        "d010F e011B l013E n0148 r0159 s0161 t0165 z017E"
    ),
}

#: Diacritic + SPACE: the spacing accents (§4.1.3.1 d, §3.2.3.8).
SPACING = {
    0xC1: "`",
    0xC2: "\u00b4",
    0xC3: "^",
    0xC4: "~",
    0xC5: "\u00af",
    0xC6: "\u02d8",
    0xC7: "\u02d9",
    0xC8: "\u00a8",
    0xCA: "\u02da",
    0xCB: "\u00b8",
    0xCD: "\u02dd",
    0xCE: "\u02db",
    0xCF: "\u02c7",
}

#: All 155 Figure B-1 combinations: bytes -> precomposed character.
LETTER_COMBINATIONS = {
    bytes([prefix, ord(entry[0])]): chr(int(entry[1:], 16))
    for prefix, entries in _FIGURE_B1.items()
    for entry in entries.split()
}

#: The 13 diacritic + SPACE forms: bytes -> spacing character.
SPACING_COMBINATIONS = {bytes([prefix, 0x20]): char for prefix, char in SPACING.items()}

#: Every valid two-byte diacritic sequence (canonical encodings).
COMBINATIONS = {**LETTER_COMBINATIONS, **SPACING_COMBINATIONS}

#: Encode-only aliases (D2, D3) and NFC singletons.
ENCODE_ALIASES = {
    "\u2126": b"\xe0",  # OHM SIGN
    "\u00d0": b"\xe2",  # LATIN CAPITAL LETTER ETH
    "\u212b": b"\xcaA",  # ANGSTROM SIGN, NFC -> U+00C5
}
