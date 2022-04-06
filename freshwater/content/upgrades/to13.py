''' Upgrade to 13 '''

import logging
from plone import api
from freshwater.content.blocks import BlocksTraverser

logger = logging.getLogger('eea.restapi.migration')

class ImageCardTransformer(object):

    """Migrator for image cards."""

    def __init__(self, context):
        self.context = context

    def __call__(self, block):
        dirty = False

        if block.get('@type') == 'customCardsBlock':
            old = block
            block['@type'] = 'imagecards'

            logger.info('fixed imagecard block: in %s (%s) => (%s)',
                        self.context, old, block)
            dirty = True

        return dirty


def run_upgrade(setup_context):
    """ Run upgrade to 13
    """

    catalog = api.portal.get_tool('portal_catalog')

    brains = catalog(_nonsense=True)

    for brain in brains:
        obj = brain.getObject()

        if hasattr(obj.aq_inner.aq_self, 'blocks') and \
                hasattr(obj.aq_inner.aq_self, 'blocks_layout'):
            traverser = BlocksTraverser(obj)

            blockimagecard_fixer = ImageCardTransformer(obj)
            traverser(blockimagecard_fixer)
