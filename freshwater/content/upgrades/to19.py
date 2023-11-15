''' Upgrade to 19 '''

import logging
from plone import api
# pylint: disable = C0412

def run_upgrade(context):
    """ Run upgrade to 19
        Set autoscale on Tableau visualization
    """

    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog.unrestrictedSearchResults(portal_type='visualization_tableau')

    for brain in brains:
        obj = brain.getObject()
        obj.tableau_visualization["autoScale"] = True

        obj.reindexObject()
