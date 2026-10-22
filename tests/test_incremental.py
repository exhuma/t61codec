"""
Tests for the incremental codecs and the stream reader and writer.
"""

import codecs
import io
from pathlib import Path

import pytest

SAMPLE_BYTES = b"Caf\xc2e \xcc\x8b\xc2a\xcc \xc8u\xc9A \xca \x9b4m\xe0\r\n\xcc\x8c\x8bz"
SAMPLE_TEXT = "Caf\u00e9 \x8b\u00e1\u0332 \u0332\u00fc\u00c4 \u02da\x9b4m\u03a9\r\n\x8c\x8bz\u0332"


def test_sample_decodes() -> None:
    """
    Ensure the multi-byte sample decodes to the expected text.
    """
    assert SAMPLE_BYTES.decode("t.61") == SAMPLE_TEXT


@pytest.mark.parametrize("split", range(len(SAMPLE_BYTES) + 1))
def test_decoder_every_split_point(split: int) -> None:
    """
    Ensure splitting the input anywhere gives the same decoded text.
    """
    decoder = codecs.getincrementaldecoder("t.61")()

    head = decoder.decode(SAMPLE_BYTES[:split])
    tail = decoder.decode(SAMPLE_BYTES[split:], final=True)

    assert head + tail == SAMPLE_TEXT


def test_decoder_byte_by_byte() -> None:
    """
    Ensure feeding one byte at a time gives the same decoded text.
    """
    decoder = codecs.getincrementaldecoder("t.61")()

    parts = [decoder.decode(bytes([byte])) for byte in SAMPLE_BYTES]
    parts.append(decoder.decode(b"", final=True))

    assert "".join(parts) == SAMPLE_TEXT


def test_decoder_holds_back_prefix() -> None:
    """
    Ensure a trailing diacritic is buffered until the next chunk.
    """
    decoder = codecs.getincrementaldecoder("t.61")()

    assert decoder.decode(b"Caf\xc2") == "Caf"
    assert decoder.getstate() == (b"\xc2", 0)
    assert decoder.decode(b"e", final=True) == "\u00e9"


def test_decoder_final_trailing_prefix_is_error() -> None:
    """
    Ensure a buffered prefix at the final call is an error.
    """
    decoder = codecs.getincrementaldecoder("t.61")()

    with pytest.raises(UnicodeDecodeError, match="unexpected end"):
        decoder.decode(b"ab\xc2", final=True)


def test_decoder_setstate_restores_buffer() -> None:
    """
    Ensure decoder state can be saved and restored.
    """
    first = codecs.getincrementaldecoder("t.61")()
    first.decode(b"\xcc\x8b")
    second = codecs.getincrementaldecoder("t.61")()

    second.setstate(first.getstate())

    assert second.decode(b"a", final=True) == "\x8ba\u0332"


@pytest.mark.parametrize("split", range(len(SAMPLE_TEXT) + 1))
def test_encoder_split_points(split: int) -> None:
    """
    Ensure splitting text anywhere except inside a cluster gives the
    canonical bytes, and a split cluster fails instead of mis-encoding.
    """
    encoder = codecs.getincrementalencoder("t.61")()
    head, tail = SAMPLE_TEXT[:split], SAMPLE_TEXT[split:]
    expected = SAMPLE_TEXT.encode("t.61")

    if tail[:1] == "\u0332":
        encoder.encode(head)
        with pytest.raises(UnicodeEncodeError):
            encoder.encode(tail, final=True)
    else:
        assert encoder.encode(head) + encoder.encode(tail, True) == expected


def test_encoder_combining_mark_in_next_chunk_is_error() -> None:
    """
    Ensure a combining mark that starts a chunk is reported, not silently
    attached to nothing or mis-encoded.
    """
    encoder = codecs.getincrementalencoder("t.61")()

    assert encoder.encode("Cafe") == b"Cafe"
    with pytest.raises(UnicodeEncodeError) as info:
        encoder.encode("\u0301", final=True)

    assert (info.value.start, info.value.end) == (0, 1)


def test_encoder_cluster_within_chunk() -> None:
    """
    Ensure a decomposed cluster inside one chunk encodes canonically.
    """
    encoder = codecs.getincrementalencoder("t.61")()

    assert encoder.encode("Cafe\u0301") == b"Caf\xc2e"


def test_stream_writer_reader_round_trip() -> None:
    """
    Ensure text written by StreamWriter is read back by StreamReader.
    """
    buffer = io.BytesIO()
    writer = codecs.getwriter("t.61")(buffer)
    writer.write("Hello \u03a9 ")
    writer.writelines(["Caf", "e\u0301"])

    buffer.seek(0)
    reader = codecs.getreader("t.61")(buffer)

    assert buffer.getvalue() == b"Hello \xe0 Caf\xc2e"
    assert reader.read() == "Hello \u03a9 Caf\u00e9"


@pytest.mark.parametrize("size", [1, 2, 3, 5])
def test_stream_reader_small_reads(size: int) -> None:
    """
    Ensure StreamReader keeps prefixes across small read() chunks.
    """
    reader = codecs.getreader("t.61")(io.BytesIO(SAMPLE_BYTES))
    parts = []
    while chunk := reader.read(size):
        parts.append(chunk)

    assert "".join(parts) == SAMPLE_TEXT


def test_stream_reader_readlines() -> None:
    """
    Ensure StreamReader splits lines correctly across prefixes.
    """
    reader = codecs.getreader("t.61")(io.BytesIO(b"\xc2e\n\xccx\n"))

    assert reader.readlines() == ["\u00e9\n", "x\u0332\n"]


def test_stream_reader_truncated_prefix_at_eof() -> None:
    """
    Ensure read() reports a prefix left over at the end of the stream.
    """
    reader = codecs.getreader("t.61")(io.BytesIO(b"ab\xc2"))

    with pytest.raises(UnicodeDecodeError, match="unexpected end"):
        reader.read()


def test_stream_reader_truncated_prefix_replace() -> None:
    """
    Ensure the reader's error handler applies to a truncated prefix.
    """
    reader = codecs.getreader("t.61")(io.BytesIO(b"ab\xc2"), "replace")

    assert reader.read() == "ab\ufffd"


def test_text_file_round_trip(tmp_path: Path) -> None:
    """
    Ensure open(..., encoding="t.61") writes every character and reads
    it back, including the last one.
    """
    path = tmp_path / "sample.txt"
    with path.open("w", encoding="t.61", newline="") as handle:
        handle.write("Caf\u00e9 ")
        handle.write("e\u0301\u0332\r\n")

    assert path.read_bytes() == b"Caf\xc2e \xcc\xc2e\r\n"
    assert path.read_text("t.61") == "Caf\u00e9 \u00e9\u0332\n"


def test_text_file_truncated_prefix(tmp_path: Path) -> None:
    """
    Ensure reading a file ending in a prefix byte raises.
    """
    path = tmp_path / "truncated.txt"
    path.write_bytes(b"ab\xc2")

    with pytest.raises(UnicodeDecodeError, match="unexpected end"):
        path.read_text("t.61")
