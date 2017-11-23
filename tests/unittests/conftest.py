import contextlib
import os
import pathlib

import pytest

from spor.repo import Repository


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
    Repository.initialize(tmpdir_path)
    repo = Repository(tmpdir_path)
    with excursion(tmpdir_path):
        yield repo
