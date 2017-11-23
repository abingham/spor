import difflib

from .anchor import make_anchor


def _context_diff(file_name, c1, c2):
    c1_text = list(c1.before) + [c1.line] + list(c1.after)
    c2_text = list(c2.before) + [c2.line] + list(c2.after)

    return difflib.context_diff(
        c1_text, c2_text,
        fromfile='{} [original]'.format(file_name),
        tofile='{} [current]'.format(file_name))


def validate(repo):
    for (anchor_id, anchor) in repo:
        context_size = max(len(anchor.context.before), len(anchor.context.after))
        new_anchor = make_anchor(
            context_size=context_size,
            file_path=anchor.file_path,
            line_number=anchor.line_number,
            metadata=anchor.metadata,
            columns=anchor.columns,
            root=repo.root)

        assert anchor.file_path == new_anchor.file_path
        assert anchor.line_number == new_anchor.line_number
        assert anchor.columns == new_anchor.columns
        assert anchor.metadata == new_anchor.metadata

        diff = tuple(
            _context_diff(
                str(repo.root / anchor.file_path),
                anchor.context,
                new_anchor.context))

        if diff:
            yield (anchor.file_path, diff)
