import pathlib

import pytest


@pytest.fixture
def tmpdir_path(tmpdir):
    "Like pytest's `tmpdir` but returning a `pathlib.Path`."
    return pathlib.Path(str(tmpdir))
