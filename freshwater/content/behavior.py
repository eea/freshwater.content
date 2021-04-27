from plone.app.dexterity.behaviors.metadata import (DCFieldProperty,
                                                    MetadataBase)

from .interfaces import ICatalogueMetadata  #, IExternalLinks


class CatalogueMetadata(MetadataBase):
    """Wise metadata"""

    original_source = DCFieldProperty(ICatalogueMetadata["original_source"])
    organisation = DCFieldProperty(ICatalogueMetadata["organisation"])
    dpsir_type = DCFieldProperty(ICatalogueMetadata["dpsir_type"])
    theme = DCFieldProperty(ICatalogueMetadata["theme"])
    subtheme = DCFieldProperty(ICatalogueMetadata["subtheme"])
    publication_year = DCFieldProperty(ICatalogueMetadata["publication_year"])
    thumbnail = DCFieldProperty(ICatalogueMetadata["thumbnail"])

    sources = DCFieldProperty(ICatalogueMetadata["sources"])
