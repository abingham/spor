import os
import pathlib
import linecache
import uuid

import yaml

from .anchor import Anchor, Context


def _find_spor_repo(path, spor_dir):
    path = pathlib.Path(os.getcwd() if path is None else path)

    while True:
        spor_path = path / spor_dir
        if spor_path.exists() and spor_path.is_dir():
            return spor_path

        if path == pathlib.Path(path.root):
            raise ValueError('No spor repository found')

        path = path.parent.resolve()


def _read_line(file_name, line_number):
    """Read the specified line from a file, returning `None` if there is no such
    line.

    Newlines will be stripped from the lines.
    """
    line = linecache.getline(file_name, line_number)
    return None if line == '' else line


def _make_context(context_size, file_name, line_number):
    line = _read_line(file_name, line_number)

    if line is None:
        raise IndexError('No line {} in {}'.format(line_number, file_name))

    before = filter(
        lambda l: l is not None,
        (_read_line(file_name, n)
         for n in range(line_number - context_size,
                        line_number)))
    after = filter(
        lambda l: l is not None,
        (_read_line(file_name, n)
         for n in range(line_number + 1,
                        line_number + 1 + context_size)))

    return Context(
        line=line,
        before=before,
        after=after)


class Store:
    def __init__(self, path, spor_dir='.spor'):
        self.repo_path = _find_spor_repo(path, spor_dir)

    @staticmethod
    def initialize(path, spor_dir='.spor'):
        path = pathlib.Path(path)
        spor_path = path / spor_dir
        if spor_path.exists():
            raise ValueError(
                'spor directory already exists: {}'.format(
                    spor_path))
        spor_path.mkdir()

    def tracked_file(self, anchor):
        return self.repo_path.parent / anchor.file_path

    def make_anchor(self, context_size, file_path, line_number, metadata,
                    columns=None):
        context = _make_context(context_size, str(file_path), line_number)
        return Anchor(
            file_path=file_path.resolve().relative_to(self.repo_path.parent),
            context=context,
            metadata=metadata,
            line_number=line_number,
            columns=columns)

    def add(self, metadata, file_path, line_number, columns=None):
        anchor_id = uuid.uuid4().hex
        data_path = self.repo_path / '{}.yml'.format(anchor_id)

        anchor = self.make_anchor(
            context_size=3,  # TODO: This needs to be configurable
            file_path=file_path,
            line_number=line_number,
            metadata=metadata,
            columns=columns)

        with open(data_path, mode='wt') as f:
            yaml.dump(anchor, f)

        return anchor_id

    def _anchor_path(self, anchor_id):
        file_name = '{}.yml'.format(anchor_id)
        file_path = self.repo_path / file_name
        return file_path

    def __getitem__(self, anchor_id):
        file_path = self._anchor_path(anchor_id)

        try:
            with open(file_path, mode='rt') as handle:
                return yaml.load(handle.read())
        except OSError:
            raise KeyError(
                'No anchor with id {}'.format(anchor_id))

    def __setitem__(self, anchor_id, metadata):
        anchor = self.get(anchor_id)
        anchor.metadata = metadata
        with open(self._anchor_path(anchor_id), mode='wt') as f:
            yaml.dump(anchor, f)

    def __delitem__(self, anchor_id):
        try:
            self._anchor_path(anchor_id).unlink()
        except OSError:
            raise KeyError(
                'No anchor with id {}'.format(anchor_id))

    def __iter__(self):
        for spor_file in self.repo_path.glob('**/*.yml'):
            anchor_id = str(spor_file.name())[:-4]

            try:
                anchor = self[anchor_id]
            except KeyError:
                assert False, 'Trying to load from missing file or something'

            yield (anchor_id, anchor)
