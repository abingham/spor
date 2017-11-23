import pathlib

from spor.anchor import make_anchor


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
