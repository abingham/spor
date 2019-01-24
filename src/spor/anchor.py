"""The data structures for anchoring.

Anchors are at the heart of spor. They associate a range of source code in some
file with some metadata. An anchor is defined by two elements:

    1. An offset into a file.
    2. The width of the anchor.

These tell you what the anchor applies to or refers to. Beyond that, though, the
anchor tracks what the anchored region and the regions around it looked like
when the anchor was created. This is important so that we can detect when the
anchor is out of date.
"""
from contextlib import contextmanager
import pathlib


class Context:
    """A region inside a file along with bracketing text.

    A Context defines what part of a file an anchor refers to, and it keeps
    track of the text before, in, and after the anchored region. The *topic* of
    an context is the text addressed by the anchor. The *before* is the text
    before the topic, and *after* is the text after it. It looks like this:

        Text before the anchor text in the topic text after the anchor.
               <--- before ---><-- topic ------><--- after --->

    Here, the topic is "text in the topic". The before is "fore the anchor ",
    and after is " text after the".    

    Contexts also have a nominal *width* which is the ideal size of the before
    and after text. When a Context is created, the user may request a specific
    width, but there may not be sufficient characters in the source code to
    create a before or after chunk of that size. For example, if the topic ends
    3 characters from the end of the file and the user requests a width of 10,
    the after chunk will be only three characters wide while the width will be
    10. If the file changes and the anchor is recalculate, it may that there are
    enough characters to fill out a full 10-width after chunk. So width is
    nominal or prescribed.
    """
    def __init__(self, offset, topic, before, after, width):
        if offset < 0:
            raise ValueError("Context offset {} is less than 0".format(offset))

        if len(before) > width:
            raise ValueError('before text cannot be larger than width ({})'.format(width))

        if len(after) > width:
            raise ValueError('after text cannot be larger than width ({})'.format(width))

        self._before = before
        self._offset = offset
        self._topic = topic
        self._after = after
        self._width = width

    @property
    def before(self):
        "The text before the topic."
        return self._before

    @property
    def offset(self):
        "The offset of the topic in the source."
        return self._offset

    @property
    def topic(self):
        "The text of the topic."
        return self._topic

    @property
    def after(self):
        "The text after the topic."
        return self._after

    @property
    def width(self):
        """The nominal width of the context.

        Width means how many characters/codepoints should ideally be in the
        `before` and `after` chunks. These chunks may be smaller than `width` if
        there aren't enough characters in the source to fill them.
        """
        return self._width

    @property
    def full_text(self):
        return self.before + self.topic + self.after

    def __eq__(self, rhs):
        return all((
            self.before == rhs.before,
            self.offset == rhs.offset,
            self.topic == rhs.topic,
            self.after == rhs.after,
            self.width == rhs.width,
        ))


    def __repr__(self):
        return 'Context(offset={}, topic="{}", before="{}", after="{}", width={})'.format(
            self.offset, self.topic, self.before, self.after, self.width)


class Anchor:
    """Metadata associated with a specific range of text in a file.

    Anchors let you attach metadata to pieces of text without needing to modify
    the text itself.

    Args:
        file_path: The path to the file being anchored.
        encoding: The encoding of the file being anchored.
        context: The `Context` of the anchor (i.e. its location)
        metadata: The JSON-serializable data of the anchor.
    """
    def __init__(self, file_path, encoding, context, metadata):
        if not file_path.is_absolute():
            raise ValueError("Anchors file-paths must be absolute.")

        self.file_path = file_path
        self.encoding = encoding
        self.context = context
        self.metadata = metadata

    def __eq__(self, rhs):
        return all((
            self.file_path == rhs.file_path,
            self.encoding == rhs.encoding,
            self.context == rhs.context,
            self.metadata == rhs.metadata
        ))

    def __repr__(self):
        return 'Anchor(file_path="{}", context={}, metadata={})'.format(
            self.file_path, self.context, self.metadata)


def _make_context(handle, offset, width, context_width):
    if context_width < 0:
        raise ValueError(
            'Context width must not be negative')

    # read topic
    handle.seek(offset)
    topic = handle.read(width)
    if len(topic) < width:
        raise ValueError(
            "Unable to read topic of length {} at offset {}".format(
                width, offset))

    # read before
    before_offset = max(0, offset - context_width)
    before_width = offset - before_offset
    handle.seek(before_offset)
    before = handle.read(before_width)
    if len(before) < before_width:
        raise ValueError(
            "Unable to read before-text of length {} at offset {}".format(
                before_width, before_offset))

    # read after
    after_offset = offset + width
    handle.seek(after_offset)
    after = handle.read(context_width)

    return Context(offset, topic, before, after, width=context_width)


def make_anchor(file_path: pathlib.Path,
                offset: int,
                width: int,
                context_width: int,
                metadata,
                encoding: str = 'utf-8',
                handle=None):
    """Construct a new `Anchor`.

    Args:
        file_path: The absolute path to the target file for the anchor.
        offset: The offset of the anchored text in codepoints in `file_path`'s
            contents.
        width: The width in codepoints of the anchored text.
        context_width: The width in codepoints of context on either side of the
            anchor.
        metadata: The metadata to attach to the anchor. Must be json-serializeable.
        encoding: The encoding of the contents of `file_path`.
        handle: If not `None`, this is a file-like object the contents of which
            are used to calculate the context of the anchor. If `None`, then
            the file indicated by `file_path` is opened instead.

    Raises:
        ValueError: `width` characters can't be read at `offset`.
        ValueError: `file_path` is not absolute.

    """

    @contextmanager
    def get_handle():
        if handle is None:
            with file_path.open(mode='rt', encoding=encoding) as fp:
                yield fp
        else:
            yield handle

    with get_handle() as fp:
        context = _make_context(fp, offset, width, context_width)

    return Anchor(
        file_path=file_path,
        encoding=encoding,
        context=context,
        metadata=metadata)
