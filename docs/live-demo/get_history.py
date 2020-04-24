"""Get the git history for a file.

usage: get_history.py <repo-path> <file-path> <output-dir>
"""
import math
from pathlib import Path

import docopt
from git import Repo


def obj_from_path(tree, path):
    obj = tree
    for part in path.parts:
        obj = obj[part]
    return obj


def main():
    args = docopt.docopt(__doc__)
    repo_path = Path(args['<repo-path>'])
    file_path = Path(args['<file-path>']).relative_to(repo_path)

    output_dir = Path(args['<output-dir>'])
    output_dir.mkdir()

    repo = Repo(repo_path)
    commits = list(repo.iter_commits(paths=file_path))
    commits.reverse()
    for (idx, commit) in enumerate(commits):
        idx = '{:0{}}'.format(idx, math.ceil(math.log(len(commits), 10)))
        blob = obj_from_path(commit.tree, file_path)
        with (output_dir / f'{idx}-{file_path.name}').open(mode='wb') as handle:
            handle.write(blob.data_stream.read())


if __name__ == '__main__':
    main()
