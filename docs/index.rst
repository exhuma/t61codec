t61codec
========

A Python codec for ITU-T Rec. T.61 (11/1988), the 8-bit Teletex character
set. T.61 text appears in X.500 directories, LDAP and the ``T61String`` type
of X.509 certificates. The codec follows the recommendation to the letter:
accented letters are composed from a diacritic prefix, and undefined bytes
and control functions are errors.

Install
-------

.. code-block:: console

   $ pip install t61codec

Example
-------

Register the codec once at startup. It is then available as ``"t61"`` and
``"t.61"``:

.. code-block:: python

   import t61codec

   t61codec.register()

   b"Caf\xc2e \xe0".decode("t.61")  # 'Café Ω'
   "Café Ω".encode("t.61")          # b'Caf\xc2e \xe0'

.. note::

   OpenSSL treats ``T61String`` as Latin-1, so "T.61" data in X.509
   certificates is often Latin-1 in practice. This codec decodes it as T.61,
   which may raise errors or change accented characters.

Project status
--------------

The standard is fixed and the codec is feature-complete. The project is in
maintenance mode: it accepts bug fixes, support for new Python versions and
security fixes. Versions follow `Semantic Versioning
<https://semver.org/spec/v2.0.0.html>`_. Version 3.0.0 changed decoding and
encoding results to match the recommendation; read the :doc:`changelog
<changes>` before upgrading from 2.x.

Contents
--------

:doc:`usage`
   Which input the codec accepts, error handling, and incremental and stream
   use.

:doc:`api`
   The public functions and codec classes.

:doc:`changes`
   Changes in every release.

.. toctree::
   :hidden:

   usage
   api
   changes
