import pathlib

import pytest

from spor.anchor import make_anchor
from spor.repo import Repository


def test_initialize_repo_creates_directory(tmpdir_path):
    assert not (tmpdir_path / '.spor').exists()
    Repository.initialize(tmpdir_path)
    assert (tmpdir_path / '.spor').exists()


def test_initialize_duplicate_repo_raises_ValueError(tmpdir_path):
    Repository.initialize(tmpdir_path)
    with pytest.raises(ValueError):
        Repository.initialize(tmpdir_path)


def test_create_repo_from_root(tmpdir_path):
    Repository.initialize(tmpdir_path)
    repo = Repository(tmpdir_path)
    assert repo.root == tmpdir_path
    assert repo._spor_dir == tmpdir_path / '.spor'


def test_create_repo_from_nested_dir(repo):
    nested = repo.root / 'nested'
    nested.mkdir()
    assert Repository(nested).root == repo.root


def test_create_repo_with_no_repo_raises_ValueError(tmpdir_path, excursion):
    with excursion(tmpdir_path):
        with pytest.raises(ValueError):
            Repository(tmpdir_path)


def test_make_anchor(repo):
    source = pathlib.Path('source.py')
    with source.open(mode='wt') as handle:
        handle.write('\n'.join('abcde'))
    anchor = make_anchor(2, repo.root / source, 3, {})
    assert anchor.file_path == source
    assert anchor.line_number == 3
    assert anchor.columns is None
    assert anchor.metadata == {}
    assert anchor.context.before == ('a\n', 'b\n')
    assert anchor.context.line == 'c\n'
    assert anchor.context.after == ('d\n', 'e\n')
