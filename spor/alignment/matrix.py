import array

class Matrix:
    """A simple 2D matrix designed to support alignment calculation.
    """
    def __init__(self, rows, cols, type_code='I', initial_value=0):
        if rows < 0 or cols < 0:
            raise ValueError('Matrix size must be non-negative')

        self._rows = rows
        self._cols = cols
        self._data = array.array(
            type_code, (initial_value for _ in range(cols * rows)))

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    def _to_index(self, row, col):
        return row * self._cols + col

    def __getitem__(self, index):
        return self._data[self._to_index(*index)]

    def __setitem__(self, index, val):
        self._data[self._to_index(*index)] = val

    def __iter__(self):
        return ((row, col)
                for row in range(self.rows)
                for col in range(self.cols))

    def items(self):
        for idx in self:
            yield (idx, self[idx])

    def values(self):
        return iter(self._data)

    def __eq__(self, other):
        return self._data == other._data

    def __str__(self):
        row_tokens = [
            ['{:3}'.format(x)
             for x
             in self._data[row * self.cols:(row + 1) * self.cols]]
            for row in range(self.rows)]
        row_strings = [''.join(tok) for tok in row_tokens]

        return '\n'.join(row_strings)
