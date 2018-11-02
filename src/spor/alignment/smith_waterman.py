"""Implementation of the Smith-Waterman algorithm.

Given two sequences of elements, a way to score similarity between any two
elements, and a function defining the penalty for gaps in a match, this can
tell you how the two sequences align. That is, it find the best "match" between
the two sequences. This has applications in genomics (e.g. finding how well two
sequences of bases match) and, in our case, in determining where an anchor
matches modified source code.
"""

from collections import namedtuple
import enum
import itertools

from .matrix import Matrix


class Direction(enum.Enum):
    """Possible directions in the traceback matrix.

    These are bitfields that can be ORd together in the matrix.
    """
    NONE = 0x00
    DIAG = 0x01
    UP = 0x02
    LEFT = 0x04


def _tracebacks(score_matrix, traceback_matrix, idx):
    """Implementation of traceeback.

    This version can produce empty tracebacks, which we generally don't want
    users seeing. So the higher level `tracebacks` filters those out.
    """
    score = score_matrix[idx]
    if score == 0:
        yield ()
        return

    directions = traceback_matrix[idx]

    assert directions != Direction.NONE, 'Tracebacks with direction NONE should have value 0!'

    row, col = idx

    if directions & Direction.UP.value:
        for tb in _tracebacks(score_matrix, traceback_matrix, (row - 1, col)):
            yield itertools.chain(tb, ((idx, Direction.UP),))

    if directions & Direction.LEFT.value:
        for tb in _tracebacks(score_matrix, traceback_matrix, (row, col - 1)):
            yield itertools.chain(tb, ((idx, Direction.LEFT),))

    if directions & Direction.DIAG.value:
        for tb in _tracebacks(score_matrix, traceback_matrix, (row - 1, col - 1)):
            yield itertools.chain(tb, ((idx, Direction.DIAG),))


def tracebacks(score_matrix, traceback_matrix, idx):
    """Calculate the tracebacks for `traceback_matrix` starting at index `idx`.

    Returns: An iterable of tracebacks where each traceback is sequence of
      (index, direction) tuples. Each `index` is an index into
      `traceback_matrix`. `direction` indicates the direction into which the
      traceback "entered" the index.
    """
    return filter(lambda tb: tb != (),
                  _tracebacks(score_matrix,
                              traceback_matrix,
                              idx))


def build_score_matrix(a, b, score_func, gap_penalty):
    """Calculate the score and traceback matrices for two input sequences and
    scoring functions.

    Returns: A tuple of (score-matrix, traceback-matrix). Each entry in the
      score-matrix is a numeric score. Each entry in the traceback-matrix is a
      logical ORing of the direction bitfields.
    """
    score_matrix = Matrix(rows=len(a) + 1, cols=len(b) + 1)
    traceback_matrix = Matrix(rows=len(a) + 1, cols=len(b) + 1, type_code='B')

    for row in range(1, score_matrix.rows):
        for col in range(1, score_matrix.cols):
            match_score = score_func(a[row - 1], b[col - 1])

            scores = sorted(
                ((score_matrix[(row - 1, col - 1)] + match_score,
                  Direction.DIAG),
                 (score_matrix[(row - 1, col)] - gap_penalty(1),
                  Direction.UP),
                 (score_matrix[(row, col - 1)] - gap_penalty(1),
                  Direction.LEFT),
                 (0, Direction.NONE)),
                key=lambda x: x[0],
                reverse=True)
            max_score = scores[0][0]
            scores = itertools.takewhile(
                lambda x: x[0] == max_score,
                scores)

            score_matrix[row, col] = max_score
            for _, direction in scores:
                traceback_matrix[row, col] = traceback_matrix[row, col] | direction.value

    return score_matrix, traceback_matrix


def _traceback_to_alignment(tb, a, b):
    """Convert a traceback (i.e. as returned by `tracebacks()`) into an alignment
    (i.e. as returned by `align`).

    Arguments:
      tb: A traceback.
      a: the sequence defining the rows in the traceback matrix.
      b: the sequence defining the columns in the traceback matrix.

    Returns: An iterable of (index, index) tupless where ether (but not both)
      tuples can be `None`.
    """
    # We subtract 1 from the indices here because we're translating from the
    # alignment matrix space (which has one extra row and column) to the space
    # of the input sequences.
    for idx, direction in tb:
        if direction == Direction.DIAG:
            yield (idx[0] - 1, idx[1] - 1)
        elif direction == Direction.UP:
            yield (idx[0] - 1, None)
        elif direction == Direction.LEFT:
            yield (None, idx[1] - 1)


def align(a, b, score_func, gap_penalty):
    """Calculate the best alignments of sequences `a` and `b`.

    Arguments:
      a: The first of two sequences to align
      b: The second of two sequences to align
      score_func: A 2-ary callable which calculates the "match" score between
        two elements in the sequences.
      gap_penalty: A 1-ary callable which calculates the gap penalty for a gap
        of a given size.

    Returns: A (score, alignments) tuple. `score` is the score that all of the
      `alignments` received. `alignments` is an iterable of `((index, index), .
      . .)` tuples describing the best (i.e. maximal and equally good)
      alignments. The first index in each pair is an index into `a` and the
      second is into `b`. Either (but not both) indices in a pair may be `None`
      indicating a gap in the corresponding sequence.

    """
    score_matrix, tb_matrix = build_score_matrix(a, b, score_func, gap_penalty)
    max_score = max(score_matrix.values())
    max_indices = (index
                   for index, score in score_matrix.items()
                   if score == max_score)
    alignments = (
        tuple(_traceback_to_alignment(tb, a, b))
        for idx in max_indices
        for tb in tracebacks(score_matrix, tb_matrix, idx))

    return (max_score, alignments)
