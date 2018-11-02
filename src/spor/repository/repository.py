import os
import pathlib
import uuid

from .persistence import load_anchor, save_anchor


def initialize_repository(path, spor_dir='.spor'):
    """Initialize a spor repository in `path` if one doesn't already exist.

    Args:
        path: Path to any file or directory within the repository.
        spor_dir: The name of the directory containing spor data.

    Returns: A `Repository` instance.

    Raises:
        ValueError: A repository already exists at `path`.
    """
    path = pathlib.Path(path)
    spor_path = path / spor_dir
    if spor_path.exists():
        raise ValueError('spor directory already exists: {}'.format(spor_path))
    spor_path.mkdir()

    return Repository(path, spor_dir)


def open_repository(path, spor_dir='.spor'):
    """Open an existing repository.

    Args:
        path: Path to any file or directory within the repository.
        spor_dir: The name of the directory containing spor data.

    Returns: A `Repository` instance.

    Raises:
        ValueError: No repository is found.
    """
    root = _find_root_dir(path, spor_dir)
    return Repository(root, spor_dir)


class Repository:
    """Storage for anchors.
    """

    def __init__(self, root, spor_dir):
        self._root = pathlib.Path(root).resolve()
        self._spor_dir = self.root / spor_dir
        if not self._spor_dir.exists():
            raise ValueError("Repository directory does not exist: {}".format(
                self._spor_dir))

    @property
    def root(self):
        """The root directory of the repository."""
        return self._root

    def add(self, anchor):
        """Add a new anchor to the repository.

        This will create a new ID for the anchor and provision new storage for
        it.

        Returns: The storage ID for the Anchor which can be used to retrieve
            the anchor later.

        """
        anchor_id = uuid.uuid4().hex
        anchor_path = self._anchor_path(anchor_id)
        with anchor_path.open(mode='wt') as f:
            save_anchor(f, anchor, self.root)

        return anchor_id

    def __getitem__(self, anchor_id):
        """Get an Anchor by ID.

        Args:
            anchor_id: The ID of the anchor to retrieve.

        Returns: An anchor instance.

        Raises:
            KeyError: The anchor can not be found.
        """
        file_path = self._anchor_path(anchor_id)

        try:
            with file_path.open(mode='rt') as handle:
                return load_anchor(handle, self.root)
        except OSError:
            raise KeyError('No anchor with id {}'.format(anchor_id))

    def __setitem__(self, anchor_id, anchor):
        """Update an anchor.

        This will update an existing anchor if it exists, or it will create new
        storage if not.

        Args:
            anchor_id: The ID of the anchor to update.
            anchor: The anchor to store.
        """
        with self._anchor_path(anchor_id).open(mode='wt') as f:
            save_anchor(f, anchor, self.root)

    def __delitem__(self, anchor_id):
        """Remove an anchor from storage.

        Args:
            anchor_id: The ID of the anchor to remove.

        Raises:
            KeyError: There is no anchor with that ID.
        """
        try:
            self._anchor_path(anchor_id).unlink()
        except OSError:
            raise KeyError('No anchor with id {}'.format(anchor_id))

    def __iter__(self):
        """An iterable of all anchor IDs in the repository.
        """
        for spor_file in self._spor_dir.glob('**/*.yml'):
            yield str(spor_file.name)[:-4]

    def items(self):
        """An iterable of all (anchor-id, Anchor) mappings in the repository.
        """
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

    start_path = pathlib.Path(os.getcwd() if path is None else path)
    paths = [start_path] + list(start_path.parents)

    for path in paths:
        data_dir = path / spor_dir
        if data_dir.exists() and data_dir.is_dir():
            return path

    raise ValueError('No spor repository found')
