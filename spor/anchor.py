import linecache
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


def context_representer(dumper, context):
    return dumper.represent_mapping(
        '!spor_context',
        {
            'before': list(context.before),
            'after': list(context.after),
            'line': context.line
        })


def context_constructor(loader, node):
    value = loader.construct_mapping(node)
    return Context(**value)


yaml.add_representer(Context, context_representer)
yaml.add_constructor('!spor_context', context_constructor)


class Anchor:
    def __init__(self, filename, context, metadata, line_number, columns=None):
        self.filename = pathlib.Path(filename)
        self.line_number = line_number
        self.columns = columns
        self.context = context
        self.metadata = metadata

    def __repr__(self):
        return 'Metadata(filename={}, line_number={}, columns={})'.format(
            self.filename, self.line_number, self.columns)


def anchor_representer(dumper, anchor):
    return dumper.represent_mapping(
        '!spor_anchor',
        {
            'filename': str(anchor.filename),
            'line_number': anchor.line_number,
            'columns': anchor.columns,
            'context': anchor.context,
            'metadata': anchor.metadata,
        })


def anchor_constructor(loader, node):
    value = loader.construct_mapping(node)
    return Anchor(**value)


yaml.add_representer(Anchor, anchor_representer)
yaml.add_constructor('!spor_anchor', anchor_constructor)


def _read_line(filepath, line_number):
    """Read the specified line from a file, returning `None` if there is no such
    line.

    Newlines will be stripped from the lines.
    """
    line = linecache.getline(str(filepath), line_number)
    return None if line == '' else line.rstrip()


def make_context(context_size, filepath, line_number):
    line = _read_line(filepath, line_number)

    if line is None:
        raise IndexError('No line {} in {}'.format(line_number, filepath))

    before = filter(
        lambda l: l is not None,
        (_read_line(filepath, n)
         for n in range(line_number - context_size,
                        line_number)))
    after = filter(
        lambda l: l is not None,
        (_read_line(filepath, n)
         for n in range(line_number + 1,
                        line_number + 1 + context_size)))

    return Context(
        line=line,
        before=before,
        after=after)


def make_anchor(context_size, filepath, line_number, metadata, columns=None):
    path = pathlib.Path(filepath)
    context = make_context(context_size, path, line_number)
    return Anchor(
        filename=filepath,
        context=context,
        metadata=metadata,
        line_number=line_number,
        columns=columns)
