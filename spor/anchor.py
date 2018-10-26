import pathlib

import yaml


class Context:
    def __init__(self, offset, topic, before, after):
        if offset < 0:
            raise ValueError("Context offset {} is less than 0".format(offset))

        self._before = before
        self._offset = offset
        self._topic = topic
        self._after = after

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
    def full_text(self):
        return self.before + self.topic + self.after

    def __repr__(self):
        return 'Context(offset={}, topic="{}", before="{}", after="{}")'.format(
            self.offset, self.topic, self.before, self.after)


class Anchor:
    def __init__(self, file_path, context, context_width, metadata):
        self.file_path = file_path
        self.context = context
        self.context_width = context_width
        self.metadata = metadata

    def __repr__(self):
        return 'Anchor(file_path={}, context={}, context_width={}, metadata={})'.format(
            self.file_path, self.context, self.context_width, self.metadata)


def _make_context(file_path, offset, width, context_width):
    with file_path.open(mode='rt') as handle:
        # read topic
        handle.seek(offset)
        topic = handle.read(width)
        if len(topic) < width:
            raise ValueError(
                "Unable to read topic of length {} from {} at offset {}".format(
                    width, file_path, offset))

        # read before
        before_offset = max(0, offset - context_width)
        before_width = offset - before_offset
        handle.seek(before_offset)
        before = handle.read(before_width)
        if len(before) < before_width:
            raise ValueError(
                "Unable to read before-text of length {} from {} at offset {}".format(
                    before_width, file_path, before_offset))

        # read after
        after_offset = offset + width
        handle.seek(after_offset)
        after = handle.read(context_width)

        return Context(offset, topic, before, after)


def make_anchor(file_path,
                offset,
                width,
                context_width,
                metadata,
                root=None):
    """Construct a new `Anchor`.

    Raises:
        ValueError: `width` characters can't be read at `offset`.
    """
    root = pathlib.Path.cwd() if root is None else root
    full_path = root / file_path

    context = _make_context(full_path, offset, width, context_width)
    return Anchor(
        file_path=file_path.resolve().relative_to(root),
        context=context,
        context_width=context_width,
        metadata=metadata)


def _context_representer(dumper, context):
    return dumper.represent_mapping(
        '!spor_context',
        {
            'before': context.before,
            'after': context.after,
            'topic': context.topic,
            'offset': context.offset
        })


def _context_constructor(loader, node):
    value = loader.construct_mapping(node)
    return Context(**value)


yaml.add_representer(Context, _context_representer)
yaml.add_constructor('!spor_context', _context_constructor)


def _anchor_representer(dumper, anchor):
    return dumper.represent_mapping(
        '!spor_anchor',
        {
            'file_path': str(anchor.file_path),
            'context': anchor.context,
            'context_width': anchor.context_width,
            'metadata': anchor.metadata,
        })


def _anchor_constructor(loader, node):
    value = loader.construct_mapping(node)
    value['file_path'] = pathlib.Path(value['file_path'])
    return Anchor(**value)


yaml.add_representer(Anchor, _anchor_representer)
yaml.add_constructor('!spor_anchor', _anchor_constructor)
