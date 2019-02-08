import json
import os
import pathlib
import signal
import subprocess
import sys
import tempfile

import docopt
import docopt_subcommands as dsc
from exit_codes import ExitCode

from .anchor import make_anchor
from .repository import initialize_repository, open_repository
from .updating import AlignmentError, update
from .diff import get_anchor_diff
import spor.version


class ExitError(Exception):
    """Exception indicating that the program should exit with a specific code.
    """

    def __init__(self, code, *args):
        super().__init__(*args)
        self.code = code


def _open_repo(args, path_key='<path>'):
    """Open and return the repository containing the specified file.

    The file is specified by looking up `path_key` in `args`. This value or
    `None` is passed to `open_repository`.

    Returns: A `Repository` instance.

    Raises:
        ExitError: If there is a problem opening the repo.
    """
    path = pathlib.Path(args[path_key]) if args[path_key] else None

    try:
        repo = open_repository(path)
    except ValueError as exc:
        raise ExitError(ExitCode.DATA_ERR, str(exc))

    return repo


def _get_anchor(repo, id_prefix):
    """Get an anchor by ID, or a prefix of its id.
    """
    result = None
    for anchor_id, anchor in repo.items():
        if anchor_id.startswith(id_prefix):
            if result is not None:
                raise ExitError(
                    ExitCode.DATA_ERR,
                    'Ambiguous ID specification')

            result = (anchor_id, anchor)

    if result is None:
        raise ExitError(
            ExitCode.DATA_ERR,
            'No anchor matching ID specification')

    return result


@dsc.command()
def init_handler(args):
    """usage: {program} init

    Initialize a new spor repository in the current directory.
    """
    try:
        initialize_repository(pathlib.Path.cwd())
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.DATAERR

    return ExitCode.OK


@dsc.command()
def list_handler(args):
    """usage: {program} list

    List the anchors for a file.
    """
    repo = open_repository(None)
    for anchor_id, anchor in repo.items():
        print("{} {}:{} => {}".format(anchor_id,
                                      anchor.file_path.relative_to(repo.root),
                                      anchor.context.offset, anchor.metadata))

    return ExitCode.OK


@dsc.command()
def add_handler(args):
    """usage: {program} add <source-file> <offset> <width> <context-width>

    Add a new anchor for a file.
    """
    file_path = pathlib.Path(args['<source-file>']).resolve()

    try:
        offset = int(args['<offset>'])
        width = int(args['<width>'])
        context_width = int(args['<context-width>'])
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.DATAERR

    repo = _open_repo(args, '<source-file>')

    if sys.stdin.isatty():
        text = _launch_editor('# json metadata')
    else:
        text = sys.stdin.read()

    try:
        metadata = json.loads(text)
    except json.JSONDecodeError:
        print(
            'Failed to create anchor. Invalid JSON metadata.', file=sys.stderr)
        return ExitCode.DATAERR

    # TODO: let user specify encoding
    with file_path.open(mode='rt') as handle:
        anchor = make_anchor(
            file_path, offset, width, context_width, metadata, handle=handle)

    repo.add(anchor)

    return ExitCode.OK


@dsc.command()
def remove_handler(args):
    """usage: {program} remove <anchor-id> [<path>]

    Remove an existing anchor.
    """

    repo = _open_repo(args)
    anchor_id, anchor = _get_anchor(repo, args['<anchor-id>'])
    del repo[anchor_id]

    return ExitCode.OK


def _launch_editor(starting_text=''):
    "Launch editor, let user write text, then return that text."
    # TODO: What is a reasonable default for windows? Does this approach even
    # make sense on windows?
    editor = os.environ.get('EDITOR', 'vim')

    with tempfile.TemporaryDirectory() as dirname:
        filename = pathlib.Path(dirname) / 'metadata.yml'
        with filename.open(mode='wt') as handle:
            handle.write(starting_text)
        subprocess.call([editor, filename])

        with filename.open(mode='rt') as handle:
            text = handle.read()
    return text


@dsc.command()
def update_handler(args):
    """usage: {program} update [<path>]

    Update out of date anchors in the current repository.
    """
    repo = _open_repo(args)

    for anchor_id, anchor in repo.items():
        try:
            anchor = update(anchor)
        except AlignmentError as e:
            print('Unable to update anchor {}. Reason: {}'.format(
                anchor_id, e))
        else:
            repo[anchor_id] = anchor


@dsc.command()
def status_handler(args):
    """usage: {program} status [<path>]

    Validate the anchors in the current repository.
    """

    repo = _open_repo(args)

    for anchor_id, anchor in repo.items():
        diff_lines = get_anchor_diff(anchor)
        if diff_lines:
            print('{} {}:{} out-of-date'.format(
                anchor_id,
                anchor.file_path,
                anchor.context.offset))

    return ExitCode.OK


@dsc.command()
def diff_handler(args):
    """usage: {program} diff <anchor-id>

    Show the difference between an anchor and the current state of the source.
    """

    repo = _open_repo(args)
    anchor_id, anchor = _get_anchor(repo, args['<anchor-id>'])

    diff_lines = get_anchor_diff(anchor)
    sys.stdout.writelines(diff_lines)

    return ExitCode.OK


@dsc.command()
def details_handler(args):
    """usage: {program} details <anchor-id> [<path>]

    Get the details of a single anchor.
    """

    repo = _open_repo(args)
    _, anchor = _get_anchor(repo, args['<anchor-id>'])

    print("""path: {file_path}
encoding: {encoding}

[before]
{before}
--------------

[topic]
{topic}
--------------

[after]
{after}
--------------

offset: {offset}
width: {width}""".format(
        file_path=anchor.file_path,
        encoding=anchor.encoding,
        before=anchor.context.before,
        topic=anchor.context.topic,
        after=anchor.context.after,
        offset=anchor.context.offset,
        width=anchor.context.width))

    return ExitCode.OK


# TODO: edit


_SIGNAL_EXIT_CODE_BASE = 128


def main():
    signal.signal(
        signal.SIGINT,
        lambda *args: sys.exit(_SIGNAL_EXIT_CODE_BASE + signal.SIGINT))

    try:
        return dsc.main(program='spor', version='spor v{}'.format(spor.version.__version__))
    except docopt.DocoptExit as exc:
        print(exc, file=sys.stderr)
        return ExitCode.USAGE
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.NOINPUT
    except PermissionError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.NOPERM
    except ExitError as exc:
        print(exc, file=sys.stderr)
        return exc.code


if __name__ == '__main__':
    sys.exit(main())
