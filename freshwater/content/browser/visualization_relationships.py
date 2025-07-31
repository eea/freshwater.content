"""Visualizations relationships with connectors"""
import os
import json
from Products.Five.browser import BrowserView
from plone import api


class VisualizationRelationships(BrowserView):
    """Visualizations relationships"""
    def __call__(self):
        connectors = self.get_data("discodataconnector")
        files = self.get_data("File")
        visualizations = self.get_visualizations(connectors, files)

        start = self.safe_int(self.request.get('b_start'), 0)
        size = self.safe_int(self.request.get('b_size'), 10)

        total = len(visualizations)
        end = start + size
        sliced = visualizations[start:end]


        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps({
            "data": sliced,
            "count": len(visualizations)
        })

    def get_visualizations(self, connectors, files):
        """Get visualizations and add connectors and files relationships"""
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

    def get_data(self, portal_type):
        """Get all data based on type to be mapped on visualizations"""
        result = api.content.find(portal_type=portal_type)
        data = {}

        for brain in result:
            obj = brain.getObject()

            data[obj.id] = {
                "id": obj.id,
                "uid": obj.UID(),
                "url": brain.getURL(),
                "path": brain.getPath().replace('/Plone', ''),
                "title": obj.Title(),
            }

        return data

    def safe_int(self, value, default):
        try:
            return max(1, int(value))
        except (ValueError, TypeError):
            return default
