import pytest

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


def test_add_anchor_generates_correct_anchor(repo):
    source_path = repo.root / "source.py"
    with source_path.open(mode='wt') as handle:
        handle.write('# nothing')

    metadata = {1: 2}
    anchor_id = repo.add(metadata, source_path, 1)
    anchor = repo[anchor_id]
    assert anchor.file_path == source_path.relative_to(repo.root)
    assert anchor.metadata == metadata
    assert anchor.line_number == 1
    assert anchor.columns == None


def test_get_anchor_by_id(repo):
    source_path = repo.root / "source.py"
    with source_path.open(mode='wt') as handle:
        handle.write('# nothing')

    metadata = {1: 2}
    anchor_id = repo.add(metadata, source_path, 1)
    repo[anchor_id]


def test_get_non_existent_anchor_raises_KeyError(repo):
    with pytest.raises(KeyError):
        assert repo['non-existent']


def test_update_updates_metadata(repo):
    source_path = repo.root / "source.py"
    with source_path.open(mode='wt') as handle:
        handle.write('# nothing')

    anchor_id = repo.add({1: 2}, source_path, 1)

    metadata = {3: 4}
    repo.update(anchor_id, metadata)
    anchor = repo[anchor_id]
    assert anchor.metadata == metadata


def test_update_raises_KeyError_for_non_existent_id(repo):
    with pytest.raises(KeyError):
        repo.update('non-existent', {})


def test_delete_removes_anchor(repo):
    source_path = repo.root / "source.py"
    with source_path.open(mode='wt') as handle:
        handle.write('# nothing')

    anchor_id = repo.add({1: 2}, source_path, 1)
    assert anchor_id in repo
    del repo[anchor_id]
    assert anchor_id not in repo


def test_delete_raises_KeyError_on_nonexistent_id(repo):
    with pytest.raises(KeyError):
        del repo['non-existent']
