''' Upgrade to 20 '''

from plone import api
from plone.app.textfield.value import RichTextValue
from bs4 import BeautifulSoup
# pylint: disable = C0412


def run_upgrade(context):
    """Run upgrade to 20
    Upgrade step on Measures content types to fix following fields
    ecosystem_services, biophysical_impacts, policy_objectives
    """

    catalog = api.portal.get_tool("portal_catalog")
    brains = catalog.unrestrictedSearchResults(
        portal_type="measure"
    )

    for brain in brains:
        obj = brain.getObject()
        # migrate measure_summary
        soup_summary = BeautifulSoup(obj.measure_summary.output, "html.parser")

        if soup_summary.findChild().name == 'div':
            childs = soup_summary.findChild().findChildren()
            text = "".join(str(c) for c in childs)
            rich_text_value = RichTextValue(
                text or '', 'text/html', 'text/html')
            obj.measure_summary = rich_text_value

        fields = ['ecosystem_services',
                  'biophysical_impacts', 'policy_objectives']
        for field_name in fields:
            field_data = getattr(obj, field_name, [])

            if not field_data:
                continue

            # skip because migration was already done
            if "value" in field_data:
                continue

            items = getattr(obj, field_name)

            for item in items:
                item["name"] = "{} - {}".format(item['code'], item['name'])

            setattr(
                obj, field_name, {"value": list(getattr(obj, field_name, []))})

        obj.reindexObject()
