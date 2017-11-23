|Python version| |Build Status|

======
 spor
======

A system for anchoring metadata in external files to source code.

spor lets you define metadata for elements of your source code. The
metadata is kept in a separate file from your source code, meaning that
you don't need to clutter your source file with extra information
encoded into comments. To accomplish this while dealing with the fact
that source code changes over time, spor uses various "anchoring"
techniques to keep the metadata in sync with the source code (or let you
know when they become unmanageably out of sync).

Motivation
==========

My main motivation for this tool comes from my work on the mutation
testing tool `Cosmic Ray <https://github.com/sixty-north/cosmic-ray>`__.
CR users need to be able to specify sections of their source code which
should not be mutated, or which should only be mutated in specific ways.
Rather than having them embed these processing directives in the source
code, I thought it would be cleaner and neater to let them do so with a
separate metadata file.

Features
========

spor needs support for the following functionality:

1. Add/edit/delete metadata to a specific range of text in a source file
2. Query existing metadata
3. Automatically update metadata when possible, or report errors when
   not
4. Provide facilities facilities for "updating" metadata with new
   anchoring data

The design needs to be sensitive to both human users (i.e. since they
may need to manually work with the metadata from time to time) as well
as programmatic users. I'm sure the design will evolve as we go, so I'm
going to try to keep it simple and explicit at first.

Ideally spor will work on any programming language (and, really, any
text document), though its initial target will be Python source code.

Tests
=====

To run the tests, first install the test dependencies and then use |tox|:

.. code-block::

  pip install -e .[test]
  tox

Notes
=====

The field of "anchoring" is not new, and there's some existing work we
need to pay attention to:

-  "Metadata Anchoring for Source Code: Robust Location Descriptor
   Definition, Building and Interpreting",
   https://www.researchgate.net/profile/Maria\_Bielikova/publication/259892218\_Metadata\_Anchoring\_for\_Source\_Code\_Robust\_Location\_Descriptor\_Definition\_Building\_and\_Interpreting/links/560478cb08aeb5718ff00039.pdf

.. |Python version| image:: https://img.shields.io/badge/Python_version-3.4+-blue.svg
   :target: https://www.python.org/
.. |Build Status| image:: https://travis-ci.org/abingham/spor.png?branch=master
   :target: https://travis-ci.org/abingham/spor
.. |tox| replace:: `tox`
   :target: https://tox.readthedocs.io/en/latest/
