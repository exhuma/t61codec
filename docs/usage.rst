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
   text = b"Hello T.61: \xe0".decode("t.61")
   print(text)
   # Hello T.61: Ω

   # Encode a Python string to T.61 bytes
   raw = "Hello T.61: \u2126".encode("t.61")
   print(raw)
   # b'Hello T.61: \xe0'

The codec can be referenced by either ``"t61"`` or ``"t.61"``.

Error handling
--------------

The standard Python error-handling modes work as expected:

.. code-block:: python

   import t61codec

   t61codec.register()

   # Characters with no T.61 mapping raise UnicodeEncodeError by default
   try:
       "\u20ac".encode("t.61")        # Euro sign has no T.61 mapping
   except UnicodeEncodeError as exc:
       print(exc)

   # Use 'replace' to substitute unmapped characters with '?'
   result = "\u20ac Hello".encode("t.61", errors="replace")
   print(result)
   # b'? Hello'

   # Use 'ignore' to silently drop unmapped characters
   result = "\u20ac Hello".encode("t.61", errors="ignore")
   print(result)
   # b' Hello'

Low-level API
-------------

You can also use the codec classes directly without registering:

.. code-block:: python

   import t61codec

   codec = t61codec.Codec()
   raw, length = codec.encode("Hello \u2126")
   print(raw)    # b'Hello \xe0'
   print(length) # 7

   text, length = codec.decode(b"Hello \xe0")
   print(text)   # Hello Ω
