"""
Tests for codec registration and package metadata.
"""

import codecs
import importlib.metadata
import importlib.util

import pytest

import t61codec


@pytest.mark.parametrize("lookup_name", ["t61", "t.61", "T61", "T.61"])
def test_search_function_finds_codec(lookup_name: str) -> None:
    """
    Ensure the search function returns the codec for its known names.
    """
    result = t61codec.search_function(lookup_name)

    assert result is not None
    assert result.name == "t.61"


def test_search_unknown_returns_none() -> None:
    """
    Ensure search_function returns None for unknown encodings.
    """
    assert t61codec.search_function("utf8") is None


def test_lookup_unknown_raises_lookup_error() -> None:
    """
    Ensure codecs.lookup raises LookupError for unknown encodings.

    Regression test for #3: search_function used to return
    codecs.lookup() for unknown names, which recursed forever.
    """
    with pytest.raises(LookupError):
        codecs.lookup("no-such-codec-xyz")


def test_decode_unknown_raises_lookup_error() -> None:
    """
    Ensure bytes.decode raises LookupError for unknown encodings (#3).
    """
    with pytest.raises(LookupError):
        b"x".decode("no-such-codec-xyz")


def test_normal_encodings_still_work() -> None:
    """
    Ensure other encodings still work after registration (#3).
    """
    assert "café".encode("utf-8") == b"caf\xc3\xa9"  # noqa: UP012


def test_codec_info_exposes_all_interfaces() -> None:
    """
    Ensure the registry entry exposes the public codec classes.
    """
    info = codecs.lookup("t.61")

    assert info.incrementalencoder is t61codec.IncrementalEncoder
    assert info.incrementaldecoder is t61codec.IncrementalDecoder
    assert info.streamreader is t61codec.StreamReader
    assert info.streamwriter is t61codec.StreamWriter


def test_tables_are_not_public() -> None:
    """
    Ensure the 2.x charmap tables are no longer part of the public API.
    """
    assert not hasattr(t61codec, "DECODING_TABLE")
    assert not hasattr(t61codec, "ENCODING_TABLE")


def test_version_is_non_empty_string() -> None:
    """
    Ensure the package exposes its version as a non-empty string.
    """
    assert isinstance(t61codec.__version__, str)
    assert t61codec.__version__ != ""


def test_version_falls_back_when_not_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure a missing distribution (vendored copy) yields a placeholder version.
    """

    def missing(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    spec = importlib.util.spec_from_file_location("t61codec_fresh", t61codec.__file__)
    assert spec is not None
    assert spec.loader is not None
    fresh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fresh)

    assert fresh.__version__ == "0+unknown"
