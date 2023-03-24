""" utils """

from plone.app.textfield.value import RichTextValue
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView

from zope.interface import alsoProvides


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
