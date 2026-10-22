"""
Stateless T.61 decoding and encoding cores.

The public codec classes in :mod:`t61codec` are thin wrappers around
:func:`decode` and :func:`encode`.
"""

import codecs
import unicodedata
from typing import TYPE_CHECKING, cast

from t61codec._tables import (
    COMBINING_LOW_LINE,
    COMPOSITES,
    CONTROLS,
    DIACRITIC_PREFIXES,
    ENCODING,
    GRAPHICS,
    PLD,
    PLU,
    SUB,
    UNDERLINABLE,
    UNDERLINE,
)

if TYPE_CHECKING:
    from typing_extensions import Buffer

NAME = "t.61"

_TRUNCATED = "unexpected end of data"
_NO_UNDERLINE_BASE = "non-spacing underline not followed by a graphic character"
_SINGLE = {**GRAPHICS, **{byte: chr(byte) for byte in CONTROLS}}

# A decoded unit is (text, end offset); a str is an error reason.
_Unit = tuple[str, int] | str


def _undefined_reason(byte: int) -> str:
    """
    Error reason for a byte that is not a T.61 character on its own.
    """
    if byte < 0x20 or 0x80 <= byte < 0xA0:
        return "control function not defined in basic T.61"
    return "undefined T.61 code position"


def _read_composite(data: bytes, start: int) -> _Unit:
    """
    Read a diacritic prefix and the letter or SPACE following it.
    """
    if start + 1 >= len(data):
        return _TRUNCATED
    char = COMPOSITES.get((data[start], data[start + 1]))
    if char is None:
        return "diacritic not followed by a letter allowed by Fig. B-1/T.61"
    return char, start + 2


def _read_underlined(data: bytes, start: int) -> _Unit:
    """
    Read ``CC [PLD|PLU]* graphic``; see T.61 §4.1.3.1 e.

    Controls between the underline and its base are emitted first, so
    the combining low line directly follows the character it applies to.
    """
    pos = start + 1
    while pos < len(data) and data[pos] in (PLD, PLU):
        pos += 1
    if pos >= len(data):
        return _TRUNCATED
    if data[pos] in DIACRITIC_PREFIXES:
        unit = _read_composite(data, pos)
    elif data[pos] in GRAPHICS:
        unit = GRAPHICS[data[pos]], pos + 1
    else:
        return _NO_UNDERLINE_BASE
    if isinstance(unit, str):
        return unit if unit == _TRUNCATED else _NO_UNDERLINE_BASE
    text, end = unit
    controls = data[start + 1 : pos].decode("latin-1")
    return controls + text + COMBINING_LOW_LINE, end


def _read_unit(data: bytes, start: int) -> _Unit:
    """
    Read one character (possibly a multi-byte sequence) at *start*.
    """
    byte = data[start]
    if byte == UNDERLINE:
        return _read_underlined(data, start)
    if byte in DIACRITIC_PREFIXES:
        return _read_composite(data, start)
    char = _SINGLE.get(byte)
    if char is None:
        return _undefined_reason(byte)
    return char, start + 1


def _resume_position(position: int, length: int) -> int:
    """
    Normalise and bounds-check a resume position from an error handler.

    :raises IndexError: If the position is outside the input.
    """
    if position < 0:
        position += length
    if not 0 <= position <= length:
        raise IndexError(f"position {position} from error handler out of bounds")
    return position


def _decode_error(data: bytes, start: int, reason: str, errors: str) -> tuple[str, int]:
    """
    Run the error handler for the one-byte span at *start*.
    """
    exc = UnicodeDecodeError(NAME, data, start, start + 1, reason)
    replacement, resume = codecs.lookup_error(errors)(exc)
    # decode-error handlers return str; typeshed's union covers encode too
    return cast("str", replacement), _resume_position(resume, len(data))


def decode(
    data: "Buffer", errors: str = "strict", final: bool = True
) -> tuple[str, int]:
    """
    Decode T.61 bytes.

    Every decode error spans exactly one byte; decoding resumes at the
    following byte, so no valid character is ever swallowed.

    :param data: Bytes-like object to decode.
    :param errors: Name of a registered error handler.
    :param final: If false, an incomplete sequence at the end of *data*
        is left unconsumed instead of being reported as an error.
    :returns: The decoded text and the number of bytes consumed.
    """
    data = bytes(data)
    parts = []
    pos = 0
    while pos < len(data):
        unit = _read_unit(data, pos)
        if isinstance(unit, tuple):
            text, pos = unit
        elif unit == _TRUNCATED and not final:
            break
        else:
            text, pos = _decode_error(data, pos, unit, errors)
        parts.append(text)
    return "".join(parts), pos


def _cluster_end(text: str, start: int) -> int:
    """
    Return the end of the cluster starting at *start*.

    A cluster is one character plus all combining characters after it.
    """
    end = start + 1
    while end < len(text) and unicodedata.combining(text[end]):
        end += 1
    return end


def _encode_cluster(cluster: str) -> bytes | None:
    """
    Encode one cluster, or return None if T.61 cannot represent it.
    """
    char = unicodedata.normalize("NFC", cluster)
    underline = len(char) == 2 and char[1] == COMBINING_LOW_LINE
    if underline:
        char = char[0]
        if char not in UNDERLINABLE:
            return None
    seq = ENCODING.get(char)
    if seq is None:
        return None
    return bytes([UNDERLINE]) + seq if underline else seq


def _encode_error(text: str, span: tuple[int, int], errors: str) -> tuple[bytes, int]:
    """
    Run the error handler for the cluster *span* of *text*.

    A str replacement is encoded strictly with this codec; if that fails,
    the original error is raised with an explanatory reason.
    """
    start, end = span
    if text[start:end] == chr(SUB):
        reason = "SUB must not be transmitted (T.61 §3.3.5)"
    else:
        reason = "character not in the T.61 repertoire"
    exc = UnicodeEncodeError(NAME, text, start, end, reason)
    replacement, resume = codecs.lookup_error(errors)(exc)
    resume = _resume_position(resume, len(text))
    if isinstance(replacement, str):
        try:
            replacement = encode(replacement)[0]
        except UnicodeEncodeError as inner:
            exc.reason = (
                f"{reason}; the replacement {replacement!r} from error "
                f"handler {errors!r} is not encodable in T.61 either"
            )
            raise exc from inner
    return bytes(replacement), resume


def encode(text: str, errors: str = "strict") -> tuple[bytes, int]:
    """
    Encode text to canonical T.61 bytes.

    Each cluster is NFC-normalised on its own, so error positions refer
    to the original, non-normalised *text*.

    :param text: Text to encode.
    :param errors: Name of a registered error handler.
    :returns: The encoded bytes and the number of characters consumed.
    """
    out = bytearray()
    pos = 0
    while pos < len(text):
        end = _cluster_end(text, pos)
        seq = _encode_cluster(text[pos:end])
        if seq is None:
            seq, end = _encode_error(text, (pos, end), errors)
        out += seq
        pos = end
    return bytes(out), len(text)
