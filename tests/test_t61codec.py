"""Tests for the t61codec package."""

import codecs

import pytest

import t61codec

# NOTE: "register()" cannot be undone in Py<3.10 (see
# https://bugs.python.org/issue41842) so we just call this on the module-level
t61codec.register()


class TestSearchFunction:
    @pytest.mark.parametrize(
        "lookup_name, expected_name",
        [("t61", "t.61"), ("t.61", "t.61")],
    )
    def test_search(self, lookup_name: str, expected_name: str) -> None:
        result = t61codec.search_function(lookup_name)
        assert result.name == expected_name

    def test_search_unknown_returns_none(self) -> None:
        """search_function should return None for unknown encodings."""
        result = t61codec.search_function("utf8")
        assert result is None


class TestEncodeDecode:
    def test_invariant(self) -> None:
        """Encoding and then decoding a value should always return the original value."""
        value = "Hello T.61: \u2126"
        result = value.encode("t.61").decode("t.61")
        assert result == value

    def test_encode_ascii(self) -> None:
        """Plain ASCII characters should encode to their byte values."""
        assert "Hello".encode("t.61") == b"Hello"

    def test_decode_ascii(self) -> None:
        """Plain ASCII bytes should decode to the same characters."""
        assert b"Hello".decode("t.61") == "Hello"

    def test_encode_omega(self) -> None:
        """The Ohm/Omega sign maps to byte 0xE0 in T.61."""
        assert "\u2126".encode("t.61") == b"\xe0"

    def test_decode_omega(self) -> None:
        """Byte 0xE0 maps to the Ohm/Omega sign in T.61."""
        assert b"\xe0".decode("t.61") == "\u2126"

    def test_encode_error_on_unmapped(self) -> None:
        """Characters with no T.61 mapping should raise UnicodeEncodeError."""
        with pytest.raises(UnicodeEncodeError):
            "\u20ac".encode("t.61")  # Euro sign has no T.61 mapping

    def test_encode_replace_on_unmapped(self) -> None:
        """The 'replace' error handler should substitute unmapped characters."""
        result = "\u20ac".encode("t.61", errors="replace")
        assert result == b"?"

    def test_encode_ignore_on_unmapped(self) -> None:
        """The 'ignore' error handler should skip unmapped characters."""
        result = "\u20ac Hello".encode("t.61", errors="ignore")
        assert result == b" Hello"

    def test_decode_special_characters(self) -> None:
        """A selection of T.61 special characters should decode correctly."""
        cases = [
            (b"\xa1", "\xa1"),  # inverted exclamation mark
            (b"\xa3", "\xa3"),  # pound sign
            (b"\xa7", "\xa7"),  # section sign
            (b"\xbf", "\xbf"),  # inverted question mark
        ]
        for raw, expected in cases:
            assert raw.decode("t.61") == expected

    def test_full_roundtrip_special_chars(self) -> None:
        """A string mixing ASCII and T.61-specific characters survives a roundtrip."""
        value = "caf\xa3"  # cafe + pound sign (U+00A3 maps to 0xA3 in T.61)
        result = value.encode("t.61").decode("t.61")
        assert result == value


class TestIncrementalCodec:
    def test_incremental_encoder(self) -> None:
        encoder = codecs.getincrementalencoder("t.61")()
        assert encoder.encode("Hello") == b"Hello"

    def test_incremental_decoder(self) -> None:
        decoder = codecs.getincrementaldecoder("t.61")()
        assert decoder.decode(b"Hello") == "Hello"


class TestStreamCodec:
    def test_stream_writer_reader_roundtrip(self) -> None:
        import io

        buf = io.BytesIO()
        writer = codecs.getwriter("t.61")(buf)
        writer.write("Hello \u2126")
        buf.seek(0)
        reader = codecs.getreader("t.61")(buf)
        assert reader.read() == "Hello \u2126"


class TestVersion:
    def test_version_is_string(self) -> None:
        assert isinstance(t61codec.__version__, str)

    def test_version_is_not_empty(self) -> None:
        assert t61codec.__version__ != ""


class TestUnknownCodecErrorHandling:
    """Regression tests for unknown codec error handling."""

    def test_lookup_unknown_raises_lookup_error(self) -> None:
        """Ensure codecs.lookup raises LookupError for unknown encodings.

        This verifies the fix for the RecursionError that occurred when
        search_function returned codecs.lookup() for unknown encodings.
        """
        with pytest.raises(LookupError):
            codecs.lookup("no-such-codec-xyz")

    def test_decode_unknown_raises_lookup_error(self) -> None:
        """Ensure bytes.decode raises LookupError for unknown encodings.

        This verifies the fix for the RecursionError that occurred when
        search_function returned codecs.lookup() for unknown encodings.
        """
        with pytest.raises(LookupError):
            b"x".decode("no-such-codec-xyz")

    def test_normal_encodings_still_work(self) -> None:
        """Ensure normal encodings like utf-8 still work after registration."""
        # UTF-8 should work through standard codec search functions
        assert b"hello".decode("utf-8") == "hello"
        # Verify encoding works with a non-ASCII character
        assert "café".encode("utf-8") == b"caf\xc3\xa9"  # noqa: UP012
