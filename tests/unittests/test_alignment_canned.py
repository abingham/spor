"""These are a set of canned tests for the Smith-Waterman alignment algorithm.

We took some input and output data from wikipedia and used that as the starting
point for getting the algorithm working. These tests make sure that we handle
that input/output correctly.
"""

from spor.alignment.matrix import Matrix
from spor.alignment.smith_waterman import align, build_score_matrix, Direction, tracebacks


# taken from https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm
COLS = list('TGTTACGG')
ROWS = list('GGTTGACTA')


def score(a, b):
    if a == b:
        return 3
    else:
        return -3


def gap_penalty(gap):
    if gap == 1:
        return 2
    else:
        gap * gap_penalty(1)


def test_canned_tracebacks():
    score_matrix, traceback_matrix = build_score_matrix(
        ROWS, COLS, score, gap_penalty)
    max_idx, max_score = max(score_matrix.items(), key=lambda item: item[1])
    tbs = list(tracebacks(traceback_matrix, max_idx))
    assert len(tbs) == 1

    expected = (
        ((2, 2), Direction.DIAG),
        ((3, 3), Direction.DIAG),
        ((4, 4), Direction.DIAG),
        ((5, 4), Direction.UP),
        ((6, 5), Direction.DIAG),
        ((7, 6), Direction.DIAG))

    assert tuple(tbs[0]) == expected


def test_canned_score_matrix():
    expected = (
       (0, 0, 0, 0, 0, 0, 0, 0, 0),
       (0, 0, 3, 1, 0, 0, 0, 3, 3),
       (0, 0, 3, 1, 0, 0, 0, 3, 6),
       (0, 3, 1, 6, 4, 2, 0, 1, 4),
       (0, 3, 1, 4, 9, 7, 5, 3, 2),
       (0, 1, 6, 4, 7, 6, 4, 8, 6),
       (0, 0, 4, 3, 5, 10, 8, 6, 5),
       (0, 0, 2, 1, 3, 8, 13, 11, 9),
       (0, 3, 1, 5, 4, 6, 11, 10, 8),
       (0, 1, 0, 3, 2, 7, 9, 8, 7))

    exp_matrix = Matrix(len(ROWS) + 1, len(COLS) + 1)
    for row, col in exp_matrix:
        exp_matrix[row, col] = expected[row][col]

    score_matrix, traceback_matrix = build_score_matrix(
        ROWS, COLS, score, gap_penalty)
    max_idx, max_score = max(score_matrix.items(), key=lambda item: item[1])
    assert max_score == 13
    assert max_idx == (7, 6)
    assert exp_matrix == score_matrix


def test_canned_alignment():
    alignments = align(ROWS, COLS, score, gap_penalty)
    alignments = list(alignments)
    assert len(alignments) == 1
    actual = tuple(alignments[0])
    expected = ((1, 1), (2, 2), (3, 3), (4, None), (5, 4), (6, 5))
    assert actual == expected
