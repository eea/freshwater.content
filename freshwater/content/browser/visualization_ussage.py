"""Visualization status and all used urls"""
import json
from Products.Five.browser import BrowserView
from plone import api


class VisualizationUssage(BrowserView):
    """Visualizations ussage and status"""
    def __call__(self):
        visualizations = self.get_visualizations()

        start = self.safe_int(self.request.get('b_start'), 0)
        size = self.safe_int(self.request.get('b_size'), 10)

        total = len(visualizations)
        end = start + size
        items = list(visualizations.items())
        sliced = items[start:end]

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps({
            "data": dict(sliced), "count": total,
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
                "path": brain.getPath().replace("/Plone", ""),
                "review_state": brain.review_state,
                "created": obj.ModificationDate(),
                "modified": obj.CreationDate(),
                "title": obj.Title(),
                "type_title": obj.portal_type
            }
            if obj.id in data:
                data[obj.id].append(path)
            else:
                data[obj.id] = [path]

        return data

    def safe_int(self, value, default):
        """Safe format to int"""
        try:
            return max(1, int(value))
        except (ValueError, TypeError):
            return default
