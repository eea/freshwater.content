""" NWRM benefits tables"""
import json

from Products.Five.browser import BrowserView
from plone import api


class BenefitsTableData(BrowserView):
    """ Return the data needed for the NWRM benefits tables """

    def __call__(self):
        portal_catalog = api.portal.get_tool("portal_catalog")
        results = portal_catalog.searchResults(portal_type='measure')
        measures = [x.getObject() for x in results]

        data = []

        for measure in measures:
            row_data = {}
            row_data['title'] = measure.title
            row_data['code'] = measure.measure_code
            row_data['sector'] = measure.measure_sector
            row_data['other_sector'] = measure.other_sector
            row_data['biophysical_impacts'] = list(
                measure._nwrm_biophysical_impacts)
            row_data['ecosystem_services'] = list(
                measure._nwrm_ecosystem_services)
            row_data['policy_objectives'] = list(
                measure._nwrm_policy_objectives)

            data.append(row_data)

        response = self.request.response
        response.setHeader("Content-type", "application/json")

        return json.dumps(data)
