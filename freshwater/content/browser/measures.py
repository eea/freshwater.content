""" measures catalogue module """

import logging
import time
import requests
from bs4 import BeautifulSoup

from Products.Five.browser import BrowserView
from plone.dexterity.utils import createContentInContainer as create_content
from plone.protect.interfaces import IDisableCSRFProtection
from plone.namedfile.file import NamedBlobImage, NamedBlobFile
from zope.interface import alsoProvides
from collective.relationhelpers import api as relapi
from .utils import t2r

logger = logging.getLogger('freshwater.content')


class SetupMeasuresCatalogue(BrowserView):
    """ Crawler to get the measures from the nwrm site
    """

    nwrm_base_url = "http://nwrm.eu"

    @property
    def case_studies(self):
        """ get all case studies """
        portal_catalog = self.context.portal_catalog
        results = portal_catalog.searchResults(portal_type='case_study')

        return [x.getObject() for x in results]

    def get_case_study_by_title(self, title):
        """ get related case study"""
        result = [x for x in self.case_studies if x.title == title]

        if not result:
            return None

        return result[0]

    def __call__(self):
        measures_url = "http://nwrm.eu/measures-catalogue"
        base_page = requests.get(measures_url)
        base_soup = BeautifulSoup(base_page.content, "html.parser")
        measures = base_soup.find_all("td", class_="views-field-title")

        for index, measure in enumerate(measures):
            try:
                time.sleep(0.2)

                anchor = measure.find("a")

                if not anchor:
                    continue

                url_measure = self.nwrm_base_url + anchor.attrs["href"]
                page_measure = requests.get(url_measure)
                soup_measure = BeautifulSoup(
                    page_measure.content, "html.parser")

                logger.info("Setup measure %s of %s %s ",
                            index+1, len(measures), url_measure)

                # setup soup
                title = soup_measure.find(class_="field--name-title").text
                code = soup_measure.find(
                    class_="field--name-field-nwrm-nwrm-code").find(
                        class_="field__item").text
                sector = soup_measure.find(
                    class_="field--name-field-nwrm-real-sector").find(
                        class_="field__item").text
                other_sector = soup_measure.find(
                    class_="field--name-field-other-sector-s-") or ''

                if other_sector:
                    other_sector = other_sector.findAll(
                        class_="field__item")
                    other_sector = ", ".join([x.text for x in other_sector])

                complete_description = soup_measure.find(
                    class_="field--name-field-nwrm-nwrm-file").find(
                        class_="field__item")
                complete_descr_url = self.nwrm_base_url + \
                    complete_description.find('a').attrs['href']
                complete_descr_file = requests.get(complete_descr_url).content
                complete_descr_filename = complete_description.find('a').text

                summary = soup_measure.find(
                    class_="field--name-field-nwrm-nwrm-summary").find(
                        class_="field__item")
                possible_benefits = soup_measure.find(
                    class_="field--name-field-nwrm-benefits-w-level").find(
                        class_="field__items")
                case_studies = soup_measure.find(
                    class_="field--name-field-nwrm-nwrm-css")

                if case_studies:
                    case_studies = case_studies.findAll(class_="field__item")

                item = create_content(self.context, "measure", title=title)

                # set object attribute other fields
                item.measure_code = code
                item.measure_sector = sector
                item.other_sector = other_sector
                item.measure_summary = t2r(summary)
                item.possible_benefits = t2r(possible_benefits)

                # PDF complete description
                file_desc = create_content(
                    item, "File", title=complete_descr_filename)
                file_desc.file = NamedBlobFile(
                    data=complete_descr_file, filename=complete_descr_filename)

                # images
                image_container = soup_measure.find(
                    class_="field--name-field-illustration-s-").find(
                        class_='field__item')

                if image_container.find('table'):
                    # multiple images
                    table_rows = image_container.findAll('tr')
                    # first row has the images, second row the title and source
                    first_row = table_rows[0].findAll('td')
                    second_row = table_rows[1].findAll('td')

                    for img_index, _ in enumerate(first_row):
                        img_src = first_row[img_index].find('img').attrs['src']
                        img_content = requests.get(img_src).content
                        img_filename = img_src.split('/')[-1]
                        # sometimes in the second row we have lesser columns
                        # because of colspan
                        try:
                            img_title = second_row[img_index].findAll(
                                'p')[0].text
                            img_description = second_row[img_index].findAll(
                                'p')[1].text
                        except Exception:
                            img_title = second_row[-1].findAll('p')[0].text
                            img_description = second_row[-1].findAll(
                                'p')[1].text

                        img = create_content(
                            item, "Image", title=img_title)
                        img.description = img_description
                        img.image = NamedBlobImage(
                            data=img_content, filename=img_filename)
                else:
                    # single image
                    img_src = image_container.find('img').attrs['src']
                    img_content = requests.get(img_src).content
                    img_title = image_container.findAll('p')[-2].text
                    img_description = image_container.findAll('p')[-1].text
                    img_filename = img_src.split('/')[-1]

                    img = create_content(
                        item, "Image", title=img_title)
                    img.description = img_description
                    img.image = NamedBlobImage(
                        data=img_content, filename=img_filename)

                # set case studies relation
                if case_studies:
                    for case_study in case_studies:
                        cs_title = case_study.find("a").text
                        case_study_obj = self.get_case_study_by_title(cs_title)

                        if not case_study_obj:
                            continue

                        relapi.link_objects(
                            item, case_study_obj, 'case_studies')

                item.reindexObject()
            except Exception:
                continue

        alsoProvides(self.request, IDisableCSRFProtection)

        return "Setup completed!"
