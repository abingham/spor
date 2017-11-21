import pathlib
import uuid
import yaml

from .anchor import Anchor, Context, make_anchor


def find_spor_repo(path, spor_dir='.spor'):
    while True:
        spor_path = path / spor_dir
        if spor_path.exists() and spor_path.is_dir():
            return spor_path

        if path == pathlib.Path(path.root):
            raise ValueError('No spor repository found')

        path = path.parent.resolve()


def _yaml_to_anchor(yml):
    before = yml['context']['before']
    after = yml['context']['after']
    line = yml['context']['line']
    ctx = Context(line, before, after)

    filename = yml['filename']
    line_number = yml['line_number']
    metadata = yml['metadata']
    cols = tuple(yml['columns']) if yml['columns'] else None

    return Anchor(
        filename=filename,
        line_number=line_number,
        context=ctx,
        metadata=metadata,
        columns=cols)


def _anchor_to_yaml(anchor):
    return {
        'filename': anchor.filename,
        'line_number': anchor.line_number,
        'columns': anchor.columns,
        'context': {
            'before': list(anchor.context.before),
            'line': anchor.context.line,
            'after': list(anchor.context.after)
        },
        'metadata': yaml.dump(anchor.metadata)
    }


class Store:
    def __init__(self, path, spor_dir='.spor'):
        self.repo_path = find_spor_repo(pathlib.Path(path))

    @staticmethod
    def initialize(path, spor_dir='.spor'):
        path = pathlib.Path(path)
        spor_path = path / spor_dir
        if spor_path.exists():
            raise ValueError(
                'spor directory already exists: {}'.format(
                    spor_path))
        spor_path.mkdir()

    def tracked_file(self, metadata):
        return self.repo_path.parent / metadata.filename

    def add(self, metadata, file_name, line_number, columns=None):
        anchor_id = uuid.uuid4().hex
        file_path = pathlib.Path(file_name).relative_to(self.repo_path.parent)
        data_path = self.repo_path / '{}.yml'.format(anchor_id)

        anchor = make_anchor(
            context_size=3,  # TODO: This needs to be configurable
            filepath=file_path,
            line_number=line_number,
            metadata=metadata,
            columns=columns)

        with open(data_path, mode='wt') as f:
            yaml.dump(_anchor_to_yaml(anchor), f)

        return anchor_id

    def find(self, file_name, line_number, columns=None):
        file_name = str(pathlib.Path(file_name).relative_to(self.repo_path.parent))
        return (
            anchor
            for anchor in self
            if anchor.filename == file_name
            if anchor.line_number == line_number
            # TODO: Match columns
        )

    def set(self, anchor_id, metadata):
        file_name = '{}.yml'.format(anchor_id)
        file_path = self.repo_path / file_name
        with open(file_path, mode='rt') as f:
            anchor = yaml.load(f.read())
        anchor.metadata = metadata
        with open(file_path, mode='wt') as f:
            yaml.dump(anchor, f)

    def delete(self, anchor_id):
        file_name = '{}.yml'.format(anchor_id)
        file_path = self.repo_path / file_name
        file_path.unlink()

    def __iter__(self):
        for spor_file in self.repo_path.glob('**/*.yml'):
            with open(spor_file) as handle:
                spec = yaml.load(handle.read())
                md = _yaml_to_anchor(spec)
                yield md
