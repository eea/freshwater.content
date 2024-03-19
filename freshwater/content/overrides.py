""" overrides.py """

import logging
import requests

from Acquisition import aq_base
from Acquisition import aq_inner
from plone import api
from plone.app.layout.navigation.root import getNavigationRoot
from plone.registry.interfaces import IRegistry
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.defaultpage import check_default_page_via_view
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer

from mo_sql_parsing import format as sql_format
from eea.api.dataconnector.queryparser import parseQuery
from eea.api.dataconnector.queryfilter import filteredData

from eea.volto.policy.image_scales.interfaces import IImagingSchema

logger = logging.getLogger(__name__)


def _split_scale_info(allowed_size):
    """
    get desired attr(name,width,height) from scale names
    """
    name, dims = allowed_size.split(" ")
    width, height = list(map(int, dims.split(":")))
    return name, width, height


def _get_scale_infos():
    """Returns list of (name, width, height) of the available image scales."""
    if IImagingSchema is None:
        return []
    registry = getUtility(IRegistry)
    imaging_settings = registry.forInterface(
        IImagingSchema, prefix="plone", omit=("picture_variants")
    )
    allowed_sizes = imaging_settings.allowed_sizes
    return [_split_scale_info(size) for size in allowed_sizes]


def get_scales(self, field, width, height):
    """Get a dictionary of available scales for a particular image field,
    with the actual dimensions (aspect ratio of the original image).
    """
    scales = {}

    for name, actual_width, actual_height in _get_scale_infos():
        if actual_width > width:
            # The width of the scale is larger than the original width.
            # Scaling would simply return the original (or perhaps a copy
            # with the same size).  We do not need this scale.
            # If we *do* want this, we should call the scale method with
            # mode="cover", so it scales up.
            continue

            # Get the scale info without actually generating the scale,
            # nor any old-style HiDPI scales.

        try:
            scale = self.images_view.scale(
                field.__name__,
                width=actual_width,
                height=actual_height,
            )
        except Exception:
            scale = None

        if scale is None:
            # If we cannot get a scale, it is probably a corrupt image.
            continue

        url = scale.url
        actual_width = scale.width
        actual_height = scale.height

        scales[name] = {
            "download": self._scale_view_from_url(url),
            "width": actual_width,
            "height": actual_height,
        }

    return scales


def _get_data(self):
    """_get_data."""
    data = {}
    metadata = self._get_metadata()
    sql = parseQuery(self.context, self.request)

    if not sql:
        return {"results": [], "metadata": metadata}

    conditions = sql.get("conditions")
    data_query = sql.get("data_query")
    form = sql.get("form")
    query = sql.get("query")

    if "where" in query and conditions:
        query["where"] = {"and": conditions + [query["where"]]}
    elif "where" not in query and len(conditions) > 1:
        query["where"] = {"and": conditions}
    elif len(conditions) == 1:
        query["where"] = conditions[0]

    try:
        data["query"] = sql_format(query)
    except Exception:
        # parsing sql query with PIVOT keyword gives an error
        data["query"] = self.context.sql_query

    if form.get("p"):
        data["p"] = form.get("p")

    if form.get("nrOfHits"):
        data["nrOfHits"] = form.get("nrOfHits")

    try:
        req = requests.post(self.context.endpoint_url, data)
        data = req.json()
    except Exception:
        logger.exception("Error in requestion data")
        data = {"results": [], "metadata": metadata}

    if "errors" in data:
        return {"results": [], "metadata": metadata}

    # This will also change orientation
    return {
        "results": filteredData(data["results"], data_query),
        "metadata": metadata,
    }


def get_url(item):
    """get_url"""
    if not item:
        return None
    if hasattr(aq_base(item), 'getURL'):
        # Looks like a brain
        return item.getURL()
    return item.absolute_url()


def get_id(item):
    """get_id"""
    if not item:
        return None
    getId = getattr(item, 'getId')
    if not utils.safe_callable(getId):
        # Looks like a brain
        return getId
    return getId()


def get_view_url(context):
    """get_view_url"""
    registry = getUtility(IRegistry)
    view_action_types = registry.get(
        'plone.types_use_view_action_in_listings', [])
    item_url = get_url(context)
    name = get_id(context)

    if item_url and getattr(context, 'portal_type', {}) in view_action_types:
        item_url += '/view'
        name += '/view'

    return name, item_url


@implementer(INavigationBreadcrumbs)
class PhysicalNavigationBreadcrumbs(BrowserView):
    """PhysicalNavigationBreadcrumbs"""

    def breadcrumbs(self):
        """breadcrumbs"""
        context = aq_inner(self.context)
        request = self.request
        container = utils.parent(context)

        _, item_url = get_view_url(context)
        state = api.content.get_state(self.context, default='')

        if container is None:
            return ({
                'absolute_url': item_url,
                'Title': utils.pretty_title_or_id(context, context),
                'review_state': state
            },)

        view = getMultiAdapter((container, request), name='breadcrumbs_view')
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        rootPath = getNavigationRoot(context)
        itemPath = '/'.join(context.getPhysicalPath())

        # don't show default pages in breadcrumbs or pages above the navigation
        # root

        if not check_default_page_via_view(context, request) \
           and not rootPath.startswith(itemPath):
            base += ({
                'absolute_url': item_url,
                'Title': utils.pretty_title_or_id(context, context),
                'review_state': state
            },)
        return base
