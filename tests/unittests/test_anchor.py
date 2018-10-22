import pathlib

from spor.anchor import make_anchor


def test_make_anchor(repo):
    source = pathlib.Path('source.py')
    with source.open(mode='wt') as handle:
        handle.write('\n'.join('abcde'))
    anchor = make_anchor(
        file_path=repo.root / source,
        offset=4,
        width=2,
        context_width=4,
        metadata={})
    assert anchor.file_path == source
    assert anchor.context.before.offset == 0
    assert anchor.context.before.text == 'a\nb\n'
    assert anchor.context.topic.offset == 4
    assert anchor.context.topic.text == 'c\n'
    assert anchor.context.after.offset == 6
    assert anchor.context.after.text == 'd\ne'
    assert anchor.metadata == {}
