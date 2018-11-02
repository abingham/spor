from contextlib import contextmanager
import pathlib


class Context:
    def __init__(self, offset, topic, before, after, width):
        if offset < 0:
            raise ValueError("Context offset {} is less than 0".format(offset))

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
        "The nominal width of the context."
        return self._width

    @property
    def full_text(self):
        return self.before + self.topic + self.after

    def __repr__(self):
        return 'Context(offset={}, topic="{}", before="{}", after="{}", width={})'.format(
            self.offset, self.topic, self.before, self.after, self.width)


class Anchor:
    def __init__(self, file_path, encoding, context, metadata):
        if not file_path.is_absolute():
            raise ValueError("Anchors file-paths must be absolute.")

        self.file_path = file_path
        self.encoding = encoding
        self.context = context
        self.metadata = metadata

    def __repr__(self):
        return 'Anchor(file_path={}, context={}, metadata={})'.format(
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
