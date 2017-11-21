import os
import pathlib
import linecache
import uuid

import yaml

from .anchor import Anchor, Context


def find_spor_repo(path=None, spor_dir='.spor'):
    path = path or pathlib.Path(os.getcwd())

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
        self.repo_path = find_spor_repo(pathlib.Path(path))

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
            file_path=file_path.relative_to(self.repo_path.parent),
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

    def find(self, file_path, line_number, columns=None):
        file_path = file_path.relative_to(self.repo_path.parent)
        return (
            anchor
            for anchor in self
            if anchor.file_path == file_path
            if anchor.line_number == line_number
            # TODO: Match columns
        )

    def set(self, anchor_id, metadata):
        file_name = '{}.yml'.format(anchor_id)
        file_path = self.repo_path / file_name
        with open(file_path, mode='rt') as f:
            anchor = yaml.load(f.read())
        anchor.metadata = metadata
        with open(file_path, mode='wt') as f:
            yaml.dump(anchor, f)

    def delete(self, anchor_id):
        file_name = '{}.yml'.format(anchor_id)
        file_path = self.repo_path / file_name
        file_path.unlink()

    def __iter__(self):
        for spor_file in self.repo_path.glob('**/*.yml'):
            with open(spor_file) as handle:
                yield yaml.load(handle.read())
