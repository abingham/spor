import pytest

from spor.anchor import make_anchor
from spor.repository import initialize_repository, open_repository


def test_initialize_repo_creates_directory(tmpdir_path):
    assert not (tmpdir_path / '.spor').exists()
    initialize_repository(tmpdir_path)
    assert (tmpdir_path / '.spor').exists()


def test_initialize_duplicate_repo_raises_ValueError(tmpdir_path):
    initialize_repository(tmpdir_path)
    with pytest.raises(ValueError):
        initialize_repository(tmpdir_path)


def test_create_repo_from_root(tmpdir_path):
    initialize_repository(tmpdir_path)
    repo = open_repository(tmpdir_path)
    assert repo.root == tmpdir_path
    assert repo._spor_dir == tmpdir_path / '.spor'


def test_create_repo_from_nested_dir(repo):
    nested = repo.root / 'nested'
    nested.mkdir()
    assert open_repository(nested).root == repo.root


def test_create_repo_with_no_repo_raises_ValueError(tmpdir_path, excursion):
    with excursion(tmpdir_path):
        with pytest.raises(ValueError):
            open_repository(tmpdir_path)


def test_add_anchor_generates_correct_anchor(repo):
    source_path = repo.root / "source.py"
    with source_path.open(mode='wt') as handle:
        handle.write('abcdefgh')

    metadata = {"1": 2}

    anchor_id = repo.add(
        make_anchor(
            file_path=source_path,
            offset=3,
            width=3,
            context_width=2,
            metadata=metadata))

    anchor = repo[anchor_id]
    assert anchor.file_path == source_path
    assert anchor.metadata == metadata
    assert anchor.context_width == 2
    assert anchor.context.before == 'bc'
    assert anchor.context.topic == 'def'
    assert anchor.context.offset == 3
    assert anchor.context.after == 'gh'


def test_get_anchor_by_id(repo):
    source_path = repo.root / "source.py"
    with source_path.open(mode='wt') as handle:
        handle.write('# nothing')

    metadata = {"1": 2}
    anchor_id = repo.add(
        make_anchor(
            metadata=metadata,
            file_path=source_path,
            offset=3,
            width=3,
            context_width=2))

    repo[anchor_id]


def test_get_non_existent_anchor_raises_KeyError(repo):
    with pytest.raises(KeyError):
        assert repo['non-existent']


def test_update_updates_metadata(repo):
    source_path = repo.root / "source.py"
    with source_path.open(mode='wt') as handle:
        handle.write('# nothing')

    anchor_id = repo.add(
        make_anchor(
            metadata={},
            file_path=source_path,
            offset=3,
            width=3,
            context_width=2))

    new_metadata = {"3": 4}
    anchor = repo[anchor_id]
    anchor.metadata = new_metadata

    repo[anchor_id] = anchor
    anchor = repo[anchor_id]
    assert anchor.metadata == new_metadata


def _test_delete_removes_anchor(repo):
    source_path = repo.root / "source.py"
    with source_path.open(mode='wt') as handle:
        handle.write('# nothing')

    anchor_id = repo.add(
        make_anchor(
            metadata={},
            file_path=source_path,
            offset=3,
            width=3,
            context_width=2))

    assert anchor_id in repo
    del repo[anchor_id]
    assert anchor_id not in repo


def test_delete_raises_KeyError_on_nonexistent_id(repo):
    with pytest.raises(KeyError):
        del repo['non-existent']
