v3.0.0
======

The codec now follows ITU-T T.61 (11/1988) to the letter. This is the final
feature release: the project is in maintenance mode (bug fixes, support for new
Python versions and security fixes only).

Breaking changes (spec conformance, #4)
---------------------------------------

Decoding:

* A diacritic (0xC1-0xCF) followed by a base letter now yields the precomposed
  character (``b"Caf\xc2e"`` decodes to ``"Café"``). Previously a standalone
  combining mark was emitted *before* the letter.
* Only the 155 combinations of Figure B-1 are valid. Anything else raises, for
  example ``C7 69``, ``CB 67``, ``C2 62`` or a diacritic before a control.
* ``C2 67`` decodes to ``ǵ`` (U+01F5).
* A diacritic followed by SPACE yields the spacing accent (``b"\xc2 "`` is
  ``"´"``, ``b"\xc4 "`` is ``"~"``).
* A trailing diacritic or underline raises "unexpected end of data". It used to
  be emitted as a standalone mark.
* 0xCE is the ogonek (``b"\xcea"`` is ``"ą"``); it used to give U+032B.
* 0xCC (non-spacing underline) yields the base character plus U+0332. It works
  over accented letters and SPACE, with PLD/PLU allowed in between.
* 0xC9 is now decoded as an alias of 0xC8 (it used to be an error).
* 0xE0 decodes to U+03A9 (was U+2126) and 0xE2 to U+0110 (was U+00D0).
* 0x23 and 0x24 decode to ``#`` and ``¤`` (they used to be errors).
* 0xA0 (was NBSP) and 0x7F (was DEL) now raise.
* All C0/C1 controls except BS, LF, FF, CR, SUB, PLD, PLU and CSI now raise.
  This includes HT, NUL, VT, ESC and 0x80-0x9F apart from 0x8B, 0x8C and 0x9B.
* Every decode error spans exactly one byte and decoding resumes at the next
  byte.
* The incremental decoder and ``StreamReader`` buffer a trailing prefix across
  chunks. ``StreamReader.read()`` raises for a prefix left at EOF.

Encoding:

* Input is NFC-normalised, so precomposed and decomposed text both encode to
  ``b"\xc2e"``. Previously decomposed input came out in the wrong order and
  precomposed input failed.
* Accented letters are encoded as diacritic + base letter. Base + U+0332 is
  encoded with 0xCC first.
* U+03A9 and U+2126 both encode to 0xE0; U+0110 and U+00D0 both encode to 0xE2.
* ``#`` encodes to 0xA6 and ``¤`` to 0xA8. 0x23, 0x24 and 0xC9 are never
  emitted.
* These now raise: SUB, HT, NUL, DEL, NBSP, a leading or standalone combining
  mark and combinations not listed in Figure B-1 (such as ``"q\u0301"``).
* ``backslashreplace`` raises a clear error when encoding, since ``\`` is not
  part of T.61.
* ``IncrementalEncoder`` and ``StreamWriter``: a combining mark must arrive in
  the same chunk as its base letter.

Public API:

* ``t61codec.DECODING_TABLE`` and ``t61codec.ENCODING_TABLE`` were removed (the
  tables are now private, in ``t61codec._tables``).
* ``StreamReader.decode`` gained ``final: bool = False``.
* ``IncrementalDecoder`` now subclasses ``codecs.BufferedIncrementalDecoder``.

Fixes
-----

* ``search_function`` returns ``None`` for unknown codec names (#3). Once
  registered, it used to raise ``RecursionError`` (2.0.0) or ``AttributeError``
  (1.0.1).

Packaging
---------

* Requires Python 3.11 or newer (2.0.0 required 3.6).
* The package is typed: it ships ``py.typed`` and passes ``mypy --strict``.
* PEP 639 license metadata. ``Development Status :: 6 - Mature``: the project
  is in maintenance mode.
* ``src`` layout, ``uv``, ``ruff`` and Sphinx documentation on Read the Docs.
* Releases are published through PyPI Trusted Publishing.


v2.0.0
======

Dropped Support for Python 2 (min version is now 3.6)


v1.0.1
======

Fix for Python 2


v1.0.0.post1
============

Added README with example code & changelog.


v1.0.0
======

Initial Release
