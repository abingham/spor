import contextlib
import os
import pathlib

import pytest

from spor.repository import initialize_repository


@pytest.fixture
def tmpdir_path(tmpdir):
    "Like pytest's `tmpdir` but returning a `pathlib.Path`."
    return pathlib.Path(str(tmpdir))


@pytest.fixture
def excursion():
    @contextlib.contextmanager
    def f(path):
        old = pathlib.Path.cwd()
        os.chdir(str(path))
        try:
            yield
        finally:
            os.chdir(str(old))
    return f


@pytest.fixture
def repo(tmpdir_path, excursion):
    repo = initialize_repository(tmpdir_path)
    with excursion(tmpdir_path):
        yield repo
