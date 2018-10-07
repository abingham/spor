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



def alignments(repo):
    for anchor_id, anchor in repo.items():
        anchor_text = ''.join(anchor.context.before) + anchor.context.line + ''.join(anchor.context.after)
        # anchor_text = anchor.context.line

        with open(anchor.file_path, mode='rt') as handle:
            source_text = handle.read()


        print('=== anchor ===')
        print(anchor_text)
        print('======')
        print('=== source ===')
        print(source_text)
        print('======')

        a_score, alignments = align(anchor_text, source_text, score, gap_penalty)
        max_score = len(anchor_text) * 3

        print('alignment:', a_score / max_score)
        for alignment in alignments:
            print(alignment)
