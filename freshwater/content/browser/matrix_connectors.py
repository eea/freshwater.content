import json
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
        results = api.content.find(portal_type="visualization")
        visualizations = []
        for brain in results:
            obj = brain.getObject()

            visualizations.append({
                "id": obj.id,
                "url": brain.getURL(),
                "path": brain.getPath(),
                "title": obj.Title(),
                "description": obj.Description()
            })

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(visualizations)
