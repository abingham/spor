from io import StringIO
from pathlib import Path

import pytest
from spor.anchor import make_anchor
from spor.updating import AlignmentError, update


# These are the "accepted" update results. See tests below to see how they're used.
ACCEPTED = (
    ((2, 2, 2, 'aabbcc'), (2, 2, 2, 'aabBbcc')),
    ((2, 2, 2, 'aabbcc'), (3, 2, 2, 'aaBbbcc')),
    ((2, 2, 2, 'aabbcc'), (2, 2, 2, 'aabbBcc')),
)


class Test_update:

    @pytest.mark.parametrize("pre, post", ACCEPTED)
    def test_acceptance(self, pre, post):
        offset, width, context_width, text = pre
        anchor = make_anchor(
            file_path=Path('/source.py'),
            offset=offset,
            width=width,
            context_width=context_width,
            metadata={},
            handle=StringIO(text))

        offset, width, context_width, text = post

        updated_anchor = update(anchor, StringIO(text))

        expected_anchor = make_anchor(
            file_path=Path('/source.py'),
            offset=offset,
            width=width,
            context_width=context_width,
            metadata={},
            handle=StringIO(text))

        assert updated_anchor == expected_anchor

    def test_raises_AlignmentError_if_no_alignments(self):
        anchor = make_anchor(
            file_path=Path('/source.py'),
            offset=2,
            width=2,
            context_width=2,
            metadata={},
            handle=StringIO("aabbcc"))

        with pytest.raises(AlignmentError):
            update(anchor, StringIO("xxxxxxx"))

    def test_raises_AlignmentError_if_empty_alignment(self):
        anchor = make_anchor(
            file_path=Path('/source.py'),
            offset=2,
            width=1,
            context_width=2,
            metadata={},
            handle=StringIO("aabcc"))

        with pytest.raises(AlignmentError):
            update(anchor, StringIO("aacc"))
