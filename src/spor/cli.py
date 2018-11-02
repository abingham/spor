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
from .updating import update
from .validation import validate


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
    """usage: {program} list <source-file>

    List the anchors for a file.
    """
    repo = open_repository(args['<source-file>'])
    for anchor_id, anchor in repo.items():
        print("{}:{} => {}".format(
            anchor.file_path.relative_to(repo.root),
            anchor.context.offset,
            anchor.metadata))

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

    try:
        repo = open_repository(file_path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.DATAERR

    if sys.stdin.isatty():
        text = _launch_editor('# json metadata')
    else:
        text = sys.stdin.read()

    try:
        metadata = json.loads(text)
    except json.JSONDecodeError:
        print('Failed to create anchor. Invalid JSON metadata.', file=sys.stderr)
        return ExitCode.DATAERR

    # TODO: let user specify encoding
    with file_path.open(mode='rt') as handle:
        anchor = make_anchor(
            file_path,
            offset,
            width,
            context_width,
            metadata,
            handle=handle)

    repo.add(anchor)

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
    path = pathlib.Path(args['<path>']) if args['<path>'] else None

    try:
        repo = open_repository(path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.DATAERR

    for anchor_id, anchor in repo.items():
        anchor = update(anchor)
        repo[anchor_id] = anchor


@dsc.command()
def validate_handler(args):
    """usage: {program} validate [--no-print] [<path>]

    Validate the anchors in the current repository."""
    path = pathlib.Path(args['<path>']) if args['<path>'] else None
    do_print = not args['--no-print']

    try:
        repo = open_repository(path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.DATAERR

    invalid = False
    for (file_name, diff) in validate(repo):
        invalid = True
        if do_print:
            print('= MISMATCH =')
            print(file_name)
            sys.stdout.writelines(diff)

    if invalid:
        return 1
    else:
        return ExitCode.OK


@dsc.command()
def details_handler(args):
    """usage: {program} details <anchor-id> [<path>]

    Get the details of a single anchor.
    """

    path = pathlib.Path(args['<path>']) if args['<path>'] else None

    try:
        repo = open_repository(path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.DATAERR

    anchor = None
    for anchor_id, a in repo.items():
        if anchor_id.startswith(args['<anchor-id>']):
            if anchor is not None:
                print('Ambiguous ID specification', file=sys.stderr)
                return ExitCode.DATA_ERR
            anchor = a

    if anchor is None:
        print('No anchor matching ID specification', file=sys.stderr)
        return ExitCode.DATA_ERR

    print("""path: {file_path}
encoding: {encoding}
context:
    before:
    {before}
    --------------

    topic:
    {topic}
    --------------

    after:
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


_SIGNAL_EXIT_CODE_BASE = 128


def main():
    signal.signal(
        signal.SIGINT,
        lambda *args: sys.exit(_SIGNAL_EXIT_CODE_BASE + signal.SIGINT))

    try:
        return dsc.main(program='spor', version='spor v0.0.0')
    except docopt.DocoptExit as exc:
        print(exc, file=sys.stderr)
        return ExitCode.USAGE
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.NOINPUT
    except PermissionError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.NOPERM


if __name__ == '__main__':
    sys.exit(main())
