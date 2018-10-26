import difflib

from .anchor import make_anchor


def _split_keep_sep(s, sep):
    toks = s.split(sep)
    result = [tok + sep for tok in toks[:-1]]
    result.append(toks[-1])
    return result


def _context_diff(file_name, c1, c2):
    c1_text = _split_keep_sep(c1.full_text, '\n')
    c2_text = _split_keep_sep(c2.full_text, '\n')

    return difflib.context_diff(
        c1_text, c2_text,
        fromfile='{} [original]'.format(file_name),
        tofile='{} [current]'.format(file_name))


def validate(repo):
    for (anchor_id, anchor) in repo.items():
        # TODO: Account for the fact that this can raise a ValueError if it
        # can't read the specified topic.
        new_anchor = make_anchor(
            file_path=anchor.file_path,
            offset=anchor.context.offset,
            width=len(anchor.context.topic),
            context_width=anchor.context_width,
            metadata=anchor.metadata,
            root=repo.root)

        assert anchor.file_path == new_anchor.file_path
        assert anchor.context.offset == new_anchor.context.offset
        assert len(anchor.context.topic) == len(new_anchor.context.topic)
        assert anchor.metadata == new_anchor.metadata

        diff = tuple(
            _context_diff(
                str(repo.root / anchor.file_path),
                anchor.context,
                new_anchor.context))

        if diff:
            yield (anchor.file_path, diff)
