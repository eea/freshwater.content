''' Upgrade to 15 '''

import logging
from plone import api
from freshwater.content.blocks import BlocksTraverser
from plone.restapi.serializer.utils import uid_to_url
from urllib.parse import urlparse

logger = logging.getLogger('eea.restapi.migration')


class DividerBlockTransformer(object):

    """Migrator for divider block."""

    def __init__(self, context):
        self.context = context

    def __call__(self, block):
        dirty = False

        if block.get('@type') == 'splitter':
            old = block
            block['@type'] = "dividerBlock"

            if block.get("style") == 'simple':
                block['fitted'] = True
                block['hidden'] = True

            if block.get("style") == 'inline':
                block['fitted'] = True

            if block.get("style") == 'line':
                block['fitted'] = True
                block['short'] = True

            block.pop('style', None)

            logger.info('fixed plotly block: in %s (%s) => (%s)',
                        self.context, old, block)
            dirty = True

        return dirty

class PlotlyChartTransformer(object):
    """Migrator for plotly charts."""

    def __init__(self, context):
        self.context = context

    def __call__(self, block):
        dirty = False

        if block.get('@type') == 'plotly_chart':
            old = block
            block['download_button'] = False
            block['with_sources'] = False

            if block.get("provider_url") is not None:
                url = uid_to_url(block['provider_url'])
                path = urlparse(url).path

                if path[:6] == "/Plone":
                    path = path[6:]

                block['visualization']['provider_url'] = path
            else:
                block['visualization']['provider_url'] = ''

            block.pop('provider_url', None)

            logger.info('fixed plotly block: in %s (%s) => (%s)',
                        self.context, old, block)
            dirty = True

        return dirty


def run_upgrade(setup_context):
    """ Run upgrade to 15
    """

    catalog = api.portal.get_tool('portal_catalog')

    brains = catalog(_nonsense=True)

    for brain in brains:
        obj = brain.getObject()

        if hasattr(obj.aq_inner.aq_self, 'blocks') and \
                hasattr(obj.aq_inner.aq_self, 'blocks_layout'):
            traverser = BlocksTraverser(obj)

            divider_fixer = DividerBlockTransformer(obj)
            traverser(divider_fixer)

            plotly_fixer = PlotlyChartTransformer(obj)
            traverser(plotly_fixer)
