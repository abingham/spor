import os
import pathlib
import signal
import subprocess
import sys
import tempfile

import docopt
import docopt_subcommands as dsc
import yaml

from .store import Store
from .validation import validate


def find_anchor(file_name):
    file_path = pathlib.Path(file_name).resolve()
    store = Store(file_path)
    for anchor in store:
        if store.tracked_file(anchor) == file_path:
            yield anchor


@dsc.command()
def init_handler(args):
    """usage: {program} init

    Initialize a new spor repository in the current directory.
    """
    try:
        Store.initialize(pathlib.Path.cwd())
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return os.EX_DATAERR

    return os.EX_OK


@dsc.command()
def list_handler(args):
    """usage: {program} list <source-file>

    List the anchors for a file.
    """
    for anchor in find_anchor(args['<source-file>']):
        print("{} => {}".format(anchor, anchor.metadata))

    return os.EX_OK


@dsc.command()
def add_handler(args):
    """usage: {program} add <source-file> <line-number> [<begin-offset> <end-offset>]

    Add a new anchor for a file.
    """
    file_path = pathlib.Path(args['<source-file>']).resolve()

    try:
        line_number = int(args['<line-number>'])
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return os.EX_DATAERR

    try:
        store = Store(file_path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return os.EX_DATAERR

    # TODO: What is a reasonable default for windows? Does this approach even make sense on windows?
    editor = os.environ.get('EDITOR', 'vim')

    with tempfile.TemporaryDirectory() as dirname:
        filename = pathlib.Path(dirname) / 'metadata.yml'
        with filename.open(mode='wt') as handle:
            handle.write('# yaml metadata')
        subprocess.call([editor, filename])

        with filename.open(mode='rt') as handle:
            text = handle.read()

    # TODO: More graceful handling of yaml.parser.ParserError
    metadata = yaml.load(text)

    # TODO: Add support for begin/end col offset
    store.add(metadata, file_path, line_number)

    return os.EX_OK


@dsc.command()
def validate_handler(args):
    """usage: {program} validate [--print] [<path>]

    Validate the anchors in the current repository.
    """
    path = pathlib.Path(args['<path>']) if args['<path>'] else None
    do_print = args['--print']

    try:
        store = Store(path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return os.EX_DATAERR

    invalid = False
    for (file_name, diff) in validate(store):
        invalid = True
        if do_print:
            print('= MISMATCH =')
            print(file_name)
            sys.stdout.writelines(diff)

    if invalid:
        return 1
    else:
        return os.EX_OK


_SIGNAL_EXIT_CODE_BASE = 128


def main():
    signal.signal(signal.SIGINT,
                  lambda *args: sys.exit(_SIGNAL_EXIT_CODE_BASE + signal.SIGINT))

    try:
        return dsc.main(
            program='spor',
            version='spor v0.0.0')
    except docopt.DocoptExit as exc:
        print(exc, file=sys.stderr)
        return os.EX_USAGE
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return os.EX_NOINPUT
    except PermissionError as exc:
        print(exc, file=sys.stderr)
        return os.EX_NOPERM


if __name__ == '__main__':
    sys.exit(main())
