from spor.alignment import align
from spor.anchor import make_anchor


def score(a, b):
    if a == b:
        return 3
    else:
        return -3


def gap_penalty(gap):
    if gap == 1:
        return 2
    else:
        gap * gap_penalty(1)


def _index_in_topic(index, anchor):
    return (index >= anchor.context.offset and
            index < anchor.context.offset + len(anchor.context.topic))


class AlignmentError(Exception):
    pass


def update(anchor):
    """Update an anchor based on the current contents of its source file.

    Args:
        anchor: The `Anchor` to be updated.

    Returns: A new `Anchor`, possibly identical to the input.

    Raises:
        AlignmentError: If no anchor could be created. The message of the
            exception will say what the problem is.
    """
    with anchor.file_path.open(mode='rt') as handle:
        source_text = handle.read()

    ctxt = anchor.context

    a_score, alignments = align(ctxt.full_text,
                                source_text,
                                score,
                                gap_penalty)
    # max_score = len(ctxt.full_text) * 3

    try:
        alignment = next(alignments)
    except StopIteration:
        raise ValueError('No alignments for anchor: {}'.format(anchor))

    anchor_offset = ctxt.offset - len(ctxt.before)

    source_indices = tuple(
        s_idx
        for (a_idx, s_idx) in alignment
        if a_idx is not None
        if s_idx is not None
        if _index_in_topic(a_idx + anchor_offset, anchor))

    if not source_indices:
        raise AlignmentError(
            "Best alignment does not map topic to updated source.")

    # TODO: This can throw index errors, indicating that there are no source
    # indices. Translate this to some reasonable API for this function.
    return make_anchor(
        file_path=anchor.file_path,
        offset=source_indices[0],
        width=len(source_indices),
        context_width=anchor.context_width,
        metadata=anchor.metadata)
