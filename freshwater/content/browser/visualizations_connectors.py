import os
import json
from Products.Five.browser import BrowserView
from plone import api


class VisualizationsConnectors(BrowserView):
    def __call__(self):
        connectors = self.get_related_data("discodataconnector")
        files = self.get_related_data("File")
        visualizations = self.get_visualizations(connectors, files)

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps({
            "data": visualizations,
            "count": len(visualizations)
        })

    def get_visualizations(self, connectors, files):
        result = api.content.find(portal_type="visualization")
        data = []

        for brain in result:
            obj = brain.getObject()

            visualization_attr = getattr(obj, 'visualization', None)
            provider_url = visualization_attr.get('provider_url')
            name = os.path.basename(provider_url)

            data.append({
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

        return data

    def get_related_data(self, portal_type):
        result = api.content.find(portal_type=portal_type)
        data = {}

        for brain in result:
            obj = brain.getObject()

            data[obj.id] = {
                "id": obj.id,
                "uid": obj.UID(),
                "url": brain.getURL(),
                "path": brain.getPath(),
                "title": obj.Title(),
            }

        return data

