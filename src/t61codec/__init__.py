"""
Python codec for ITU-T Rec. T.61 (11/1988), the 8-bit basic Teletex code.

The codec follows the 1988 edition of T.61 to the letter:

* **Graphic characters** are the primary set (Table 1/T.61) and the
  supplementary set (Table 2/T.61). 0xE0 decodes to U+03A9 and 0xE2 to
  U+0110; on encode, U+2126 and U+00D0 are accepted as aliases. The
  receive-only bytes 0x23 and 0x24 decode to ``#`` and ``¤`` but are
  never produced: the encoder uses 0xA6 and 0xA8.
* **Diacritics** (0xC1-0xCF) are prefixes. A diacritic plus a base
  letter decodes to the precomposed character, but only for the 155
  combinations of Figure B-1/T.61. A diacritic plus SPACE decodes to the
  spacing accent (for example ``C2 20`` gives U+00B4). 0xC9, the umlaut
  of the 1980 edition, is a decode-only alias of 0xC8.
* **Non-spacing underline** (0xCC) may precede any graphic character,
  including an accented letter or SPACE, with PLD/PLU allowed in
  between. It decodes to the base character followed by U+0332
  COMBINING LOW LINE; intervening PLD/PLU are emitted before the base.
* **Control functions**: only BS, LF, FF, CR, SUB, PLD, PLU and CSI are
  accepted, by identity. SUB is accepted on decode only. CSI decodes to
  U+009B; the parameter and final bytes of a control sequence are
  ordinary primary-set bytes and are decoded as such (T.61 defines no
  further obligation for a character codec). Code extension (ESC, SS2,
  SS3, LS0, LS1, RLF) is not supported.
* **Encoding** normalises each character cluster to NFC, then emits the
  single byte or the diacritic sequence (underline first). The output is
  canonical: one byte string per NFC text. The incremental encoder and
  the stream writer encode each chunk on its own, so a character and its
  combining marks must not be split across chunks.

Everything else is an error, reported through the usual error handlers.
Every decode error spans one byte and decoding resumes right after it.
An encode error spans the cluster (base character plus combining marks)
in the original, non-normalised input (``replace`` gives one ``?`` per
code point). ``backslashreplace`` cannot work on encode because T.61 has
no backslash; it raises the original error with an explanatory reason.

**Differences from glibc** (``iconv -f T.61``): glibc passes all C0/C1
controls and 0x7F through, rejects 0x23/0x24/0xC9, decodes 0xE0/0xE2 to
U+2126/U+00D0, rejects ``C2 67`` (ǵ), ``C1/C3/C4 20`` (spacing grave,
circumflex and tilde) and the non-spacing underline 0xCC, and accepts
``CB 67`` (ģ), which Figure B-1 does not list.

**Real-world note:** OpenSSL treats T61String as Latin-1, so
TeletexString data found in X.509 certificates is often Latin-1 rather
than T.61, and this codec may reject or alter it.

See https://www.itu.int/rec/T-REC-T.61-198811-S/en
"""

import codecs
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

from t61codec import _codec

if TYPE_CHECKING:
    from typing_extensions import Buffer

try:
    __version__ = version("t61codec")
except PackageNotFoundError:  # not installed, e.g. a vendored copy
    __version__ = "0+unknown"


class Codec(codecs.Codec):
    """
    Stateless T.61 encoder and decoder.
    """

    def encode(self, input: str, errors: str = "strict") -> tuple[bytes, int]:
        """
        Encode *input* completely.

        :param input: Text to encode.
        :param errors: Name of a registered error handler.
        :returns: The encoded bytes and the number of characters consumed.
        """
        return _codec.encode(input, errors)

    def decode(self, input: "Buffer", errors: str = "strict") -> tuple[str, int]:
        """
        Decode *input* completely; a trailing prefix byte is an error.

        :param input: Bytes to decode.
        :param errors: Name of a registered error handler.
        :returns: The decoded text and the number of bytes consumed.
        """
        return _codec.decode(input, errors, final=True)


