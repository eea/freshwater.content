""" utils """

from plone.app.textfield.value import RichTextValue
from Products.Five.browser import BrowserView

from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


def t2r(text):
    """ transform string to richtext """

    text = str(text) or ''

    if not text:
        return ''

    return RichTextValue(text or '', 'text/html', 'text/html')


class ToPDB(BrowserView):
    """ global view to enter in pdb """

    def __call__(self):
        import pdb
        pdb.set_trace()

        alsoProvides(self.request, IDisableCSRFProtection)
