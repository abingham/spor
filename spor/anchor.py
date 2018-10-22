import linecache
import pathlib

import yaml


class Span:
    def __init__(self, offset, text):
        if offset < 0:
            raise ValueError("Span offset {} is less than 0".format(offset))

        self._offset = offset
        self._text = text

    @property
    def offset(self):
        return self._offset

    @property
    def text(self):
        return self._text

    def __repr__(self):
        return "Span(offset={}, text={})".format(self._offset, self.text)


class Context:
    def __init__(self, topic, before, after):
        if not before.offset <= topic.offset:
            raise ValueError(
                "Context 'before' must not start after the topic")

        if not after.offset > topic.offset:
            raise ValueError(
                "Context 'after' must start after the topic.")

        self._before = before
        self._topic = topic
        self._after = after

    @property
    def before(self):
        return self._before

    @property
    def topic(self):
        return self._topic

    @property
    def after(self):
        return self._after

    @property
    def full(self):
        return self.before.text + self.topic.text + self.after.text

    def __repr__(self):
        return 'Context:\n  text: {}\n  before: {}\n  after: {}'.format(
            self.topic, self.before, self.after)


class Anchor:
    def __init__(self, file_path, context, context_width, metadata):
        self.file_path = file_path
        self.context = context
        self.context_width = context_width
        self.metadata = metadata

    def __repr__(self):
        return 'Anchor(file_path={}, offset={}, length={})'.format(
            self.file_path,
            self.context.topic.offset,
            len(self.context.topic.text))


def _make_context(file_path, offset, width, context_width):
    with file_path.open(mode='rt') as handle:
        # read topic
        handle.seek(offset)
        topic = handle.read(width)
        if len(topic) < width:
            raise ValueError(
                "Unable to read topic of length {} from {} at offset {}".format(
                    width, file_path, offset))
        topic_span = Span(offset, topic)

        # read before
        before_offset = max(0, offset - context_width)
        before_width = offset - before_offset
        handle.seek(before_offset)
        before_text = handle.read(before_width)
        if len(before_text) < before_width:
            raise ValueError(
                "Unable to read before-text of length {} from {} at offset {}".format(
                    before_width, file_path, before_offset))
        before_span = Span(before_offset, before_text)

        # read after
        after_offset = offset + width
        handle.seek(after_offset)
        after_text = handle.read(context_width)
        after_span = Span(after_offset, after_text)

        return Context(topic_span, before_span, after_span)


def make_anchor(file_path,
                offset,
                width,
                context_width,
                metadata,
                root=None):
    root = pathlib.Path.cwd() if root is None else root
    full_path = root / file_path

    context = _make_context(full_path, offset, width, context_width)
    return Anchor(
        file_path=file_path.resolve().relative_to(root),
        context=context,
        context_width=context_width,
        metadata=metadata)


def _span_representer(dumper, span):
    return dumper.represent_mapping(
        '!spor_span',
        {
            'offset': span.offset,
            'text': span.text,
        })


def _span_constructor(loader, node):
    value = loader.construct_mapping(node)
    return Span(**value)


yaml.add_representer(Span, _span_representer)
yaml.add_constructor('!spor_span', _span_constructor)


def _context_representer(dumper, context):
    return dumper.represent_mapping(
        '!spor_context',
        {
            'before': context.before,
            'after': context.after,
            'topic': context.topic
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