class IncrementalEncoder(codecs.IncrementalEncoder):
    """
    Incremental T.61 encoder.

    Each chunk is encoded on its own and nothing is held back, because
    :class:`io.TextIOWrapper` never calls ``encode(..., final=True)``:
    a held-back character would be lost when a file is closed. A chunk
    that starts with a combining mark therefore fails like any other
    combining mark without a base. Keep each character and its combining
    marks in the same chunk.
    """

    def encode(self, input: str, final: bool = False) -> bytes:
        """
        Encode one chunk of text.

        :param input: Next chunk of text.
        :param final: Ignored; the encoder keeps no state.
        :returns: The encoded bytes.
        """
        return _codec.encode(input, self.errors)[0]


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    """
    Incremental T.61 decoder.

    A trailing diacritic or underline prefix is buffered until the next
    call. With ``final=True`` it is an error.
    """

    def _buffer_decode(
        self, input: "Buffer", errors: str, final: bool
    ) -> tuple[str, int]:
        return _codec.decode(input, errors, final)


class StreamWriter(Codec, codecs.StreamWriter):
    """
    T.61 stream writer.

    Each :meth:`write` is encoded on its own, as with
    :class:`IncrementalEncoder`: a character and its combining marks must
    be written in the same call.
    """


class StreamReader(Codec, codecs.StreamReader):
    """
    T.61 stream reader.

    Prefix bytes at the end of one read are kept until the next read.
    :meth:`read` without a size reports a truncated prefix at the end of
    the stream as an error; :meth:`readline` cannot detect it and leaves
    it in the buffer. :class:`io.TextIOWrapper` (``open(...,
    encoding="t.61")``) always reports it.
    """

    bytebuffer: bytes  # typeshed leaves the attribute's type undetermined

    def decode(
        self, input: "Buffer", errors: str = "strict", final: bool = False
    ) -> tuple[str, int]:
        """
        Decode *input*, leaving an incomplete trailing sequence unread.

        :param input: Bytes to decode.
        :param errors: Name of a registered error handler.
        :param final: If true, a trailing prefix byte is an error.
        :returns: The decoded text and the number of bytes consumed.
        """
        return _codec.decode(input, errors, final)

    def read(self, size: int = -1, chars: int = -1, firstline: bool = False) -> str:
        """
        Read and decode, as :meth:`codecs.StreamReader.read`.

        :param size: Approximate number of bytes to read; -1 for all.
        :param chars: Number of characters to return; -1 for all.
        :param firstline: Return only the first line if decoding fails.
        :returns: The decoded text.
        """
        text = super().read(size, chars, firstline)
        if size < 0 and chars < 0 and self.bytebuffer:
            tail, _ = self.decode(self.bytebuffer, self.errors, final=True)
            self.bytebuffer = b""
            text += tail
        return text


def getregentry() -> codecs.CodecInfo:
    """
    Create a :py:class:`codecs.CodecInfo` instance for the registry.
    """
    return codecs.CodecInfo(
        name="t.61",
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )


def search_function(encoding: str) -> codecs.CodecInfo | None:
    """
    Look up the codec; usable with :py:func:`codecs.register`.

    Returns a CodecInfo for t61/t.61 encodings, or None for unknown
    encodings to allow other search functions to handle them.

    As a convenience, there is also :func:`~.register` in this module.
    """
    if encoding.lower() in ("t61", "t.61"):
        return getregentry()
    return None


def register() -> None:
    r"""
    Register the T.61 search function with Python's codec registry.

    Example:

    >>> import t61codec
    >>> t61codec.register()
    >>> b'Hello T.61: \xe0 Caf\xc2e'.decode('t.61')
    'Hello T.61: Ω Café'
    """
    codecs.register(search_function)
