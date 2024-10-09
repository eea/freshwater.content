""" module to fetch chemical data from discodata and update the content """

import logging
import requests

from Products.Five.browser import BrowserView
from plone.api.content import transition
from plone.dexterity.utils import createContentInContainer
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from .discodata_queries import (
    SW_PRIORITY_SUBSTANCE_EU27_2022, SW_PRIORITY_SUBSTANCE_COUNTRIES_2022,
    SW_RBSP_POLLUTANT_COUNTRIES_2022, SW_RBSP_POLLUTANT_EU27_2022,
    GW_POLLUTANT_COUNTRIES_2022, GW_POLLUTANT_EU27_2022)

logger = logging.getLogger('freshwater.content')

ENDPOINT_URL = "https://discodata.eea.europa.eu/sql"
CREATION_PATH = {
    "SWPrioritySubstance": "/Plone/europe-freshwater/water-framework-directive"
    "/surface-water-chemical-status"
    "/priority-substances-causing-failure-to-good-chemical-status",

    "swFailingRBSP": "/Plone/europe-freshwater/water-framework-directive"
    "/ecological-status-of-surface-water/river-basin-specific-pollutants",

    "GWPollutant": "/Plone/europe-freshwater/water-framework-directive"
    "/groundwater-bodies-chemical-status/groundwater-pollutants",
}


class UpdateChemicalData(BrowserView):
    """ update chemical data """

    def update_data(self, query):
        """ update data """

        count_portal_catalog, count_updated, count_created = 0, 0, 0
        # GET data from discodata
        logger.info("Fetching data from discodata...")
        data = {}
        data["query"] = query
        req = requests.post(ENDPOINT_URL, data, timeout=30)
        data = req.json()
        logger.info("Data fetched from discodata: %s", len(data['results']))

        # get objects from portal_catalog and filter them
        brains = self.context.portal_catalog.searchResults(
            portal_type='chemical')
        objects_filtered = []

        chemical_type = data['results'][0]['chemical_type']
        management_plan = data['results'][0]['management_plan']
        creation_path = CREATION_PATH[chemical_type]
        parent = self.context.portal_catalog.searchResults(
            path={'query': creation_path, 'depth': 0})
        parent = parent[0].getObject()

        for brain in brains:
            obj = brain.getObject()

            if getattr(obj, 'chemical_type') != chemical_type:
                continue

            if getattr(obj, 'management_plan') != management_plan:
                continue

            objects_filtered.append(obj)

        count_portal_catalog = len(objects_filtered)
        logger.info("Found %s objects in portal_catalog", count_portal_catalog)

        # update objects
        for item in data['results']:
            found = False

            for obj in objects_filtered:
                if obj.id != item['id']:
                    continue

                found = True
                count_updated += 1
                obj.number_of_appearances = item['number_of_appearances']

                if chemical_type != 'GWPollutant':
                    obj.number_of_categories = item['number_of_categories']

                if chemical_type == 'GWPollutant':
                    obj.number_of_area = item['number_of_area']

                obj.number_of_countries = item['number_of_countries']

                obj._p_changed = True
                obj.reindexObject()

            # create new object
            if not found:
                count_created += 1
                c_obj = createContentInContainer(
                    parent,
                    'chemical',
                    title=item['title'],
                    id=item['id'],
                )
                c_obj.number_of_appearances = item['number_of_appearances']

                if chemical_type != 'GWPollutant':
                    c_obj.number_of_categories = item['number_of_categories']

                if chemical_type == 'GWPollutant':
                    c_obj.number_of_area = item['number_of_area']

                c_obj.number_of_countries = item['number_of_countries']
                c_obj.chemical_type = chemical_type
                c_obj.management_plan = management_plan
                c_obj.country = item['country']
                transition(obj=c_obj, transition='publish')

                c_obj._p_changed = True
                c_obj.reindexObject()

        logger.info("Updated %s objects", count_updated)
        logger.info("Created %s objects", count_created)
        logger.info("Total %s objects", (count_updated + count_created))
        logger.info("Finished updating %s", chemical_type)

        return {
            "portal_catalog": count_portal_catalog,
            "updated": count_updated,
            "created": count_created,
        }

    def __call__(self):
        """ update chemical data """
        alsoProvides(self.request, IDisableCSRFProtection)

        return {
            "SW_PRIORITY_SUBSTANCE_EU27_2022":
                self.update_data(SW_PRIORITY_SUBSTANCE_EU27_2022),
            "SW_PRIORITY_SUBSTANCE_COUNTRIES_2022":
                self.update_data(SW_PRIORITY_SUBSTANCE_COUNTRIES_2022),
            "SW_RBSP_POLLUTANT_COUNTRIES_2022":
                self.update_data(SW_RBSP_POLLUTANT_COUNTRIES_2022),
            "SW_RBSP_POLLUTANT_EU27_2022":
                self.update_data(SW_RBSP_POLLUTANT_EU27_2022),
            "GW_POLLUTANT_COUNTRIES_2022":
                self.update_data(GW_POLLUTANT_COUNTRIES_2022),
            "GW_POLLUTANT_EU27_2022":
                self.update_data(GW_POLLUTANT_EU27_2022),
        }
