import contextlib
import os
import pathlib

import pytest


@pytest.fixture
def tmpdir_path(tmpdir):
    "Like pytest's `tmpdir` but returning a `pathlib.Path`."
    return pathlib.Path(str(tmpdir))


@pytest.fixture
def excursion():
    @contextlib.contextmanager
    def f(path):
        old = pathlib.Path.cwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(old)
    return f
