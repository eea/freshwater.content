from collective.bookmarks.api.utils import bookmark_dict_to_json_dict
from collective.bookmarks.api.utils import get_owner
from collective.bookmarks.storage import Bookmarks
from plone.restapi.services import Service
from repoze.catalog.query import Eq, NotEq
from zExceptions import NotFound


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
        """get all bookmark

        """

        bookmark = BookmarksAll()
        owner = get_owner(request=self.request)
        query_eq = Eq("owner", owner)
        query_noteq = NotEq("owner", owner)
        bookmarks_eq = bookmark.fetch_all(query_eq)
        bookmarks_noteq = bookmark.fetch_all(query_noteq)
        bookmarks = bookmarks_eq + bookmarks_noteq

        if bookmarks:
            return [bookmark_dict_to_json_dict(x) for x in bookmarks]
        
        raise NotFound("No such bookmark found.")
