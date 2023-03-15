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
from .utils import t2r

logger = logging.getLogger('freshwater.content')


class SetupMeasuresCatalogue(BrowserView):
    """ Crawler to get the measures from the nwrm site
    """

    nwrm_base_url = "http://nwrm.eu"

    def __call__(self):
        measures_url = "http://nwrm.eu/measures-catalogue"
        base_page = requests.get(measures_url)
        base_soup = BeautifulSoup(base_page.content, "html.parser")
        measures = base_soup.find_all("td", class_="views-field-title")

        for index, measure in enumerate(measures[:1]):
            time.sleep(0.5)

            anchor = measure.find("a")

            if not anchor:
                continue

            url_measure = self.nwrm_base_url + anchor.attrs["href"]
            page_measure = requests.get(url_measure)
            soup_measure = BeautifulSoup(
                page_measure.content, "html.parser")

            logger.info("Setup measure %s of %s %s ",
                        index+1, len(measures), url_measure)

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
            # case_studies = soup_measure.find(
            #     class_="field--name-field-nwrm-nwrm-css").find(
            #         class_="field__items")

            item = create_content(self.context, "measure", title=title)

            import pdb
            pdb.set_trace()

            # complete description
            file = create_content(item, "File", title=complete_descr_filename)
            file.file = NamedBlobFile(
                data=complete_descr_file, filename=complete_descr_filename)

            # other fields
            item.measure_code = code
            item.measure_sector = sector
            item.other_sector = other_sector
            item.measure_summary = t2r(summary)
            item.possible_benefits = t2r(possible_benefits)

            # images
            image_container = soup_measure.find(
                class_="field--name-field-illustration-s-").find(
                    class_='field__item')

            if image_container.find('table'):
                # multiple images
                pass
            else:
                # single image
                img_src = image_container.find('img').attrs['src']
                img_content = requests.get(img_src).content
                img_filename = image_container.findAll('p')[-2].text
                img_description = image_container.findAll(
                    'p')[-1].findAll()[-1].text

                img = create_content(
                    item, "Image", title=img_src.split('/')[-1])
                img.description = img_description
                img.image = NamedBlobImage(
                    data=img_content, filename=img_filename)

            # item.case_studies = t2r(case_studies)
            # item.complete_description = NamedBlobFile(
            #     data=complete_descr_file, filename=complete_descr_filename)

            item.reindexObject()

        alsoProvides(self.request, IDisableCSRFProtection)

        return "Setup completed!"
