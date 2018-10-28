import json
import pathlib


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
        if not file_path.is_absolute():
            raise ValueError("Anchors file-paths must be absolute.")

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
                metadata):
    """Construct a new `Anchor`.

    Raises:
        ValueError: `width` characters can't be read at `offset`.
        ValueError: `file_path` is not absolute.
    """
    context = _make_context(file_path, offset, width, context_width)
    return Anchor(
        file_path=file_path,
        context=context,
        context_width=context_width,
        metadata=metadata)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Anchor):
            return {
                '!spor_anchor': {
                    # TODO: Remove repository root from front.
                    'file_path': str(obj.file_path),
                    'context': obj.context,
                    'context_width': obj.context_width,
                    'metadata': obj.metadata
                }
            }
        elif isinstance(obj, Context):
            return {
                '!spor_context': {
                    'before': obj.before,
                    'after': obj.after,
                    'topic': obj.topic,
                    'offset': obj.offset
                }
            }

        return super().default(self, obj)


class JSONDecoder(json.JSONDecoder):
    def __init__(self):
        super().__init__(object_hook=JSONDecoder.object_hook)

    @staticmethod
    def object_hook(dct):
        if '!spor_anchor' in dct:
            data = dct['!spor_anchor']
            return Anchor(
                # TODO: Add repo too to front
                file_path=pathlib.Path(data['file_path']),
                context=data['context'],
                context_width=data['context_width'],
                metadata=data['metadata'])
        elif '!spor_context' in dct:
            return Context(**dct['!spor_context'])
        return dct
