import random

from hypothesis import given
import hypothesis.strategies as ST

from spor.alignment import align


def simple_score(a, b):
    return 3 if a == b else -3


def simple_gap(gap):
    return gap


@ST.composite
def lists_with_common_element(draw):
    """Produce two lists which are guaranteed to have at least one element in
    common."""
    l1 = draw(ST.lists(ST.integers()))
    l2 = draw(ST.lists(ST.integers()))
    common_value = draw(ST.integers())
    idx = random.randint(0, len(l1))
    l1.insert(idx, common_value)
    idx = random.randint(0, len(l2))
    l2.insert(idx, common_value)

    assert common_value in l1
    assert common_value in l2

    return (l1, l2)


@given(ST.lists(ST.integers(), min_size=1))
def test_empty_sequences_have_no_alignment(seq):
    als = align(seq, [], simple_score, simple_gap)
    assert len(list(als)) == 0

    als = align([], seq, simple_score, simple_gap)
    assert len(list(als)) == 0


@given(lists_with_common_element())
def test_sequences_with_commonality_have_at_least_one_alignment(seqs):
    als = align(seqs[0], seqs[1], simple_score, simple_gap)
    assert len(list(als)) >= 1


@given(ST.sets(ST.integers()),
       ST.sets(ST.integers()))
def test_sequences_without_commonality_have_no_alignment(s1, s2):
    u1 = s1.difference(s2)
    u2 = s1.intersection(s2)
    assert u1.intersection(u2) == set()

    als = align(list(u1), list(u2), simple_score, simple_gap)
    assert (len(list(als))) == 0


@given(ST.lists(ST.integers()),
       ST.lists(ST.integers()))
def test_alignments_are_no_longer_than_longest_input(s1, s2):
    max_input_len = max(len(s1), len(s2))

    als = align(s1, s2, simple_score, simple_gap)
    for al in als:
        assert len(al) <= max_input_len
