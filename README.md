# spor

A system for anchoring metadata in external files to source code.

spor lets you define metadata for elements of your source code. The metadata is
kept in a separate file from your source code, meaning that you don't need to
clutter your source file with extra information encoded into comments. To
accomplish this while dealing with the fact that source code changes over time,
spor uses various "anchoring" techniques to keep the metadata in sync with the
source code (or let you know when they become irrevocably out of sync).

## Motivation

My main motivation for this tool comes from my work on the mutation testing
tool [Cosmic Ray](https://github.com/sixty-north/cosmic-ray). CR users need to
be able to specify sections of their source code which should not be mutated, or
which should only be mutated in specific ways. Rather than having them embed
these processing directives in the source code, I thought it would be cleaner
and neater to let them do so with a separate metadata file.

## Features

spor needs support for the following functionality:

1. Add/edit/delete metadata to a specific range of text in a source file
2. Query existing metadata
3. Automatically update metadata when possible, or report errors when not
4. Provide facilities facilities for "updating" metadata with new anchoring data

The design needs to be sensitive to both human users (i.e. since they may need
to manually work with the metadata from time to time) as well as programmatic
users. I'm sure the design will evolve as we go, so I'm going to try to keep it
simple and explicit at first.

Ideally spor will work on any programming language (and, really, any text
document), though its initial target will be Python source code.

## Notes

The field of "anchoring" is not new, and there's some existing work we need to pay attention to:

* "Metadata Anchoring for Source Code: Robust Location Descriptor Definition, Building and Interpreting", https://www.researchgate.net/profile/Maria_Bielikova/publication/259892218_Metadata_Anchoring_for_Source_Code_Robust_Location_Descriptor_Definition_Building_and_Interpreting/links/560478cb08aeb5718ff00039.pdf
