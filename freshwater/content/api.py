from freshwater.content.interfaces import IFreshwaterContentLayer
from plone.restapi.interfaces import IExpandableElement
from collective.bookmarks.api.utils import bookmark_dict_to_json_dict
from collective.bookmarks.api.utils import get_bookmark_from_request
from collective.bookmarks.api.utils import get_owner
from collective.bookmarks.storage import Bookmarks
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service
from zope.interface import alsoProvides
from repoze.catalog.query import Eq, NotEq
from zExceptions import NotFound
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, IFreshwaterContentLayer)
class Breadcrumbs:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"breadcrumbs": {
            "@id": f"{self.context.absolute_url()}/@breadcrumbs"}}
        if not expand:
            return result

        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        breadcrumbs_view = getMultiAdapter(
            (self.context, self.request), name="breadcrumbs_view"
        )
        items = []
        for crumb in breadcrumbs_view.breadcrumbs():
            item = {
                "title": crumb["Title"],
                "@id": crumb["absolute_url"],
                "review_state": crumb.get('review_state')
            }
            if crumb.get("nav_title", False):
                item.update({"title": crumb["nav_title"]})

            items.append(item)

        result["breadcrumbs"]["items"] = items
        result["breadcrumbs"]["root"] = portal_state.navigation_root().absolute_url()
        return result


class BreadcrumbsGet(Service):
    def reply(self):
        breadcrumbs = Breadcrumbs(self.context, self.request)
        return breadcrumbs(expand=True)["breadcrumbs"]


class BookmarksAll(Bookmarks):
    def fetch_all(self, query):
        """fetch all bookmarks

        """
        res = []
        for lazy_record in self._soup.lazy(query):
            res.append(self._dictify(lazy_record()))

        return res


class BookmarksGet(Service):
    def reply(self):
        """get all bookmarks

        """

        bookmark = BookmarksAll()
        try:
            owner = get_owner(request=self.request)
        except:
            owner = '__anonym__'

        query_eq = Eq("owner", owner)
        query_noteq = NotEq("owner", owner)
        bookmarks_eq = bookmark.fetch_all(query_eq)
        bookmarks_noteq = bookmark.fetch_all(query_noteq)
        bookmarks = bookmarks_eq + bookmarks_noteq

        if bookmarks:
            return [bookmark_dict_to_json_dict(x) for x in bookmarks]

        raise NotFound("No such bookmark found.")


class BookmarkPut(Service):
    def reply(self):
        """update bookmark by

        uid
        owner
        group
        queryparams (optional): serialized querystring

        Add new bookmark if bookmark not found.
        """
        owner, uid, group, queryparams, payload = get_bookmark_from_request(
            self.request, loadjson=True
        )
        alsoProvides(self.request, IDisableCSRFProtection)
        # payload = self.request.form.get("payload", "{}")
        bookmarks = Bookmarks()
        bookmark = bookmarks.update(owner, uid, group, queryparams, payload)
        if not bookmark:
            # be kind
            bookmark = bookmarks.add(owner, uid, group, queryparams, payload)
        self.request.response.setStatus(201)
        return bookmark_dict_to_json_dict(bookmark)
