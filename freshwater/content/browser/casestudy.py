""" case studies module """

import logging
import time
import requests
from bs4 import BeautifulSoup

from Products.Five.browser import BrowserView
from plone.dexterity.utils import createContentInContainer as create_content
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

from .utils import t2r

logger = logging.getLogger('freshwater.content')


class SetupCaseStudies(BrowserView):
    """ Crawler to get the case studies from the nwrm site
    """

    nwrm_base_url = "http://nwrm.eu"

    def get_section_by_id(self, soup, id_section):
        """ return section """

        section = soup.find(id=id_section)

        if not section:
            return ''

        res = section.find(class_="details-wrapper")

        return res

    def __call__(self):
        case_studies_url = "http://nwrm.eu/list-of-all-case-studies"
        base_page = requests.get(case_studies_url)
        base_soup = BeautifulSoup(base_page.content, "html.parser")
        case_studies = base_soup.find_all("td", class_="views-field-title")

        for index, case_study in enumerate(case_studies):
            time.sleep(0.5)

            anchor = case_study.find("a")

            if not anchor:
                continue

            url_case_study = self.nwrm_base_url + anchor.attrs["href"]
            page_case_study = requests.get(url_case_study)
            soup_case_study = BeautifulSoup(
                page_case_study.content, "html.parser")

            logger.info("Setup case study %s of %s %s ",
                        index+1, len(case_studies), url_case_study)

            title = soup_case_study.find(class_="field--name-title").text
            general = self.get_section_by_id(
                soup_case_study, 'edit-group-general')
            site_info = self.get_section_by_id(
                soup_case_study, 'edit-group-site-information')
            monitoring_maintenance = self.get_section_by_id(
                soup_case_study, 'edit-group-monitoring-maintenance')
            performance = self.get_section_by_id(
                soup_case_study, 'edit-group-performance')
            design_implementations = self.get_section_by_id(
                soup_case_study, 'edit-group-design-implementations')
            lessons_risks = self.get_section_by_id(
                soup_case_study, 'edit-group-lessons-risks-implications')
            policy_general_gov = self.get_section_by_id(
                soup_case_study, 'edit-group-policy-general-governance-')
            socio_economic = self.get_section_by_id(
                soup_case_study, 'edit-group-socio-economic')
            biophysical_impacts = self.get_section_by_id(
                soup_case_study, 'edit-group-biophysical-impacts')

            item = create_content(self.context, "case_study", title=title)

            item.general = t2r(general)
            item.site_information = t2r(site_info)
            item.monitoring_maintenance = t2r(monitoring_maintenance)
            item.performance = t2r(performance)
            item.design_and_implementations = t2r(design_implementations)
            item.lessons_risks_implications = t2r(lessons_risks)
            item.policy_general_governance = t2r(policy_general_gov)
            item.socio_economic = t2r(socio_economic)
            item.biophysical_impacts = t2r(biophysical_impacts)

            item.reindexObject()

        alsoProvides(self.request, IDisableCSRFProtection)

        return "Setup completed!"
