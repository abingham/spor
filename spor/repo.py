import os
import pathlib
import uuid

import yaml

from .anchor import make_anchor


def _find_root_dir(path, spor_dir):
    """Search for a spor repo containing `path`.

    This searches for `spor_dir` in directories dominating `path`. If a
    directory containing `spor_dir` is found, then that directory is returned
    as a `pathlib.Path`.

    Returns: The dominating directory containing `spor_dir` as a
      `pathlib.Path`.

    Raises:
      ValueError: No repository is found.

    """
    path = pathlib.Path(os.getcwd() if path is None else path)

    while True:
        data_dir = path / spor_dir
        if data_dir.exists() and data_dir.is_dir():
            return path

        if path == pathlib.Path(path.root):
            raise ValueError('No spor repository found')

        path = path.parent.resolve()


class Repository:
    def __init__(self, path, spor_dir='.spor'):
        self._root = _find_root_dir(path, spor_dir)
        self._spor_dir = self.root / spor_dir

    @property
    def root(self):
        """The root directory of the repository."""
        return self._root

    @staticmethod
    def initialize(path, spor_dir='.spor'):
        """Initialize a spor repository in `path` if one doesn't already exist.

        Raises:
          ValueError: A repository already exists at `path`.
        """
        path = pathlib.Path(path)
        spor_path = path / spor_dir
        if spor_path.exists():
            raise ValueError(
                'spor directory already exists: {}'.format(
                    spor_path))
        spor_path.mkdir()

    def add(self, metadata, file_path, line_number, columns=None):
        anchor = make_anchor(
            context_size=3,  # TODO: This needs to be configurable
            file_path=file_path.resolve().relative_to(self.root),
            line_number=line_number,
            metadata=metadata,
            columns=columns,
            root=self.root)

        anchor_id = uuid.uuid4().hex
        anchor_path = self._anchor_path(anchor_id)
        with anchor_path.open(mode='wt') as f:
            yaml.dump(anchor, f)

        return anchor_id

    def __getitem__(self, anchor_id):
        file_path = self._anchor_path(anchor_id)

        try:
            with file_path.open(mode='rt') as handle:
                return yaml.load(handle.read())
        except OSError:
            raise KeyError(
                'No anchor with id {}'.format(anchor_id))

    def update(self, anchor_id, metadata):
        anchor = self[anchor_id]
        anchor.metadata = metadata
        with self._anchor_path(anchor_id).open(mode='wt') as f:
            yaml.dump(anchor, f)

    def __delitem__(self, anchor_id):
        try:
            self._anchor_path(anchor_id).unlink()
        except OSError:
            raise KeyError(
                'No anchor with id {}'.format(anchor_id))

    def __iter__(self):
        for spor_file in self._spor_dir.glob('**/*.yml'):
            yield str(spor_file.name)[:-4]

    def items(self):
        for anchor_id in self:
            try:
                anchor = self[anchor_id]
            except KeyError:
                assert False, 'Trying to load from missing file or something'

            yield (anchor_id, anchor)

    def _anchor_path(self, anchor_id):
        "Absolute path to the data file for `anchor_id`."
        file_name = '{}.yml'.format(anchor_id)
        file_path = self._spor_dir / file_name
        return file_path
