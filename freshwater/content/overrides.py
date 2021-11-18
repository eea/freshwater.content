from Acquisition import aq_base
from Acquisition import aq_inner
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

from plone import api


def get_url(item):
    if not item:
        return None
    if hasattr(aq_base(item), 'getURL'):
        # Looks like a brain
        return item.getURL()
    return item.absolute_url()


def get_id(item):
    if not item:
        return None
    getId = getattr(item, 'getId')
    if not utils.safe_callable(getId):
        # Looks like a brain
        return getId
    return getId()


def get_view_url(context):
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

    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        container = utils.parent(context)

        name, item_url = get_view_url(context)
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
