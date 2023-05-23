import json
import logging

# from eea.climateadapt.translation.utils import translate_text
from plone.api.portal import get_tool
from Products.Five import BrowserView
# from zope.component import getUtility
# from zope.schema.interfaces import IVocabularyFactory

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

logger = logging.getLogger("eea.climateadapt")


class Items(BrowserView):
    def __call__(self):
        """"""
        # factory = getUtility(
        #     IVocabularyFactory, "eea.climateadapt.aceitems_climateimpacts"
        # )
        # vocabulary_impacts = factory(self.context)
        # factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_sectors")
        # vocabulary_sectors = factory(self.context)

        results = {
            "type": "FeatureCollection",
            "metadata": {
                "generated": 1615559750000,
                "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson",
                "title": "WISE Freshwater arcgis items",
                "status": 200,
                "api": "1.10.3",
                "count": 10739,
            },
            "features": [],
        }

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "case_study",
                ],
                # "path": "/",
                # "review_state": "published",
            }
        )

        iPos = 0
        for brain in brains:
            obj = brain.getObject()
            if not getattr(obj, "nwrm_geolocation", ""):
                continue
            long_description = ""
            measures = []

            if obj.measures:
                measures = [
                    {"id": measure.to_id,
                    "title": measure.to_object.title,
                    "path": measure.to_path.replace("/Plone", "")}
                    for measure in obj.measures
                ]
            results["features"].append(
                {
                    "properties": {
                        "portal_type": obj.portal_type.replace(
                            "eea.climateadapt.", ""
                        ),
                        "nwrm_type": obj.nwrm_type,
                        "title": obj.title,
                        "description": long_description,
                        "url": brain.getURL(),
                        "image": "",  # obj.primary_photo and brain.getURL() + "/@@images/primary_photo/preview"
                        "measures": measures
                    },
                    "geometry": {
                        "type": "Point",
                        # "coordinates": [geo.x, geo.y]
                        "svg": {"fill_color": "#009900"},
                        "color": "#009900",
                        "coordinates": [
                            # "6.0142918",
                            # "49.5057481"
                            obj.nwrm_geolocation.split(',')[0],
                            obj.nwrm_geolocation.split(',')[1],
                        ],
                    },
                }
            )
            iPos = iPos + 1

        response = self.request.response
        response.setHeader("Content-type", "application/json")

        return json.dumps(results)
