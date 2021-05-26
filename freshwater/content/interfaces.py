"""Module where all interfaces, events and exceptions live."""

from plone.app.dexterity import _
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
                         TextLine, Tuple)


class IFreshwaterContentLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


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

    # default fieldset
    title = TextLine(title=_(u"label_title", default=u"Title"), required=True)

    description = Text(
        title=_(u"label_description", default=u"Description"),
        description=_(
            u"help_description", default=u"Used in item listings and search results."
        ),
        required=True,
    )

    lineage = Text(
        title=u"Lineage",
        required=False,
    )

    original_source = TextLine(
        title=u"Original source",
        # description=u"If EEA link, can trigger "
        # u"automatic fetching of EEA information",
    )

    embed_url = TextLine(
        title=u"Embed URL",
        description=u"Tableau or webmap URL",
        required=False,
    )

    publisher = Choice(
        title=u"Organisation",
        description=u"The responsible organisation for this item",
        required=True,
        vocabulary="wise_organisations_vocabulary",
        default="EEA",
    )

    dpsir_type = Choice(
        title=u"DPSIR", required=False, vocabulary="wise_dpsir_vocabulary"
    )

    # theme = Choice(title=u"Theme", required=False,
    #                vocabulary="wise_themes_vocabulary")

    category = Text(title=u"Category", required=False)

    # subtheme = Choice(title=u"Subtheme", required=False,
    #                   vocabulary="wise_subthemes_vocabulary")

    tags = Text(title=u"Tags", required=False)

    publication_year = Int(title=u"Publication year", required=True)

    license_copyright = TextLine(title=_(u"label_title", default=u"Rights"), required=False)

    temporal_coverage = JSONField(
        title=u"Temporal coverage", required=False, widget="temporal", default={}
    )

    geo_coverage = JSONField(
        title=u"Geographical coverage", required=False, widget="geolocation", default={}
    )

    data_source_info = RichText(
        title=u"Data source information", description=u"", required=False
    )

    thumbnail = NamedBlobImage(
        title=u"Preview image (thumbnail)",
        required=False,
    )


@provider(IFormFieldProvider)
class IReportDataTypes(model.Schema):
    """Freshwater Report type
    """

    report_type = Choice(
        title=u"Report type",
        required=False,
        vocabulary="wise_report_vocabulary"
    )
