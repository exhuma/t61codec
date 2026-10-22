Usage
=====

Installation
------------

.. code-block:: console

   $ pip install t61codec

Quick start
-----------

Register the codec once at application startup, then use it like any other
Python encoding:

.. code-block:: python

   import t61codec

   t61codec.register()

   # Decode T.61 bytes to a Python string
   text = b"Hello T.61: \xe0 Caf\xc2e".decode("t.61")
   print(text)
   # Hello T.61: Ω Café

   # Encode a Python string to T.61 bytes
   raw = "Hello T.61: Ω Café".encode("t.61")
   print(raw)
   # b'Hello T.61: \xe0 Caf\xc2e'

The codec can be referenced by either ``"t61"`` or ``"t.61"``.

What the codec accepts
----------------------

The codec implements ITU-T Rec. T.61 (11/1988) to the letter. The API
reference has the full rules; in short:

* Accented letters are a diacritic byte followed by the base letter
  (``b"\xc2e"`` is ``é``). Only the combinations listed in Figure B-1 of
  the recommendation are valid, and they decode to precomposed
  characters. A diacritic followed by a space is the spacing accent.
* Encoding normalises the text to NFC first, so ``"e\N{COMBINING ACUTE
  ACCENT}"`` and ``"é"`` both give ``b"\xc2e"``.
* The non-spacing underline (0xCC) decodes to the base character followed
  by U+0332 COMBINING LOW LINE, and vice versa.
* 0xE0 decodes to U+03A9 (Ω) and 0xE2 to U+0110 (Đ). The encoder also
  accepts U+2126 OHM SIGN and U+00D0 (Ð).
* Only the control functions BS, LF, FF, CR, SUB (decode only), PLD, PLU
  and CSI are accepted. Tabs, NUL and all other controls are errors.

.. note::

   OpenSSL treats T61String as Latin-1, so "T.61" data found in X.509
   certificates is often Latin-1 in practice. This codec decodes it
   according to T.61, which may raise errors or change accented
   characters.

Error handling
--------------

The standard Python error-handling modes work in both directions:

.. code-block:: python

   import t61codec

   t61codec.register()

   # Characters with no T.61 mapping raise UnicodeEncodeError by default
   try:
       "€".encode("t.61")
   except UnicodeEncodeError as exc:
       print(exc)

   # Use 'replace' to substitute unmapped characters with '?'
   print("€ Hello".encode("t.61", errors="replace"))
   # b'? Hello'

   # Use 'ignore' to silently drop unmapped characters
   print("€ Hello".encode("t.61", errors="ignore"))
   # b' Hello'

   # Decode errors span one byte; decoding resumes right after it
   print(b"\xc2b\tc".decode("t.61", errors="replace"))
   # �b�c

``backslashreplace`` cannot be used for encoding, because T.61 has no
backslash: it raises the original :class:`UnicodeEncodeError`.

Incremental and stream use
--------------------------

The incremental decoder, the stream reader and text files opened with
``encoding="t.61"`` keep a diacritic at the end of one chunk until the next
one arrives.

The incremental encoder and the stream writer encode each chunk on its own.
Write a character and its combining marks in the same call, or pass
precomposed text.

Low-level API
-------------

You can also use the codec classes directly without registering:

.. code-block:: python

   import t61codec

   codec = t61codec.Codec()
   raw, length = codec.encode("Hello Ω")
   print(raw)    # b'Hello \xe0'
   print(length) # 7

   text, length = codec.decode(b"Hello \xe0")
   print(text)   # Hello Ω
