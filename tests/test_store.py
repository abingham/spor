import pathlib

import pytest

from spor.store import Store


def test_initialize_store_creates_directory(tmpdir_path):
    assert not (tmpdir_path / '.spor').exists()
    Store.initialize(tmpdir_path)
    assert (tmpdir_path / '.spor').exists()


def test_initialize_duplicate_store_raises_ValueError(tmpdir_path):
    Store.initialize(tmpdir_path)
    with pytest.raises(ValueError):
        Store.initialize(tmpdir_path)


def test_create_store_from_root(tmpdir_path):
    Store.initialize(tmpdir_path)
    store = Store(tmpdir_path)
    assert store.repo_path == tmpdir_path / '.spor'


def test_create_store_from_nested_dir(tmpdir_path):
    nested = tmpdir_path / 'nested'
    nested.mkdir()
    Store.initialize(tmpdir_path)
    store = Store(nested)
    assert store.repo_path == tmpdir_path / '.spor'


def test_create_store_with_no_repo_raises_ValueError(tmpdir_path, excursion):
    with excursion(tmpdir_path):
        with pytest.raises(ValueError):
            Store(tmpdir_path)


def test_make_anchor_simple(tmpdir_path, excursion):
    Store.initialize(tmpdir_path)
    store = Store(tmpdir_path)
    with excursion(tmpdir_path):
        source = pathlib.Path('source.py')
        with source.open(mode='wt') as handle:
            handle.write('\n'.join('abcde'))
        anchor = store.make_anchor(2, source, 3, {})
        assert anchor.file_path == source
        assert anchor.line_number == 3
        assert anchor.columns is None
        assert anchor.metadata == {}
        assert anchor.context.before == ('a\n', 'b\n')
        assert anchor.context.line == 'c\n'
        assert anchor.context.after == ('d\n', 'e\n')
