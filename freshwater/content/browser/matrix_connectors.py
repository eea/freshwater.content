import json
from z3c.relationfield.schema import RelationChoice
from plone.app.vocabularies.catalog import CatalogSource
from DateTime.DateTime import DateTime
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import iterSchemata

"""
TODO: [x] Get all visualizations (Too much data to get siblings, think about it)
TODO: [] Get all connectors / avoid sandbox
TODO: [] Determine relationship between visualizations and connectors
TODO: [] Determine status of visualizations and used pages
"""

class MatrixConnectors(BrowserView):
    def __call__(self):
        visualizations_result = api.content.find(portal_type="visualization")
        connectors_result = api.content.find(portal_type="discodataconnector")
        visualizations = []
        connectors = []

        for brain in connectors_result:
            obj = brain.getObject()

            connectors.append({
                "id": obj.id,
                "uid": obj.UID(),
                "url": brain.getURL(),
                "path": brain.getPath(),
                "title": obj.Title(),
                "description": obj.Description()
            })

        for brain in visualizations_result:
            obj = brain.getObject()

            visualizations.append({
                "id": obj.id,
                "uid": obj.UID(),
                "url": brain.getURL(),
                "path": brain.getPath(),
                "title": obj.Title(),
                "description": obj.Description()
            })

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps({"visualizations": visualizations, "connectors": connectors})
