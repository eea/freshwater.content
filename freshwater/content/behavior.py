""" behavior.py """

from plone.app.dexterity.behaviors.metadata import DCFieldProperty, MetadataBase

from .interfaces import (
    ICatalogueMetadata,
    IWiseMetadata,
    IReportDataTypes,
)  # , IExternalLinks


class CatalogueMetadata(MetadataBase):
    """Freshwater metadata"""

    title = DCFieldProperty(ICatalogueMetadata["title"])
    description = DCFieldProperty(ICatalogueMetadata["description"])
    lineage = DCFieldProperty(ICatalogueMetadata["lineage"])
    original_source = DCFieldProperty(ICatalogueMetadata["original_source"])
    embed_url = DCFieldProperty(ICatalogueMetadata["embed_url"])
    webmap_url = DCFieldProperty(ICatalogueMetadata["webmap_url"])
    publisher = DCFieldProperty(ICatalogueMetadata["publisher"])
    legislative_reference = DCFieldProperty(ICatalogueMetadata["legislative_reference"])
    dpsir_type = DCFieldProperty(ICatalogueMetadata["dpsir_type"])
    category = DCFieldProperty(ICatalogueMetadata["category"])
    publication_year = DCFieldProperty(ICatalogueMetadata["publication_year"])
    license_copyright = DCFieldProperty(ICatalogueMetadata["license_copyright"])
    temporal_coverage = DCFieldProperty(ICatalogueMetadata["temporal_coverage"])
    geo_coverage = DCFieldProperty(ICatalogueMetadata["geo_coverage"])
    external_links = DCFieldProperty(ICatalogueMetadata["external_links"])
    data_source_info = DCFieldProperty(ICatalogueMetadata["data_source_info"])
    # tags = DCFieldProperty(ICatalogueMetadata["tags"])
    # thumbnail = DCFieldProperty(ICatalogueMetadata["thumbnail"])


class ReportDataTypes(MetadataBase):
    """Freshwater Report data types"""

    report_type = DCFieldProperty(IReportDataTypes["report_type"])


class WiseMetadata(MetadataBase):
    """WISE metadata"""

    # embed_url = DCFieldProperty(ICatalogueMetadata["embed_url"])
    lineage = DCFieldProperty(IWiseMetadata["lineage"])
    legislative_reference = DCFieldProperty(IWiseMetadata["legislative_reference"])
    dpsir_type = DCFieldProperty(IWiseMetadata["dpsir_type"])
    category = DCFieldProperty(IWiseMetadata["category"])
