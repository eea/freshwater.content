"""Module where all interfaces, events and exceptions live."""

from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope.interface import provider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
                         TextLine, Tuple)


class IFreshwaterContentLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


# @provider(IFormFieldProvider)
# class IExternalLinks(model.Schema):
#     """External links interface with RichText schema"""
#
#     external_links = RichText(title=u"External Links", description=u"", required=False)


@provider(IFormFieldProvider)
class ICatalogueMetadata(model.Schema):
    """Wise catalogue metadata

    Title   text    y
    Short description   Text    y
    Organisation name   from a list y
    Organization acronym    from the list   y
    Organization Logo   image (to be provided by Silvia)    y
    Organisation webpage    From the list   y
    Thumbnail   image   n   usefull for cards setting
    Type (DPSR) from the list   n
    Theme   from the list   n
    Subtheme    from the list   n
    keywords    text    n
    Date of Publication date (at least year)    y
    Last modified in WISE Marine    automatic from plone
    Link        y   the link can be internal or external links (more external, including EEA
    website and SDI catalogue
    """

    original_source = TextLine(
        title=u"Original source",
        description=u"If EEA link, can trigger automatic fetching of EEA information",
    )

    organisation = Choice(
        title=u"Organisation",
        required=True,
        vocabulary="wise_organisations_vocabulary",
        default="EEA",
    )

    dpsir_type = Choice(
        title=u"DPSIR", required=False, vocabulary="wise_dpsir_vocabulary"
    )

    theme = Choice(title=u"Theme", required=False, vocabulary="wise_themes_vocabulary")

    subtheme = Choice(
        title=u"Subtheme", required=False, vocabulary="wise_subthemes_vocabulary"
    )

    publication_year = Int(title=u"Publication year", required=True)

    thumbnail = NamedBlobImage(
        title=u"Preview image (thumbnail)",
        required=False,
    )

    sources = RichText(title=u"Sources", description=u"", required=False)
