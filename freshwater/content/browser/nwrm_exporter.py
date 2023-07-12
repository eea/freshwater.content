""" export case studies and measures to xls """

from io import BytesIO
from collections import defaultdict

import json

import lxml
import xlsxwriter

from Products.Five.browser import BrowserView
from plone import api


def css_select_one(node, selector):
    """ cssselect to return only one result """

    value = node.cssselect(selector)

    if value:
        return value[0].text

    return ""


class ExportMeasuresXls(BrowserView):
    """ Export measures as excel """

    def __call__(self):
        portal_catalog = api.portal.get_tool("portal_catalog")
        results = portal_catalog.searchResults(portal_type='measure')
        measures = [x.getObject() for x in results]

        data = []
        for measure in measures:
            row_data = {}
            row_data['title'] = measure.title
            row_data['url'] = "{}/{}".format(
                "https://wise-test.eionet.europa.eu/freshwater"
                "/nwrm-imported/nwrm-measures-catalogue",
                measure.getPhysicalPath()[-1])

            row_data['code'] = measure.measure_code
            row_data['sector'] = measure.measure_sector
            row_data['other_sector'] = measure.other_sector
            row_data['measure_summary'] = measure.measure_summary.raw
            row_data['biophysical_impacts'] = measure._nwrm_biophysical_impacts
            row_data['ecosystem_services'] = measure._nwrm_ecosystem_services
            row_data['policy_objectives'] = measure._nwrm_policy_objectives

            data.append(row_data)

        headers = ['title', 'url', 'code', 'sector', 'other_sector',
                   'biophysical_impacts', 'ecosystem_services',
                   'policy_objectives']

        # Create a workbook and add a worksheet.
        out = BytesIO()
        workbook = xlsxwriter.Workbook(out, {'in_memory': True})

        wtitle = 'Measures'
        worksheet = workbook.add_worksheet(wtitle[:30])

        for i, title in enumerate(headers):
            worksheet.write(0, i, title or '')

        row_index = 1

        for row in data:
            for index, header in enumerate(headers):
                worksheet.write(row_index, index, str(row.get(header, '')))

            row_index += 1

        # worksheet benefits
        headers_benefits = ['title', 'url', 'code', 'name', 'level', 'type']
        wtitle_benefits = 'Benefits'
        worksheet_b = workbook.add_worksheet(wtitle_benefits[:30])

        for i, title in enumerate(headers_benefits):
            worksheet_b.write(0, i, title or '')

        benefits_categories = ['biophysical_impacts', 'ecosystem_services',
                               'policy_objectives']

        row_index = 1
        for row in data:
            for category in benefits_categories:
                cat_values = row[category]

                for item in cat_values:
                    code, name, level = item
                    worksheet_b.write(row_index, 0, str(row.get('title', '')))
                    worksheet_b.write(row_index, 1, str(row.get('url', '')))
                    worksheet_b.write(row_index, 2, code)
                    worksheet_b.write(row_index, 3, name)
                    worksheet_b.write(row_index, 4, level)
                    worksheet_b.write(row_index, 5, category)

                    row_index += 1

        workbook.close()
        out.seek(0)

        xlsio = out
        sh = self.request.response.setHeader

        sh('Content-Type', 'application/vnd.openxmlformats-officedocument.'
           'spreadsheetml.sheet')
        fname = "-".join(["Measures"])
        sh('Content-Disposition',
           'attachment; filename=%s.xlsx' % fname)

        return xlsio.read()


class ExportCaseStudiesXls(BrowserView):
    """ Export measures as excel """

    attributes = ["general", "site_information", "monitoring_maintenance",
                  "performance", "design_and_implementations",
                  "lessons_risks_implications", "policy_general_governance",
                  "socio_economic", "biophysical_impacts"]

    def get_value(self, node):
        """ return a value for a field"""

        if node.cssselect('table'):
            result = []
            headers = [
                n.text
                for n in node.cssselect('table thead th em')]

            rows = node.cssselect('table tbody tr')

            for row in rows:
                tds = row.cssselect('td')
                values = []

                for td in tds:
                    div = td.cssselect('div')
                    v = div[0].text if div else ''
                    values.append(v)

                result.append(dict(zip(headers, values)))

            return json.dumps(result)

        if node.cssselect('div.field__item'):
            return css_select_one(node, 'div.field__item')

        return "!NOT IMPLEMENTED!"

    def __call__(self):
        portal_catalog = api.portal.get_tool("portal_catalog")
        results = portal_catalog.searchResults(portal_type='case_study')
        case_studies = [x.getObject() for x in results]

        data = []
        headers = defaultdict(list)

        for case_study in case_studies:
            row_data = {"Case study url": "{}/{}".format(
                "https://wise-test.eionet.europa.eu/freshwater"
                "/nwrm-imported/nwrm-case-studies",
                case_study.getPhysicalPath()[-1])}

            for attribute in self.attributes:
                section_value = getattr(case_study, attribute)
                section_raw = (
                    section_value.raw if hasattr(section_value, 'raw')
                    else section_value
                )

                if not section_raw:
                    continue

                field_node = lxml.etree.fromstring(section_raw)
                nodes = field_node.cssselect('div.field')

                for node in nodes:
                    label = css_select_one(node, 'div.field__label')
                    value = self.get_value(node)

                    if label not in headers[attribute]:
                        headers[attribute].append(label)

                    row_data[label] = value
                    # import pdb;pdb.set_trace()

            data.append(row_data)

        # Create a workbook and add a worksheet.
        out = BytesIO()
        workbook = xlsxwriter.Workbook(out, {'in_memory': True})
        wtitle = "Case studies"
        worksheet = workbook.add_worksheet(wtitle[:30])

        headers_unpacked = ['Case study url']

        for section in self.attributes:
            headers_unpacked.extend(headers[section])

        for i, title in enumerate(headers_unpacked):
            worksheet.write(0, i, title or '')

        row_index = 1

        for row in data:
            for index, header in enumerate(headers_unpacked):
                worksheet.write(row_index, index, row.get(header, ''))

            row_index += 1

        workbook.close()
        out.seek(0)

        xlsio = out
        sh = self.request.response.setHeader

        sh('Content-Type', 'application/vnd.openxmlformats-officedocument.'
           'spreadsheetml.sheet')
        sh('Content-Disposition', 'attachment; filename=CaseStudies.xlsx')

        return xlsio.read()
