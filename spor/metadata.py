import pathlib


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


class Metadata:
    def __init__(self, filename, line_number, context, metadata):
        self.filename = pathlib.Path(filename)
        self.line_number = line_number
        self.context = context
        self.metadata = metadata

    def __repr__(self):
        return 'Metadata(filename={}, line_number={})'.format(
            self.filename, self.line_number)


def make_metadata(yml):
    before = yml['context']['before']
    after = yml['context']['after']
    line = yml['context']['line']
    ctx = Context(line, before, after)

    filename = yml['filename']
    line_number = yml['line_number']
    metadata = yml['metadata']

    return Metadata(filename, line_number, ctx, metadata)
