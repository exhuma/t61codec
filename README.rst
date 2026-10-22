Python Codec for ITU T.61 Strings
=================================

.. image:: https://img.shields.io/pypi/v/t61codec.svg
   :target: https://pypi.org/project/t61codec/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/t61codec.svg
   :target: https://pypi.org/project/t61codec/
   :alt: Supported Python versions

.. image:: https://github.com/exhuma/t61codec/actions/workflows/pythonpackage.yml/badge.svg
   :target: https://github.com/exhuma/t61codec/actions/workflows/pythonpackage.yml
   :alt: CI status

.. image:: https://github.com/exhuma/t61codec/actions/workflows/docs.yml/badge.svg
   :target: https://exhuma.github.io/t61codec/
   :alt: Documentation

A Python codec for ITU-T Rec. T.61 (11/1988), the 8-bit Teletex code,
implemented to the letter of the recommendation: accented letters are
composed from their diacritic prefix, only the combinations of Figure B-1
are accepted, and undefined bytes and control functions are errors.

Documentation: https://exhuma.github.io/t61codec/

For background see https://en.wikipedia.org/wiki/ITU_T.61 and
https://www.itu.int/rec/T-REC-T.61-198811-S/en


Project status
--------------

The codec implements a fixed standard (ITU-T T.61, 1988) and is
feature-complete. The project is in maintenance mode: only bug fixes, support
for new Python versions and security fixes are accepted. Feature requests will
be declined unless a change in Python itself requires one. Semantic Versioning
applies.

Upgrading from 2.x
~~~~~~~~~~~~~~~~~~

Version 3.0.0 changes the decoding and encoding results to follow the
recommendation exactly. Please read the `changelog
<https://github.com/exhuma/t61codec/blob/master/CHANGES.rst>`_ before
upgrading.


Installation
------------

Installation follows the standard Python procedure:

::

    pip install t61codec


The package uses Semantic Versioning 2.0 (https://semver.org/spec/v2.0.0.html).


Usage
-----

The codec can be registered into Python's codec registry. A helper method has
been provided::

    import t61codec
    t61codec.register()

Please see the notes on `codecs.register
<https://docs.python.org/3/library/codecs.html#codecs.register>`_!

After registering, the codec is available as either ``'t61'`` or ``'t.61'``::

    >>> b'Hello T.61: \xe0'.decode('t.61')
    'Hello T.61: Ω'
    >>> 'Hello T.61: Ω'.encode('t.61')
    b'Hello T.61: \xe0'
    >>> b'Caf\xc2e'.decode('t.61')
    'Café'
    >>> 'Café'.encode('t.61')
    b'Caf\xc2e'

Real-world T61String data (for example in X.509 certificates) is often
Latin-1 rather than T.61, because OpenSSL treats it that way. This codec
decodes strictly according to T.61, so such data may raise errors or
decode differently.
