import os
import json
from Products.Five.browser import BrowserView
from plone import api

"""
TODO: [x] Get all visualizations and related connectors
TODO: [] Handle .csv connectors
TODO: [] Map connectors to visualizations
TODO: [] Determine relationship between visualizations and connectors
TODO: [] Determine status of visualizations and used pages
"""

class MatrixConnectors(BrowserView):
    def __call__(self):
        visualizations_result = api.content.find(portal_type="visualization")
        connectors_result = api.content.find(portal_type="discodataconnector")
        files_result = api.content.find(portal_type="File")
        visualizations = []
        connectors = {}
        files = {}

        for brain in connectors_result:
            obj = brain.getObject()

            connectors[obj.id] = {
                "id": obj.id,
                "uid": obj.UID(),
                "url": brain.getURL(),
                "path": brain.getPath(),
                "title": obj.Title(),
                "description": obj.Description()
            }

        for brain in files_result:
            obj = brain.getObject()

            files[obj.id] = {
                "id": obj.id,
                "uid": obj.UID(),
                "url": brain.getURL(),
                "path": brain.getPath(),
                "title": obj.Title(),
                "description": obj.Description()
            }

        for brain in visualizations_result:
            obj = brain.getObject()
            connectors_result = api.content.find(portal_type="discodataconnector")

            visualization = getattr(obj, 'visualization', None)
            provider_url = visualization.get('provider_url')
            name = os.path.basename(provider_url)

            visualizations.append({
                "id": obj.id,
                "uid": obj.UID(),
                "url": brain.getURL(),
                "path": brain.getPath(),
                "title": obj.Title(),
                "description": obj.Description(),
                "provider_url": provider_url,
                "connector": connectors.get(name, None),
                "file": files.get(name, None)
            })

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(visualizations)
