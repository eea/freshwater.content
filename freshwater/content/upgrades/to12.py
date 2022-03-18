''' Upgrade to 12 '''

import logging
from plone import api
from freshwater.content.blocks import BlocksTraverser

logger = logging.getLogger('eea.restapi.migration')

chart_block_types = ['filteredConnectedPlotlyChart',
                     'connected_plotly_chart']


def clean_url(url):
    """clean_url"""

    if not url:
        return url

    hosts = [
        'http://localhost:8080',
        'http://backend:8080',
        'https://demo-freshwater.eea.europa.eu/api',
        'https://demo-freshwater.eea.europa.eu',
        'https://demo-freshwater.devel4cph.eea.europa.eu',
        'https://demo-freshwater.devel4cph.eea.europa.eu/api',
        ]
    for bit in hosts:
        url = url.replace(bit, '')
    return url


class PlotlyChartTransformer(object):

    """Migrator for plotly charts."""

    def __init__(self, context):
        self.context = context

    def __call__(self, block):
        dirty = False

        if block.get('@type') in chart_block_types:
            old = block
            block['@type'] = 'plotly_chart'
            block['height'] = '550'
            block['download_button'] = False
            block['visualization'] = {}
            block['visualization']['chartData'] = block['chartData']
            block['provider_url'] = block.pop('url')
            block.pop('chartData', None)

            logger.info('fixed plotly block: in %s (%s) => (%s)',
                        self.context, old, block)
            dirty = True

        return dirty


def run_upgrade(setup_context):
    """ Run upgrade to 12
    """

    catalog = api.portal.get_tool('portal_catalog')

    brains = catalog(_nonsense=True)

    for brain in brains:
        obj = brain.getObject()

        if hasattr(obj.aq_inner.aq_self, 'blocks') and \
                hasattr(obj.aq_inner.aq_self, 'blocks_layout'):
            traverser = BlocksTraverser(obj)

            plotlychart_fixer = PlotlyChartTransformer(obj)
            traverser(plotlychart_fixer)
