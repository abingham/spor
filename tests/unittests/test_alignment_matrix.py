from hypothesis import assume, given
import hypothesis.strategies as ST
import pytest

from spor.alignment.matrix import Matrix


@ST.composite
def matrix_and_indices(draw):
    rows = draw(ST.integers(min_value=1, max_value=100))
    cols = draw(ST.integers(min_value=1, max_value=100))
    matrix = Matrix(rows, cols)
    row = draw(ST.integers(min_value=0, max_value=matrix.rows - 1))
    col = draw(ST.integers(min_value=0, max_value=matrix.cols - 1))
    return (matrix, row, col)


@given(ST.integers(min_value=0, max_value=100),
       ST.integers(min_value=0, max_value=100))
def test_matrices_remember_dimensions(rows, cols):
    m = Matrix(rows, cols)
    assert m.rows == rows
    assert m.cols == cols


@given(ST.integers(max_value=100),
       ST.integers(max_value=100))
def test_matrices_must_have_non_negative_dimensions(rows, cols):
    assume(rows < 0 or cols < 0)

    with pytest.raises(ValueError):
        Matrix(rows, cols)


@given(ST.integers(max_value=1000000000),
       matrix_and_indices())
def test_matrix_remembers_values(value, m_and_i):
    matrix, row, col = m_and_i
    matrix[(row, col)] = value
    assert matrix[(row, col)] == value
