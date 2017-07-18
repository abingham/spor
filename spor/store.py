import yaml

from .metadata import make_metadata


def find_spor_dir(path):
    while True:
        path = path.parent.resolve()
        sporpath = path / '.spor'
        if sporpath.exists() and sporpath.is_dir():
            return sporpath

        if path == path.root:
            raise ValueError('No .spor directory found')


class Store:
    def __init__(self, path):
        self.path = path

    def tracked_file(self, metadata):
        return self.path.parent / metadata.filename

    def __iter__(self):
        for spor_file in self.path.glob('**/*.yml'):
            with open(spor_file) as f:
                spec = yaml.load(f.read())
                md = make_metadata(spec)
                yield md
