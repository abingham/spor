import docopt_subcommands as dsc
import pathlib
from .store import find_spor_dir, Store


def find_metadata(file_name):
    file_path = pathlib.Path(file_name).resolve()
    spor_path = find_spor_dir(file_path)
    store = Store(spor_path)
    for md in store:
        if store.tracked_file(md) == file_path:
            yield md


@dsc.command()
def list_handler(args):
    """usage: {program} list <source-file>
    """
    for md in find_metadata(args['<source-file>']):
        print("{} => {}".format(md, md.metadata))


def main():
    dsc.main(
        program='spor',
        version='spor v0.0.0')


if __name__ == '__main__':
    main()
