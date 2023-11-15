''' Upgrade to 18 '''

import logging
from plone import api
from uuid import uuid4
# pylint: disable = C0412

logger = logging.getLogger('eea.restapi.migration')

def make_uid():
    return str(uuid4())

def get_block_id(blocks, type):
    block = {k for k, v in blocks.items() if v['title'] == type}
    if block:
        block_id = list(block)[0]
        return block_id
    else:
        return None
    
def update_blocks(obj):
    blocks = obj.blocks
    blocks_layout = obj.blocks_layout['items']
    second_group_block_id = blocks_layout[2]

    second_group_block = blocks[second_group_block_id]
    tabs_block_id = second_group_block['data']['blocks_layout']['items'][0]
    tabs_block = second_group_block['data']['blocks'][tabs_block_id]
    tabs_blocks_layout = tabs_block['data']['blocks_layout']['items']

    metadata_tab_id = get_block_id(tabs_block['data']['blocks'], 'Metadata')
    more_info_tab_id = get_block_id(tabs_block['data']['blocks'], 'More info')

    item_tabs_block = obj.blocks[second_group_block_id]['data']['blocks'][tabs_block_id]
    item_tabs = item_tabs_block['data']['blocks']

    if more_info_tab_id:
        more_info_tab = tabs_block['data']['blocks'][more_info_tab_id]
        more_info_tab_items = more_info_tab['blocks_layout']['items']
        more_info_tab_meta_id = more_info_tab_items[0]
        item_tabs[more_info_tab_id]['blocks'][more_info_tab_meta_id] = {
            '@type': 'metadataSection', 
            'variation': 'default',
            'fields': []
        }
        more_info_tab_index = tabs_blocks_layout.index(more_info_tab_id)
        tabs_blocks_layout.pop(more_info_tab_index)
        tabs_block['data']['blocks'].pop(more_info_tab_id)


    if metadata_tab_id:
        meta_tab = tabs_block['data']['blocks'][metadata_tab_id]
        meta_tab_metadata_id = meta_tab['blocks_layout']['items'][0]
        item_tabs[metadata_tab_id]['blocks'][meta_tab_metadata_id] = {
            '@type': 'metadataSection', 
            'variation': 'default',
            'fields':[
            {
                "@id": make_uid(),
                "field": {
                    "id": "topics",
                    "title": "Topics",
                    "widget": "array"
                },
                "showLabel": True,
                "hideInView": True
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "geo_coverage",
                    "title": "Geographical coverage",
                    "widget": "geolocation"
                },
                "showLabel": True
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "temporal_coverage",
                    "title": "Temporal coverage",
                    "widget": "temporal"
                },
                "showLabel": True
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "publisher",
                    "title": "Publisher",
                    "widget": "array"
                },
                "showLabel": True
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "rights",
                    "title": "Rights",
                    "widget": "textarea"
                },
                "showLabel": True
            },
            {
                "@id": make_uid(),
                "field": {
                    "id": "other_organisations",
                    "title": "Other organisations involved",
                    "widget": "array"
                },
                "showLabel": True,
                "hideInView": True
            },
            {
                "@id": make_uid(),
                "field": {
                "id": "dpsir_type",
                "title": "DPSIR",
                "widget": "choices"
                },
                "showLabel": True
            },
            {
                "@id": make_uid(),
                "field": {
                "id": "legislative_reference",
                "title": "Legislative reference",
                "widget": "array"
                },
                "showLabel": True
            },
            {
                "@id": make_uid(),
                "field": {
                "id": "category",
                "title": "Sub-Theme",
                "widget": "array"
                },
                "showLabel": True
            }]
        }

    def hide_in_view(type):
        metadata_fields = item_tabs[metadata_tab_id]['blocks'][meta_tab_metadata_id]['fields']
        field = [k for k in metadata_fields if k['field']['id'] == type]
        field[0]['hideInView'] = True
        
    if not obj.legislative_reference:
        hide_in_view("legislative_reference")
    
    if not obj.category:
        hide_in_view("category")
    
    if not obj.dpsir_type:
        hide_in_view("dpsir_type")



def run_upgrade(context):
    """ Run upgrade to 18
        Update blocks in Tableau visualization
    """

    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog.unrestrictedSearchResults(portal_type='visualization_tableau')

    for brain in brains:
        obj = brain.getObject()
        obj.tableau_visualization["hideToolbar"] = True
        obj.tableau_visualization["hideTabs"] = True

        if type(obj.legislative_reference) == str:
            obj.legislative_reference = tuple([obj.legislative_reference])

        if obj.lineage is None:
            obj.lineage = 'No data'
        
        if obj.rights is None or obj.rights == '':
            obj.rights = 'No data'

        update_blocks(obj)
        obj.reindexObject()
