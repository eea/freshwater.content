"""Visualization status and all used urls"""
import json
from Products.Five.browser import BrowserView
from plone import api


class VisualizationsStatus(BrowserView):
    """Visualizations status and ussage"""
    def __call__(self):
        visualizations = self.get_visualizations()

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps({
            "data": visualizations, "count": len(visualizations)
        })

    def get_visualizations(self):
        """Get visualizations and gather all ussages"""
        result = api.content.find(portal_type="visualization")
        data = {}

        for brain in result:
            obj = brain.getObject()
            path = {
                "id": obj.id,
                "uid": obj.UID(),
                "url": brain.getURL(),
                "path": brain.getPath(),
                "review_state": brain.review_state,
                "created": obj.ModificationDate(),
                "modified": obj.CreationDate()
            }
            if obj.id in data:
                data[obj.id].append(path)
            else:
                data[obj.id] = [path]

        return data
