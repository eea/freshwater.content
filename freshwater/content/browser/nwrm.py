""" module to setup NWRM data """

import logging
import time
import requests
import traceback
from bs4 import BeautifulSoup

from Products.Five.browser import BrowserView
from plone import api
from plone.dexterity.utils import createContentInContainer as create_content
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.protect.interfaces import IDisableCSRFProtection
from plone.namedfile.file import NamedBlobImage, NamedBlobFile
from zope.component import queryUtility
from zope.interface import alsoProvides
from collective.relationhelpers import api as relapi
from .utils import t2r

logger = logging.getLogger('freshwater.content')

NWRM_BASE_URL = "http://nwrm.eu"


def get_section_by_id(soup, id_section):
    """ return section """

    section = soup.find(id=id_section)

    if not section:
        return ''

    res = section.find(class_="details-wrapper")

    return res


def get_object_by_id(content_type, obj_id):
    """ get related object type """
    portal_catalog = api.portal.get_tool("portal_catalog")
    results = portal_catalog.searchResults(portal_type=content_type, id=obj_id)

    result = [x.getObject() for x in results]

    if not result:
        return None

    return result[0]


def create_source(url_source, sources_folder):
    time.sleep(0.2)
    url_normalizer = queryUtility(IURLNormalizer)

    page_source = requests.get(url_source)
    soup_source = BeautifulSoup(
        page_source.content, "html.parser")

    title = soup_source.find(class_="field--name-title").text
    id_source = url_normalizer.normalize(url_source.split("/")[-1])
    item = create_content(sources_folder, "source", title=title, id=id_source)
    logger.info("Created source %s ", item.absolute_url())

    source_data = soup_source.find(class_="node__content")
    case_studies_orig = soup_source.find(
        class_="field--name-field-nwrm-source-cs")

    # set case studies relation
    if case_studies_orig:
        case_studies = case_studies_orig.findAll(class_="field__item")

        for case_study in case_studies:
            # cs_title = case_study.find("a").text
            cs_id = case_study.find("a").attrs['href'].split("/")[-1]
            case_study_obj = get_object_by_id("case_study", cs_id)

            if not case_study_obj:
                continue

            relapi.link_objects(
                item, case_study_obj, 'source_case_studies')

        case_studies_orig.decompose()

    item.source_data = t2r(source_data)

    # item.reindexObject()

    return item


def create_case_study(url_case_study, parent, sources_folder):
    try:
        time.sleep(0.2)
        url_normalizer = queryUtility(IURLNormalizer)

        page_case_study = requests.get(url_case_study)
        soup_case_study = BeautifulSoup(
            page_case_study.content, "html.parser")

        title = soup_case_study.find(class_="field--name-title").text
        id_case_study = url_normalizer.normalize(url_case_study.split("/")[-1])
        item = create_content(parent, "case_study",
                              title=title, id=id_case_study)
        logger.info("Created case study %s ", item.absolute_url())

        general = get_section_by_id(
            soup_case_study, 'edit-group-general')
        site_info = get_section_by_id(
            soup_case_study, 'edit-group-site-information')
        monitoring_maintenance = get_section_by_id(
            soup_case_study, 'edit-group-monitoring-maintenance')
        performance = get_section_by_id(
            soup_case_study, 'edit-group-performance')
        design_implementations = get_section_by_id(
            soup_case_study, 'edit-group-design-implementations')
        lessons_risks = get_section_by_id(
            soup_case_study, 'edit-group-lessons-risks-implications')
        policy_general_gov = get_section_by_id(
            soup_case_study, 'edit-group-policy-general-governance-')
        socio_economic = get_section_by_id(
            soup_case_study, 'edit-group-socio-economic')
        biophysical_impacts = get_section_by_id(
            soup_case_study, 'edit-group-biophysical-impacts')

        # get in-depth description and save the file
        file_soup = general.find(class_="field--name-field-nwrm-cs-file")
        
        if file_soup:
            filename = file_soup.find('a').text
            file_url = NWRM_BASE_URL + file_soup.find('a').attrs['href']
            file_content = requests.get(file_url).content
            file_soup.decompose()

            file_desc = create_content(
                item, "File", title=filename)
            file_desc.file = NamedBlobFile(
                data=file_content, filename=filename)

        # create source(s) relation
        sources_orig = general.find(
            class_="field--name-field-nwrm-cs-sources")
        if sources_orig:
            sources = sources_orig.findAll(class_="field__item")

            for source in sources:
                # source_title = source.find("a").text
                source_id = source.find("a").attrs['href'].split("/")[-1]
                source_obj = get_object_by_id("source", source_id)
                source_url = NWRM_BASE_URL + source.find("a").attrs['href']

                if not source_obj:
                    source_obj = create_source(source_url, sources_folder)

                relapi.link_objects(
                    item, source_obj, 'sources')

            sources_orig.decompose()

        # create measure relation
        measures_orig = general.find(
            class_="field--name-field-nwrm-cs-nwrms")
        if measures_orig:
            measures = measures_orig.findAll(class_="field__item")

            for measure in measures:
                # measure_title = measure.find("a").text
                measure_id = measure.find("a").attrs['href'].split("/")[-1]
                measure_obj = get_object_by_id("measure", measure_id)

                if not measure_obj:
                    continue

                relapi.link_objects(
                    item, measure_obj, 'measures')

            measures_orig.decompose()

        # set attributes
        item.general = t2r(general)
        item.site_information = t2r(site_info)
        item.monitoring_maintenance = t2r(monitoring_maintenance)
        item.performance = t2r(performance)
        item.design_and_implementations = t2r(design_implementations)
        item.lessons_risks_implications = t2r(lessons_risks)
        item.policy_general_governance = t2r(policy_general_gov)
        item.socio_economic = t2r(socio_economic)
        item.biophysical_impacts = t2r(biophysical_impacts)
    except:
        print(traceback.format_exc())

    # item.reindexObject()

    return item


