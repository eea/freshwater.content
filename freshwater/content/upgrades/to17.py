''' Upgrade to 17 '''

from uuid import uuid4
from plone import api
from plone.api import portal

# pylint: disable = C0412
import transaction
from zope.component import getUtility
from zc.relation.interfaces import ICatalog
from zope.intid.interfaces import IIntIds


def make_uid():
    """Block id"""
    return str(uuid4())


def html_to_text(html):
    """Convert html to text"""
    portal_transform = portal.get_tool(name="portal_transforms")

    data = portal_transform.convertTo("text/plain", html, mimetype="text/html")

    data = data.getData().strip()

    return data


def migrate_content_to_metadata_blocks(item):
    """Migrate content to metadata blocks"""
    blocks = item.blocks
    blocks_layout = item.blocks_layout["items"]
    first_group_block_id = blocks_layout[1]
    second_group_block_id = blocks_layout[2]

    # add description
    first_group_block = blocks[first_group_block_id]
    desc_block_id = first_group_block["data"]["blocks_layout"]["items"][0]
    item.blocks[first_group_block_id]["data"]["blocks"][desc_block_id] = {
        "@type": "slate",
        "plaintext": item.description,
        "value": [{
            "children": [{
                "text": item.description
            }],
            "type": "callout"
        }],
    }

    # add metadata values in tabs block
    second_group_block = blocks[second_group_block_id]
    tabs_block_id = second_group_block["data"]["blocks_layout"]["items"][0]
    tabs_block = second_group_block["data"]["blocks"][tabs_block_id]
    tabs_blocks_layout = tabs_block["data"]["blocks_layout"]["items"]

    notes_tab_id = tabs_blocks_layout[0]
    sources_tab_id = tabs_blocks_layout[1]
    metadata_tab_id = tabs_blocks_layout[2]
    more_info_tab_id = tabs_blocks_layout[3]

    second_block = item.blocks[second_group_block_id]
    item_tabs_block = second_block["data"]["blocks"][tabs_block_id]
    item_tabs = item_tabs_block["data"]["blocks"]

    notes_tab = tabs_block["data"]["blocks"][notes_tab_id]
    notes_tab_meta_id = notes_tab["blocks_layout"]["items"][0]
    item_tabs[notes_tab_id]["blocks"][notes_tab_meta_id] = {
        "@type": "metadataSection",
        "variation": "default",
        "fields": [
            {
                "@id": make_uid(),
                "field": {
                    "id": "lineage",
                    "title": "Notes",
                    "widget": "textarea"
                },
            }
        ],
    }

    sources_tab = tabs_block["data"]["blocks"][sources_tab_id]
    sources_tab_meta_id = sources_tab["blocks_layout"]["items"][0]
    item_tabs[sources_tab_id]["blocks"][sources_tab_meta_id] = {
        "@type": "metadataSection",
        "variation": "default",
        "fields": [
            {
                "@id": make_uid(),
                "field": {
                    "id": "data_provenance",
                    "title": "Add sources for the data used",
                    "widget": "data_provenance",
                },
            }
        ],
    }

    more_info_tab = tabs_block["data"]["blocks"][more_info_tab_id]
    more_info_tab_meta_id = more_info_tab["blocks_layout"]["items"][0]
    item_tabs[more_info_tab_id]["blocks"][more_info_tab_meta_id] = {
        "@type": "metadataSection",
        "variation": "default",
        "fields": [
            {
                "@id": make_uid(),
                "field": {
                    "id": "embed_url",
                    "title": "Tableau URL",
                    "widget": "string",
                },
                "showLabel": True,
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "dpsir_type",
                    "title":
                    "DPSIR",
                    "widget": "choices"
                },
                "showLabel": True,
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "legislative_reference",
                    "title": "Legislative reference",
                    "widget": "array",
                },
                "showLabel": True,
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "category",
                    "title": "Sub-Theme",
                    "widget": "array"
                    },
                "showLabel": True,
            },
        ],
    }

    meta_tab = tabs_block["data"]["blocks"][metadata_tab_id]
    meta_tab_metadata_id = meta_tab["blocks_layout"]["items"][0]
    item_tabs[metadata_tab_id]["blocks"][meta_tab_metadata_id] = {
        "@type": "metadataSection",
        "variation": "default",
        "fields": [
            {
                "@id": make_uid(),
                "field": {
                    "id": "topics",
                    "title": "Topics",
                    "widget": "array"
                },
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "geo_coverage",
                    "title": "Geographical coverage",
                    "widget": "geolocation",
                },
                "showLabel": True,
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "temporal_coverage",
                    "title": "Temporal coverage",
                    "widget": "temporal",
                },
                "showLabel": True,
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "publisher",
                    "title": "Publisher",
                    "widget": "array"
                },
                "showLabel": True,
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "rights",
                    "title": "Rights",
                    "widget": "textarea"
                },
                "showLabel": True,
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "other_organisations",
                    "title": "Other organisations involved",
                    "widget": "array",
                },
            },
        ],
    }


