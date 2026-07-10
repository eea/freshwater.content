"""Base64 field serializers for collective.exportimport.

Why this exists
---------------
collective.exportimport exports images as base64 by marking the request with
``IBase64BlobsMarker`` and relying on an adapter registered for
``(INamedImageField, IDexterityContent, IBase64BlobsMarker)``.

``eea.volto.policy`` registers a *dedicated* image serializer for
``(INamedImageField, IDexterityContent, IEeaVoltoPolicyLayer)`` which subclasses
plone.restapi's ``ImageFieldSerializer`` (the one that produces
download/scales/size instead of base64 ``data``).

During export the request provides both ``IBase64BlobsMarker`` and
``IEeaVoltoPolicyLayer``. The two adapters tie on the field
(``INamedImageField``) and context (``IDexterityContent``) axes, and the tie is
broken by registration order: eea.volto.policy loads after
collective.exportimport, so EEA wins and the image is exported as download URLs
instead of base64.

Fix: register base64 serializers for the *more specific* field interfaces
(``INamedBlobImageField`` / ``INamedBlobFileField``). A more specific field
interface outranks any adapter registered for the base ``INamedImageField`` /
``INamedFileField`` on the field axis, so these win adapter lookup during base64
export regardless of browser layer or load order.

The non-blob ``INamedImageField`` case (e.g. plone.leadimage ``NamedImage``) is
covered by re-registering for ``INamedImageField`` + ``IBase64BlobsMarker`` here;
since freshwater.content loads after both collective.exportimport and
eea.volto.policy, it wins that tie too.
"""

from collective.exportimport.interfaces import IBase64BlobsMarker
from collective.exportimport.serializer import FileFieldSerializerWithBlobs
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.interfaces import INamedBlobFileField
from plone.namedfile.interfaces import INamedBlobImageField
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImageField
from plone.restapi.interfaces import IFieldSerializer
from zope.component import adapter
from zope.interface import implementer


# Blob image (plone.app.contenttypes Image, NamedBlobImage behaviors) -- the
# common case. Wins outright on field specificity.
@adapter(INamedBlobImageField, IDexterityContent, IBase64BlobsMarker)
@implementer(IFieldSerializer)
class BlobImageFieldSerializerBase64(FileFieldSerializerWithBlobs):
    """Export blob image fields as base64 during collective.exportimport export."""


# Blob file (plone.app.contenttypes File). Defensive: collective.exportimport
# already wins this, but pin it explicitly so future EEA adapters can't regress.
@adapter(INamedBlobFileField, IDexterityContent, IBase64BlobsMarker)
@implementer(IFieldSerializer)
class BlobFileFieldSerializerBase64(FileFieldSerializerWithBlobs):
    """Export blob file fields as base64 during collective.exportimport export."""


# Non-blob image (NamedImage, e.g. plone.leadimage). Same registration triple as
# collective.exportimport's stock adapter; wins the tie because this package
# loads last.
@adapter(INamedImageField, IDexterityContent, IBase64BlobsMarker)
@implementer(IFieldSerializer)
class NamedImageFieldSerializerBase64(FileFieldSerializerWithBlobs):
    """Export non-blob image fields as base64 during collective.exportimport export."""


# Non-blob file (NamedFile). Same reasoning as the non-blob image above.
@adapter(INamedFileField, IDexterityContent, IBase64BlobsMarker)
@implementer(IFieldSerializer)
class NamedFileFieldSerializerBase64(FileFieldSerializerWithBlobs):
    """Export non-blob file fields as base64 during collective.exportimport export."""
