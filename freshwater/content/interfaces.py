"""Module where all interfaces, events and exceptions live."""

from plone.app.dexterity import _
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import Choice, Int, Text, TextLine, Tuple

# from plone.app.z3cform.widget import AjaxSelectFieldWidget
# from plone.namedfile.field import NamedBlobImage
# from zope import schema


class IFreshwaterContentLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


@provider(IFormFieldProvider)
class ICatalogueMetadata(model.Schema):
    """Freshwater catalogue metadata

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
    Link        y   the link can be internal or external links
        (more external, including EEA website and SDI catalogue
    """

    # default fieldset
    title = TextLine(title=_(u"label_title", default=u"Title"), required=True)

    description = Text(
        title=_(u"label_description", default=u"Description"),
        description=_(
            u"help_description",
            default=u"Used in item listings and search results."
        ),
        required=True,
    )

    lineage = Text(
        title=u"Lineage",
        required=False,
    )

    original_source = TextLine(
        title=u"Original source",
        required=False,
        # description=u"If EEA link, can trigger "
        # u"automatic fetching of EEA information",
    )

    embed_url = TextLine(
        title=u"Tableau URL",
        required=False,
    )

    webmap_url = TextLine(
        title=u"Embed URL",
        description=u"Webmap URL",
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

    directives.widget("category", vocabulary="wise_category_vocabulary")
    category = Tuple(
        title=u"Topics",
        required=False,
        default=(),
        value_type=TextLine(
            title=u"Single topic",
        ))

    legislative_reference = Tuple(
        title="Legislative reference",
        required=False,
        value_type=Choice(
            title=u"Single legislative reference",
            vocabulary="wise_legislative_vocabulary",
        ))

    # subtheme = Choice(title=u"Subtheme", required=False,
    #                   vocabulary="wise_subthemes_vocabulary")

    # tags = Text(title=u"Tags", required=False)

    publication_year = Int(title=u"Publication year", required=True)

    license_copyright = TextLine(
        title=_(u"label_title", default=u"Rights"), required=False
    )

    temporal_coverage = JSONField(
        title=u"Temporal coverage",
        required=False, widget="temporal", default={}
    )

    geo_coverage = JSONField(
        title=u"Geographical coverage",
        required=False, widget="geolocation", default={}
    )

    data_source_info = RichText(
        title=u"Data source information",
        description=u"Rich text, double click for toolbar.",
        required=False,
    )

    external_links = RichText(
        title=u"External links",
        description=u"Rich text, double click for toolbar.",
        required=False,
    )

    # thumbnail = NamedBlobImage(
    #     title=u"Preview image (thumbnail)",
    #     required=False,
    # )


@ provider(IFormFieldProvider)
class IReportDataTypes(model.Schema):
    """Freshwater Report type"""

    report_type = Choice(
        title=u"Report type",
        required=False, vocabulary="wise_report_vocabulary"
    )


@provider(IFormFieldProvider)
class IWiseMetadata(model.Schema):
    """Wise catalogue metadata
    """

    model.fieldset(
        "wise_metadata",
        label=_("label_schema_default", default="WISE metadata"),
        fields=[
            "lineage",
            # "embed_url",
            "dpsir_type",
            "category",
            "legislative_reference",
        ],
    )

    # embed_url = TextLine(
    #     title=u"Tableau URL",
    #     required=False,
    # )

    lineage = Text(
        title=u"Notes",
        required=False,
    )

    dpsir_type = Choice(
        title=u"DPSIR", required=False, vocabulary="wise_dpsir_vocabulary"
    )

    directives.widget("category", vocabulary="wise_category_vocabulary")
    category = Tuple(
        title=u"Sub-Theme",
        required=False,
        default=(),
        value_type=TextLine(
            title=u"Single topic",
        ))

    directives.widget("legislative_reference",
                      vocabulary="wise_legislative_vocabulary")
    legislative_reference = Tuple(
        title="Legislative reference",
        required=False,
        default=(),
        missing_value=None,
        value_type=TextLine(
            title=u"Single topic",
        ))
