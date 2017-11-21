import os
import pathlib
import subprocess
import sys
import tempfile

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
def list_handler(args):
    """usage: {program} list <source-file>

    List the anchors for a file.
    """
    for anchor in find_anchor(args['<source-file>']):
        print("{} => {}".format(anchor, anchor.metadata))


@dsc.command()
def add_handler(args):
    """usage: {program} add <source-file> <line-number> [<begin-offset> <end-offset>]

    Add a new anchor for a file.
    """
    file_path = pathlib.Path(args['<source-file>']).resolve()
    line_number = int(args['<line-number>'])

    store = Store(file_path)

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


@dsc.command()
def validate_handler(args):
    """usage: {program} validate [<path>]

    Validate the anchors in the current repository.
    """
    path = pathlib.Path(args['<path>']) if args['<path>'] else None
    store = Store(path)
    for (file_name, diff) in validate(store):
        print('= MISMATCH =')
        print(file_name)
        sys.stdout.writelines(diff)


def main():
    dsc.main(
        program='spor',
        version='spor v0.0.0')


if __name__ == '__main__':
    main()
