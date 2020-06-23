|Python version| |Build Status|

======
 spor
======

**NB:** This Python implementation of spor has been superseded by a `Rust
implementation <https://github.com/abingham/spor>`_. This version might be
kept compatible with the Rust version, but don't count on it for now.

A system for anchoring metadata in external files to source code.

spor lets you define metadata for elements of your source code. The
metadata is kept in a separate file from your source code, meaning that
you don't need to clutter your source file with extra information
encoded into comments. To accomplish this while dealing with the fact
that source code changes over time, spor uses various "anchoring"
techniques to keep the metadata in sync with the source code (or let you
know when they become unmanageably out of sync).

Quickstart
==========

Before you can use spor to anchor metadata to files, you need to initialize a
repository with the ``init`` command::

  $ spor init

This is very similar in spirit to ``git init``. It creates a new directory in your
current directory called ``.spor``, and this is where spor will keep the
information it needs.

Now you can create anchors. Suppose you've got a file, ``example.py``, like
this:

.. code-block:: python

   # example.py


   def func(x):
       return x * 2

You can anchor metadata to line 4 (the function definition) by specifying the starting offset and anchor width like this::

  $ echo "{\"meta\": \"data\"}" | spor add example.py 32 12 10

.. pull-quote::

  You don't have to pipe the metadata into the ``add`` command. If you don't,
  spor will pop up an editor so that you can enter the metadata there.

The `10` at the end specifies the size of the "context" around the anchored code
that we use for updating anchors.

This will associate the dictionary ``{meta: data}`` with the code `return x * 2`. You can see
this metadata by using the ``list`` command::

  $ spor list example.py
  example.py:32 => {'meta': 'data'}

The metadata can be any valid JSON. spor doesn't look at the data at all, so
it's entirely up to you to decide what goes there.

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

Development
===========

Spor is new and small enough that we do fun things like try out new tools.
Instead of `setuptools` et al., we're using `poetry
<https://github.com/sdispater/poetry>`__. So if you want to contribute to spor,
the first thing you need to do is to `install poetry
<https://github.com/sdispater/poetry#installation>`__.

To install the package, use::

  poetry install

Tests
-----

The installation command above will install all of the test dependencies as
well. To run all of the tests, run |tox|_:

.. code-block::

  tox

To run just the `pytests` unit tests, run::

  poetry run pytest tests/unittests

To run the `radish` tests, run::

  poetry run radish tests/e2e/features -b tests/e2e/radish

Notes
=====

The field of "anchoring" is not new, and there's some existing work we
need to pay attention to:

- Bielikova, Maria. `"Metadata Anchoring for Source Code: Robust Location Descriptor Definition, Building and Interpreting" <https://www.researchgate.net/profile/Maria\_Bielikova/publication/259892218\_Metadata\_Anchoring\_for\_Source\_Code\_Robust\_Location\_Descriptor\_Definition\_Building\_and\_Interpreting/links/560478cb08aeb5718ff00039.pdf>`__

.. |Python version| image:: https://img.shields.io/badge/Python_version-3.4+-blue.svg
   :target: https://www.python.org/
.. |Build Status| image:: https://travis-ci.org/abingham/spor.png?branch=master
   :target: https://travis-ci.org/abingham/spor
.. |tox| replace:: ``tox``
.. _tox: https://tox.readthedocs.io/en/latest/
