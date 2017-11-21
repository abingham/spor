import contextlib
import os
import pathlib

import pytest

from spor.store import find_spor_repo, Store


@contextlib.contextmanager
def excursion(path):
    old = pathlib.Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def test_find_spor_repo_root_dir(tmpdir_path):
    Store.initialize(tmpdir_path)
    assert find_spor_repo(tmpdir_path) == tmpdir_path / '.spor'


def test_find_spor_repo_nested_dir(tmpdir_path):
    nested = tmpdir_path / 'nested'
    nested.mkdir()
    Store.initialize(tmpdir_path)
    assert find_spor_repo(nested) == tmpdir_path / '.spor'


def test_find_spor_repo_root_dir_from_cwd(tmpdir_path):
    Store.initialize(tmpdir_path)
    with excursion(tmpdir_path):
        assert find_spor_repo() == tmpdir_path / '.spor'


def test_find_spor_repo_nested_dir_from_cwd(tmpdir_path):
    nested = tmpdir_path / 'nested'
    nested.mkdir()
    Store.initialize(tmpdir_path)
    with excursion(nested):
        assert find_spor_repo() == tmpdir_path / '.spor'


def test_find_spor_repo_with_no_repo_raises_ValueError(tmpdir_path):
    with excursion(tmpdir_path):
        with pytest.raises(ValueError):
            find_spor_repo(tmpdir_path)
