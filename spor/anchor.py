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
