import subprocess

from radish import step


@step('I initialize a repository')
def init_repo(context):
    subprocess.check_call(['spor', 'init'])


@step('I create the source file "{filename}"')
def create_source_file(step, filename):
    source_file = step.context.repo_path / filename
    with source_file.open(mode='wt') as handle:
        handle.write('''def func():
    x = 1
    y = 2
    z = 3
    return x + y + z
''')


@step('I modify "{filename}"')
def modify_file(step, filename):
    source_file = step.context.repo_path / filename
    with source_file.open(mode='rt') as handle:
        text = handle.read()
    text = "# a comment\n" + text
    with source_file.open(mode='wt') as handle:
        handle.write(text)


@step('a repo data directory exists')
def check_repo_exists(step):
    assert (step.context.repo_path / ".spor").exists()


@step('I create a new anchor for "{filename}" at offset {offset:d}')
def create_anchor(step, filename, offset):
    proc = subprocess.Popen(['spor', 'add', filename,
                             str(offset), "3", "1"],
                            universal_newlines=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    output, output_err = proc.communicate(input='{meta: data}')
    assert output_err is None


@step('an anchor for "{filename}" at offset {offset:d} appears in the listing')
def check_anchor_listing(step, filename, offset):
    output = subprocess.check_output(['spor', 'list', 'source.py'],
                                     universal_newlines=True)
    expected = "{}:{} => {{'meta': 'data'}}".format(filename, offset)

    assert output.strip() == expected.strip(
    ), 'expected: {}, actual: {}'.format(expected, output)


@step('the repository is valid')
def check_repo_is_valid(step):
    subprocess.check_call(['spor', 'validate', '--no-print'])


@step('the repository is invalid')
def check_repo_is_invalid(step):
    try:
        subprocess.check_call(['spor', 'validate', '--no-print'])
        assert False, 'validate should fail'
    except subprocess.CalledProcessError as exc:
        assert exc.returncode == 1


@step('I update the repository')
def update_repository(step):
    subprocess.check_call(['spor', 'update'])
