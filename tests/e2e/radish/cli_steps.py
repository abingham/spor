import subprocess

from radish import given, when, then


@given('I initialize a repository')
def init_repo(context):
    subprocess.check_call(['spor', 'init'])


@given('I create the source file "{filename}"')
def create_source_file(step, filename):
    source_file = step.context.repo_path / filename
    with source_file.open(mode='wt') as handle:
        handle.write('''def func():
    x = 1
    y = 2
    z = 3
    return x + y + z
''')


@when('I modify "{filename}"')
def modify_file(step, filename):
    source_file = step.context.repo_path / filename
    with source_file.open(mode='rt') as handle:
        text = handle.read()
    text = "# a comment\n" + text
    with source_file.open(mode='wt') as handle:
        handle.write(text)


@then('a repo data directory exists')
def check_repo_exists(step):
    assert (step.context.repo_path / ".spor").exists()


@when('I create a new anchor for "{filename}" at line {lineno:d}')
def create_anchor(step, filename, lineno):
    proc = subprocess.Popen(['spor', 'add', filename, str(lineno)],
                            universal_newlines=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    output, output_err = proc.communicate(input='{meta: data}')
    assert output_err is None


@then('an anchor for "{filename}" at line {lineno:d} appears in the listing')
def check_anchor_listing(step, filename, lineno):
    output = subprocess.check_output(['spor', 'list', 'source.py'],
                                     universal_newlines=True)
    expected = "Anchor(file_path={filename}, line_number={lineno}, "\
               "columns=None) => {{'meta': 'data'}}\n".format(
                   filename=filename, lineno=lineno)

    assert output == expected, 'expected: {}, actual: {}'.format(expected, output)


@then('the repository is valid')
def check_repo_is_valid(step):
    subprocess.check_call(['spor', 'validate'])


@then('the repository is invalid')
def check_repo_is_invalid(step):
    try:
        subprocess.check_call(['spor', 'validate'])
        assert False, 'validate should fail'
    except subprocess.CalledProcessError as exc:
        assert exc.returncode == 1
