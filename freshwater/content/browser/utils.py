""" utils """

from plone import api
from plone.app.textfield.value import RichTextValue
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView

from zope.interface import alsoProvides

import transaction


def t2r(text, remove_last_column=False):
    """ transform string to richtext """

    if not text:
        return ''

    # remove empty tables
    if text.find('table'):
        items = text.findAll(class_="field__item")

        for item in items:
            table = item.find('table')

            if table and not table.find('tbody'):
                table.decompose()
                item.string = "No data"

    # remove last column from tables
    if remove_last_column and text.find('table'):
        tables = text.findAll("table")

        for table in tables:
            rows = table.findAll("tr")

            for row in rows:
                ths = row.findAll("th")

                if ths:
                    ths[-1].decompose()

                tds = row.findAll("td")

                if tds:
                    tds[-1].decompose()

    text = str(text) or ''

    return RichTextValue(text or '', 'text/html', 'text/html')


class ToPDB(BrowserView):
    """ global view to enter in pdb """

    def __call__(self):
        import pdb
        pdb.set_trace()

        alsoProvides(self.request, IDisableCSRFProtection)


class BrokenSlotsScanner(BrowserView):
    """BrokenSlotsScanner"""

    def __call__(self):
        ids_to_remove = ['uwwt', 'copy_of_uwwt']
        parent = self.context

        for obj_id in ids_to_remove:
            parent._delObject(obj_id, suppress_events=True)
            transaction.commit()

        return "removed ids: {}".format(ids_to_remove)


class FixPlone6ResourceDependency(BrowserView):
    """FixPlone6ResourceDependency"""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        registry = api.portal.get_tool('portal_registry')

        for key in list(registry.records.keys()):
            if 'imagecropping' in key:
                print("Deleting registry key: {}".format(key))
                del registry.records[key]

        portal_actions = api.portal.get_tool(name='portal_actions')
        for category in portal_actions.objectValues():
            for action in category.objectValues():
                available_expr = getattr(action, 'available_expr', '')

                if available_expr and 'imagecropping' in available_expr:
                    print(
                        "Removing condition from action: {}".format(action.id))
                    category.manage_delObjects([action.id])

        transaction.commit()

        return 'Done'
