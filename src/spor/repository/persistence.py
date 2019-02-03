import yaml

import spor.anchor


def save_anchor(fp, anchor, repo_root):
    d = {
        'file_path': str(anchor.file_path.relative_to(repo_root)),
        'encoding': anchor.encoding,
        'context': _save_context(anchor.context),
        'metadata': anchor.metadata
    }
    
    yaml.dump(d, fp)


def load_anchor(fp, repo_root):
    d = yaml.load(fp)
    context = _load_context(d['context'])
    return spor.anchor.Anchor(
        file_path=repo_root / d['file_path'],
        encoding=d['encoding'],
        context=context,
        metadata=d['metadata'])


def _save_context(context):
    return {
        'before': context.before,
        'offset': context.offset,
        'topic': context.topic,
        'after': context.after,
        'width': context.width
    }


def _load_context(d):
    return spor.anchor.Context(
        offset=d['offset'],
        topic=d['topic'],
        before=d['before'],
        after=d['after'],
        width=d['width'])