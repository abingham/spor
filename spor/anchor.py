import pathlib
import yaml


class Context:
    def __init__(self, line, before=None, after=None):
        self._before = tuple(before or ())
        self._line = line
        self._after = tuple(after or ())

    @property
    def before(self):
        return self._before

    @property
    def line(self):
        return self._line

    @property
    def after(self):
        return self._after

    def __repr__(self):
        return 'Context:\n  line: {}\n  before: {}\n  after: {}'.format(
            self.line, self.before, self.after)


class Anchor:
    def __init__(self, file_path, context, metadata, line_number, columns=None):
        self.file_path = file_path
        self.line_number = line_number
        self.columns = columns
        self.context = context
        self.metadata = metadata

    def __repr__(self):
        return 'Anchor(file_path={}, line_number={}, columns={})'.format(
            self.file_path, self.line_number, self.columns)


def _context_representer(dumper, context):
    return dumper.represent_mapping(
        '!spor_context',
        {
            'before': context.before,
            'after': context.after,
            'line': context.line
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
            'line_number': anchor.line_number,
            'columns': anchor.columns,
            'context': anchor.context,
            'metadata': anchor.metadata,
        })


def _anchor_constructor(loader, node):
    value = loader.construct_mapping(node)
    value['file_path'] = pathlib.Path(value['file_path'])
    return Anchor(**value)


yaml.add_representer(Anchor, _anchor_representer)
yaml.add_constructor('!spor_anchor', _anchor_constructor)
