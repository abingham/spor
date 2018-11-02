from hypothesis import given
import hypothesis.strategies as ST

from spor.diff import _split_keep_sep


@given(ST.text(), ST.text(min_size=1))
def test_split_keep_sep(s, sep):
    toks = _split_keep_sep(s, sep)
    assert ''.join(toks) == s