class SetupCaseStudies(BrowserView):
    """ Crawler to get the case studies from the nwrm site
    """

    def __call__(self):
        parent = self.context
        case_studies_url = "http://nwrm.eu/list-of-all-case-studies"
        base_page = requests.get(case_studies_url)
        base_soup = BeautifulSoup(base_page.content, "html.parser")
        case_studies = base_soup.find_all("td", class_="views-field-title")

        for index, case_study in enumerate(case_studies):
            time.sleep(0.5)

            anchor = case_study.find("a")

            if not anchor:
                continue

            url_case_study = NWRM_BASE_URL + anchor.attrs["href"]
            logger.info("Setup case study %s of %s %s ",
                        index+1, len(case_studies), url_case_study)

            create_case_study(url_case_study, parent)

        alsoProvides(self.request, IDisableCSRFProtection)

        return "Setup completed!"


class SetupMeasuresCatalogue(BrowserView):
    """ Crawler to get the measures from the nwrm site
    """

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
        url_normalizer = queryUtility(IURLNormalizer)
        measures_url = "http://nwrm.eu/measures-catalogue"
        base_page = requests.get(measures_url)
        base_soup = BeautifulSoup(base_page.content, "html.parser")
        measures = base_soup.find_all("td", class_="views-field-title")
        measure_folder = create_content(
            self.context, "Document", title='Measures')
        case_study_folder = create_content(
            self.context, "Document", title='Case studies')
        sources_folder = create_content(
            self.context, "Document", title='Sources')

        for index, measure in enumerate(measures[:1]):
            try:
                time.sleep(0.2)

                anchor = measure.find("a")

                if not anchor:
                    continue

                url_measure = NWRM_BASE_URL + anchor.attrs["href"]
                if "index.php" in url_measure:
                    url_measure = url_measure.replace("index.php/", "")

                page_measure = requests.get(url_measure)
                soup_measure = BeautifulSoup(
                    page_measure.content, "html.parser")

                logger.info("Create measure %s of %s %s ",
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

                id_measure = url_normalizer.normalize(
                    url_measure.split("/")[-1])
                item = create_content(
                    measure_folder, "measure", title=title, id=id_measure)

                # set object attribute other fields
                item.measure_code = code
                item.measure_sector = sector
                item.other_sector = other_sector
                item.measure_summary = t2r(summary)
                item.possible_benefits = t2r(possible_benefits)

                # complete description PDF file
                complete_description = soup_measure.find(
                    class_="field--name-field-nwrm-nwrm-file").find(
                        class_="field__item")
                complete_descr_url = NWRM_BASE_URL + \
                    complete_description.find('a').attrs['href']
                complete_descr_file = requests.get(complete_descr_url).content
                complete_descr_filename = complete_description.find('a').text

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
                        # cs_title = case_study.find("a").text
                        cs_id = case_study.find(
                            "a").attrs['href'].split("/")[-1]
                        case_study_obj = get_object_by_id(
                            "case_study", cs_id)

                        if not case_study_obj:
                            case_study_url = NWRM_BASE_URL + \
                                case_study.find("a").attrs['href']
                            case_study_obj = create_case_study(
                                case_study_url, 
                                case_study_folder, 
                                sources_folder)

                        relapi.link_objects(
                            item, case_study_obj, 'case_studies')

                # item.reindexObject()

            except Exception as e:
                print(traceback.format_exc())
                # import pdb; pdb.set_trace()
                # continue

        alsoProvides(self.request, IDisableCSRFProtection)

        return "Setup completed!"