def run_upgrade(setup_context):
    """Run upgrade to 17
    Migrate Dashboard content type to Tableau visualization
    """

    catalog = api.portal.get_tool("portal_catalog")
    brains = catalog.searchResults(portal_type="dashboard")

    for brain in brains:
        obj = brain.getObject()
        embed_url = obj.embed_url

        if embed_url is not None and "://tableau" in embed_url:
            parent = obj.aq_parent
            eea_license = (
                "EEA standard re-use policy: unless otherwise indicated, " +
                "re-use of content on the EEA website for commercial or " +
                "non-commercial purposes is permitted free of charge, " +
                "provided that the source is acknowledged " +
                "(https://www.eea.europa.eu/legal/copyright)"
            )
            tableau_url = embed_url.replace(
                "://tableau.discomap", "://tableau-public.discomap"
            )
            tableau_url = tableau_url.replace("/t/Wateronline", "")
            tableau_url = tableau_url.split("?")[0]

            title = obj.title
            description = obj.description
            lineage = obj.lineage
            original_source = obj.original_source
            legislative_reference = obj.legislative_reference
            dpsir_type = obj.dpsir_type
            category = obj.category
            license_copyright = obj.license_copyright
            temporal_coverage = obj.temporal_coverage
            geo_coverage = obj.geo_coverage
            contributors = obj.Contributors()
            effective_date = obj.EffectiveDate()
            creation_date = obj.CreationDate()
            related_items = obj.relatedItems
            tags = obj.Subject()
            image = obj.image
            image_caption = obj.image_caption
            language = obj.language
            creators = obj.listCreators()

            intids = getUtility(IIntIds)
            obj_id = intids.getId(obj)
            relation_catalog = getUtility(ICatalog)
            rels = relation_catalog.findRelations({"to_id": obj_id})
            for rel in list(rels):
                relation_catalog.unindex(rel)

            try:
                api.content.delete(obj=obj)
            except Exception:
                print("Could not remove item", obj.absolute_url())

            item = api.content.create(
                type="visualization_tableau",
                title=title,
                safe_id=True,
                id=obj.id,
                container=parent,
            )

            item.description = description
            item.setCreators(creators)
            item.relatedItems = related_items
            item.contributors = contributors
            item.creation_date = creation_date
            item.preview_image = image
            item.preview_caption = image_caption
            item.language = language
            item.subject = tags
            item.lineage = lineage
            item.embed_url = tableau_url
            item.legislative_reference = legislative_reference
            item.dpsir_type = dpsir_type
            item.category = category
            item.temporal_coverage = temporal_coverage
            item.geo_coverage = geo_coverage
            item.publisher = ("EEA",)
            item.tableau_visualization = {"url": tableau_url}

            if obj.data_source_info is not None:
                data_source_info = html_to_text(obj.data_source_info.output)
            else:
                data_source_info = ""

            if effective_date != "None":
                item.effective_date = effective_date

            if license_copyright == "EEA":
                item.rights = eea_license
            else:
                item.rights = license_copyright

            if original_source is not None or data_source_info:
                sources = []
                if original_source:
                    data = {
                        "@id": make_uid(),
                        "link": original_source,
                        "organisation": "",
                        "title": "",
                    }
                    sources.append(data)

                if data_source_info:
                    data = {
                        "@id": make_uid(),
                        "link": data_source_info,
                        "organisation": "",
                        "title": "",
                    }
                    sources.append(data)

                item.data_provenance = {"data": sources}

            migrate_content_to_metadata_blocks(item)

            obj_state = api.content.get_state(obj=obj)
            if obj_state == "published":
                api.content.transition(obj=item, transition="publish")
            transaction.commit()
