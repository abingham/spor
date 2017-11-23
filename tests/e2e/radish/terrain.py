import os
import pathlib
from tempfile import TemporaryDirectory

from radish import after, before


@before.each_scenario
def enter_tempdir(scenario):
    tmpdir = TemporaryDirectory()
    scenario.context.repo_path = pathlib.Path(tmpdir.name)
    scenario.context.repo_tmpdir = (tmpdir, os.getcwd())
    os.chdir(tmpdir.name)


@after.each_scenario
def cleanup_tempdir(scenario):
    os.chdir(scenario.context.repo_tmpdir[1])
    scenario.context.repo_tmpdir[0].cleanup()
