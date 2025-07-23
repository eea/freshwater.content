import os
import json
from Products.Five.browser import BrowserView
from plone import api

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
            connectors_result = api.content.find(portal_type="discodataconnector")

            visualization = getattr(obj, 'visualization', None)
            provider_url = visualization.get('provider_url')
            filename = os.path.basename(provider_url)
            name = os.path.splitext(filename)[0]

            visualizations.append({
                "id": obj.id,
                "uid": obj.UID(),
                "url": brain.getURL(),
                "path": brain.getPath(),
                "title": obj.Title(),
                "description": obj.Description(),
                "provider_url": provider_url,
                "connector": name
            })

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps({"visualizations": visualizations, "connectors": connectors})
