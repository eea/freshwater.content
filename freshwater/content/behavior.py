from plone.app.dexterity.behaviors.metadata import (DCFieldProperty,
                                                    MetadataBase)

from .interfaces import ICatalogueMetadata  #, IExternalLinks


class CatalogueMetadata(MetadataBase):
    """Freshwater metadata"""
    title = DCFieldProperty(ICatalogueMetadata["title"])
    description = DCFieldProperty(ICatalogueMetadata["description"])
    lineage = DCFieldProperty(ICatalogueMetadata["lineage"])
    original_source = DCFieldProperty(ICatalogueMetadata["original_source"])
    organisation = DCFieldProperty(ICatalogueMetadata["organisation"])
    dpsir_type = DCFieldProperty(ICatalogueMetadata["dpsir_type"])
    topic = DCFieldProperty(ICatalogueMetadata["topic"])
    tags = DCFieldProperty(ICatalogueMetadata["tags"])
    publication_year = DCFieldProperty(ICatalogueMetadata["publication_year"])
    temporal_coverage = DCFieldProperty(ICatalogueMetadata["temporal_coverage"])
    geo_coverage = DCFieldProperty(ICatalogueMetadata["geo_coverage"])
    data_source_info = DCFieldProperty(ICatalogueMetadata["data_source_info"])
    thumbnail = DCFieldProperty(ICatalogueMetadata["thumbnail"])
