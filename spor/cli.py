import docopt_subcommands as dsc
import pathlib
import yaml


def find_metadata(spor_dir, source_file):
    spor_dir = pathlib.Path(spor_dir)
    for spor_file in spor_dir.glob('**/*.yml'):
        with open(spor_file) as f:
            spec = yaml.load(f.read())
            if pathlib.Path(spec['filename']) == spor_dir.parent.joinpath(source_file):
                yield spec['metadata']


@dsc.command()
def list_handler(args):
    """usage: {program} list <spor-dir> <source-file>
    """
    for md in find_metadata(args['<spor-dir>'], args['<source-file>']):
        print(md)

dsc.main(
    program='spor',
    version='spor v0.0.0')
