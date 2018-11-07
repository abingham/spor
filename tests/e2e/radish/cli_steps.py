import subprocess

from exit_codes import ExitCode
from radish import step


@step('I initialize a repository')
def init_repo(context):
    subprocess.check_call(['spor', 'init'])


@step('reinitializing the repository fails')
def reinit_repo_fails(context):
    result = subprocess.call(['spor', 'init'])
    assert result == ExitCode.DATAERR


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


def spor_add(filename, offset, width, context_width):
    proc = subprocess.Popen(['spor', 'add',
                             filename,
                             str(offset),
                             str(width),
                             str(context_width)],
                            universal_newlines=True,
                            stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    return proc, proc.communicate(input='{"meta": "data"}')


@step('I create an anchor for "{filename}" at offset {offset:d}')
def create_anchor(step, filename, offset):
    proc, (output, output_err) = spor_add(filename, offset, 3, 1)

    msg = "stderr should be empty, not {}".format(output_err)
    assert output_err == '', msg


@step('I can not create an anchor for "{filename}"')
def unable_to_create_anchor(step, filename):
    proc, (output, output_err) = spor_add(filename, 3, 3, 1)
    retcode = proc.wait()

    msg = "err is {}, not {}".format(retcode, ExitCode.DATAERR)
    assert retcode == ExitCode.NOINPUT, msg


@step('an anchor for "{filename}" at offset {offset:d} appears in the listing')
def check_anchor_listing(step, filename, offset):
    output = subprocess.check_output(['spor', 'list'],
                                     universal_newlines=True)
    expected = "{}:{} => {{'meta': 'data'}}".format(filename, offset)

    lines = output.split('\n')
    assert any(line.strip().endswith(expected) for line in lines)


@step('the repository has {count:d} anchor')
def count_anchors(step, count):
    output = subprocess.check_output(['spor', 'list'],
                                     universal_newlines=True)
    lines = output.split('\n')
    assert len(lines) == count + 1


@step('the repository is valid')
def check_repo_is_valid(step):
    output = subprocess.check_output(['spor', 'status'])
    print(output)
    assert output == b''


@step('the repository is invalid')
def check_repo_is_invalid(step):
    output = subprocess.check_output(['spor', 'status'])
    assert output != b''


@step('I update the repository')
def update_repository(step):
    subprocess.check_call(['spor', 'update'])


@step('I delete the anchor for "{filename}" at offset {offset:d}')
def delete_anchor(step, filename, offset):
    # TODO
    pass


@step('no anchor for "{filename}" at offset {offset:d} appears in the listing')
def no_anchor_appears(step, filename, offset):
    # TODO
    pass
