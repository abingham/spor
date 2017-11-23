import os
import subprocess

import pytest


@pytest.fixture
def initialized_repo(tmpdir_path):
    """Initialize a repo and add an anchor for "source.py".

    Returns the root path of the repo.
    """
    os.chdir(str(tmpdir_path))
    source_file = tmpdir_path / "source.py"
    with source_file.open(mode='wt') as handle:
        handle.write('''def func():
    x = 1
    y = 2
    z = 3
    return x + y + z
''')

    subprocess.check_call(['spor', 'init'])

    proc = subprocess.Popen(['spor', 'add', 'source.py', '3'],
                            universal_newlines=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    output, output_err = proc.communicate(input='{meta: data}')
    assert output_err is None
    return tmpdir_path


def test_init_creates_repo(tmpdir_path):
    os.chdir(str(tmpdir_path))
    subprocess.check_call(['spor', 'init'])
    assert (tmpdir_path / ".spor").exists()


def test_add_anchor_creates_anchor(initialized_repo):
    output = subprocess.check_output(['spor', 'list', 'source.py'],
                                     universal_newlines=True)
    assert output == "Anchor(file_path=source.py, line_number=3, columns=None) "\
                     "=> {'meta': 'data'}\n"


def test_validate_on_unchanged_source_is_clean(initialized_repo):
    subprocess.check_call(['spor', 'validate'])


def test_validate_on_modified_source_fails(initialized_repo):
    source_file = initialized_repo / "source.py"
    with source_file.open(mode='wt') as handle:
        handle.write('''# a comment
def func():
    x = 1
    y = 2
    z = 3
    return x + y + z
''')

    with pytest.raises(subprocess.CalledProcessError) as exc:
        subprocess.check_call(['spor', 'validate'])
    assert exc.value.returncode == 1
