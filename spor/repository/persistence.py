import json

import spor.anchor


def save_anchor(fp, anchor, repo_root):
    json.dump(anchor, fp, cls=make_encoder(repo_root))


def load_anchor(fp, repo_root):
    return json.load(fp, cls=make_decoder(repo_root))


def make_encoder(repo_root):
    class JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, spor.anchor.Anchor):
                return {
                    '!spor_anchor': {
                        'file_path': str(obj.file_path.relative_to(repo_root)),
                        'context': obj.context,
                        'context_width': obj.context_width,
                        'metadata': obj.metadata
                    }
                }
            elif isinstance(obj, spor.anchor.Context):
                return {
                    '!spor_context': {
                        'before': obj.before,
                        'after': obj.after,
                        'topic': obj.topic,
                        'offset': obj.offset
                    }
                }

            return super().default(self, obj)

    return JSONEncoder


def make_decoder(repo_root):
    class JSONDecoder(json.JSONDecoder):
        def __init__(self):
            super().__init__(object_hook=self.anchor_decoder)

        def anchor_decoder(self, dct):
            if '!spor_anchor' in dct:
                data = dct['!spor_anchor']
                return spor.anchor.Anchor(
                    file_path=repo_root / data['file_path'],
                    context=data['context'],
                    context_width=data['context_width'],
                    metadata=data['metadata'])

            elif '!spor_context' in dct:
                return spor.anchor.Context(**dct['!spor_context'])

            return dct

    return JSONDecoder
