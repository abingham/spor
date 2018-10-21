from spor.alignment import align


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


def update(anchor):
    anchor_text = ''.join(anchor.context.before) + anchor.context.line + ''.join(anchor.context.after)
    # anchor_text = anchor.context.line

    with open(anchor.file_path, mode='rt') as handle:
        source_text = handle.read()

    a_score, alignments = align(anchor_text, source_text, score, gap_penalty)
    max_score = len(anchor_text) * 3

    try:
        alignment = next(alignments)
    except StopIteration:
        raise ValueError('No alignments for anchor: {}'.format(anchor))

    # For each char in the anchor's line, the line in the new anchor is the correspondence from the alignment.


    print(alignment)
