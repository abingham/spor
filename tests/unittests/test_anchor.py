from io import StringIO
import pathlib

import pytest
from spor.anchor import make_anchor

from hypothesis import given
import hypothesis.strategies as ST


@ST.composite
def overflow_width(draw):
    text_size = draw(ST.integers(min_value=1, max_value=10))
    text = draw(ST.text(min_size=text_size, max_size=text_size))
    offset = draw(ST.integers(min_value=0, max_value=text_size))
    width = text_size + 1
    return (text, offset, width)


@ST.composite
def past_end_of_file(draw):
    text_size = draw(ST.integers(min_value=1, max_value=10))
    text = draw(ST.text(min_size=text_size, max_size=text_size))
    offset = draw(ST.integers(min_value=text_size + 1))
    width = 1
    return (text, offset, width)


class Test_make_anchor():

    def test_success(self):
        anchor = make_anchor(
            file_path=pathlib.Path('/source.py'),
            handle=StringIO('\n'.join('abcde')),
            offset=4,
            width=2,
            context_width=4,
            metadata={})
        assert anchor.file_path == pathlib.Path('/source.py')
        assert anchor.context.before == 'a\nb\n'
        assert anchor.context.offset == 4
        assert anchor.context.topic == 'c\n'
        assert anchor.context.after == 'd\ne'
        assert anchor.metadata == {}

    def test_raises_ValueError_if_path_is_not_absolute(self):
        with pytest.raises(ValueError):
            make_anchor(
                file_path=pathlib.Path("source.py"),
                handle=StringIO('contents'),
                offset=0,
                width=1,
                context_width=1,
                metadata={})

    @given(overflow_width())
    def test_raises_ValueError_if_anchor_too_wide(self, args):
        text, offset, width = args

        with pytest.raises(ValueError):
            make_anchor(
                file_path=pathlib.Path("/source.py"),
                handle=StringIO(text),
                offset=offset,
                width=width,
                context_width=4,
                metadata={})

    @given(past_end_of_file())
    def test_raises_ValueError_if_anchor_past_end_of_file(self, args):
        text, offset, width = args

        with pytest.raises(ValueError):
            make_anchor(
                file_path=pathlib.Path("/source.py"),
                handle=StringIO(text),
                offset=offset,
                width=width,
                context_width=4,
                metadata={})

    def test_raises_ValueError_on_negative_offset(self):
        with pytest.raises(ValueError):
            make_anchor(
                file_path=pathlib.Path("/source.py"),
                handle=StringIO('contents'),
                offset=-1,
                width=1,
                context_width=1,
                metadata={})

    def test_raises_ValueError_on_negative_width(self):
        with pytest.raises(ValueError):
            make_anchor(
                file_path=pathlib.Path("/source.py"),
                handle=StringIO("contents"),
                offset=0,
                width=-1,
                context_width=1,
                metadata={})

    def test_raises_ValueError_on_negative_context_width(self):
        with pytest.raises(ValueError):
            make_anchor(
                file_path=pathlib.Path("/source.py"),
                handle=StringIO("contents"),
                offset=0,
                width=1,
                context_width=-1,
                metadata={})
