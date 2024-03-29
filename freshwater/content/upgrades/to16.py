''' Upgrade to 16 '''

import logging

from plone import api
from plone.restapi.deserializer.utils import path2uid

from freshwater.content.blocks import BlocksTraverser

# pylint: disable = C0412

logger = logging.getLogger('eea.restapi.migration')

TYPES = ['countryHeaderDataBlock', 'conditionalDataBlock', 'plotly_chart']


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
        'https://water.europa.eu/api',
        'https://water.europa.eu',
    ]
    for bit in hosts:
        url = url.replace(bit, '')
    return url


def clean_provider_url(provider_url):
    """clean_provider_url"""
    provider_url = provider_url.replace('/freshwaternew', '/')
    provider_url = provider_url.replace('/freshwater-api', '/')
    provider_url = provider_url.replace('/freshwater/', '/')
    # provider_url = provider_url.replace('/freshwater', '')

    return provider_url


class ConditionalDataBlockTransformer(object):
    """ ConditionalDataBlockTransformer """

    def __init__(self, context):
        self.context = context

    def __call__(self, block):
        if (block or {}).get('@type') not in TYPES:
            return None

        def clean(url):
            """ clean """
            link = clean_provider_url(clean_url(url))
            return path2uid(context=self.context, link=link)

        dirty = False

        provider_url = block.get('provider_url', '')
        if provider_url:
            block['provider_url'] = clean(provider_url)
            dirty = True

        return dirty


class PlotlyChartTransformer(object):
    """Migrator for plotly charts."""

    def __init__(self, context):
        self.context = context

    def __call__(self, block):
        dirty = False

        def clean(url):
            """ clean """
            link = clean_provider_url(clean_url(url))
            return path2uid(context=self.context, link=link)

        if block.get('@type') == 'plotly_chart':
            if block['visualization'].get('provider_url'):
                provider_url = block['visualization']['provider_url']
                block['visualization']['provider_url'] = clean(provider_url)

            if block['visualization'].get('chartData', {}).get('provider_url'):
                chartData = block['visualization']['chartData']
                provider_url = chartData['provider_url']
                block['visualization']['chartData']['provider_url'] = clean(
                    provider_url)

            logger.info('fixed plotly block: in %s', self.context)
            dirty = True

        if block.get('@type') == 'countryHeaderDataBlock':
            if block.get("provider_url") is not None:
                block['provider_url'] = clean(block['provider_url'])

            dirty = True

        return dirty


def run_upgrade(setup_context):
    """ Run upgrade to 15
    """

    catalog = api.portal.get_tool('portal_catalog')

    brains = catalog.searchResults(portal_type='country_profile')

    for brain in brains:
        obj = brain.getObject()

        if hasattr(obj.aq_inner.aq_self, 'blocks') and \
                hasattr(obj.aq_inner.aq_self, 'blocks_layout'):
            traverser = BlocksTraverser(obj)

            divider_fixer = ConditionalDataBlockTransformer(obj)
            traverser(divider_fixer)

            plotly_fixer = PlotlyChartTransformer(obj)
            traverser(plotly_fixer)
