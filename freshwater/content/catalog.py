from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from .blocks import BlocksTraverser


class BlockType(object):
    """Check block types."""

    def __init__(self, context, out):
        self.out = out
        self.context = context

    def __call__(self, block):
        _type = block.get("@type", "")

        print(_type)
        if _type:
            self.out.add(_type)


@indexer(IDexterityContent)
def block_types(obj):
    blocks_type = set()
    bt = BlockType(obj, blocks_type)
    traverser = BlocksTraverser(obj)
    traverser(bt)
    return list(blocks_type)
