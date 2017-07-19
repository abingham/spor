import docopt_subcommands as dsc
import pathlib
from .store import find_spor_repo, Store


def find_anchor(file_name):
    file_path = pathlib.Path(file_name).resolve()
    spor_path = find_spor_repo(file_path)
    store = Store(spor_path)
    for md in store:
        if store.tracked_file(md) == file_path:
            yield md


@dsc.command()
def list_handler(args):
    """usage: {program} list <source-file>
    """
    for md in find_anchor(args['<source-file>']):
        print("{} => {}".format(md, md.metadata))


@dsc.command()
def add_handler(args):
    """usage: {program} add <source-file> <line-number> [<begin-offset> <end-offset>]
    """
    file_path = pathlib.Path(file_name).resolve()
    spor_path = find_spor_repo(file_path)
    store = Store(spor_path)


def main():
    dsc.main(
        program='spor',
        version='spor v0.0.0')


if __name__ == '__main__':
    main()
