""" to11.py """

import json
from collections import deque
import logging
from plone import api
from plone.restapi.deserializer.utils import path2uid


logger = logging.getLogger('freshwater.content.migration')


def clean_url(url):
    """clean_url"""
    if not url:
        return url

    hosts = [
        'http://localhost:8080',
        'http://backend:8080',
        'https://demo-freshwater.eea.europa.eu/api',
        'https://demo-freshwater.eea.europa.eu',
        'https://demo-freshwater.devel4cph.eea.europa.eu',
        'https://demo-freshwater.devel4cph.eea.europa.eu/api',
    ]
    for bit in hosts:
        url = url.replace(bit, '')
    return url


def iterate_children(value):
    """iterate_children.

    :param value:
    """
    queue = deque(value)

    while queue:
        child = queue.pop()
        yield child
        if child.get("children"):
            queue.extend(child["children"] or [])


def get_blocks(obj):
    """get_blocks"""
    blocks_layout = getattr(obj, 'blocks_layout', {})

    if isinstance(blocks_layout, str):
        blocks_layout = json.loads(blocks_layout)
        obj.blocks_layout = blocks_layout
        obj._p_changed = True
        logger.info('Converted str blocks_layout for % s',
                    obj.absolute_url())

    order = blocks_layout.get('items', [])

    blocks = getattr(obj, 'blocks', {})
    if isinstance(blocks, str):
        blocks = json.loads(blocks)
        obj.blocks = blocks
        obj._p_changed = True
        logger.info('Converted str blocks for % s',
                    obj.absolute_url())

    out = []
    for _id in order:
        if _id not in blocks:
            obj.blocks_layout['items'] = [b for b in order if b in blocks]
            obj._p_changed = True
            logger.info("Object with incomplete blocks %s", obj.absolute_url())
            continue
        out.append((_id, blocks[_id]))

    return out


class BlocksTraverser(object):
    """BlocksTraverser"""
    def __init__(self, context):
        self.context = context

    def __call__(self, visitor):

        for (_, block_value) in get_blocks(self.context):

            if visitor(block_value):
                self.context._p_changed = True

            self.handle_subblocks(block_value, visitor)

    def handle_subblocks(self, block_value, visitor):
        """handle_subblocks"""
        if "data" in block_value and isinstance(block_value["data"], dict) \
                and "blocks" in block_value["data"]:
            for block in block_value["data"]["blocks"].values():
                if visitor(block):
                    self.context._p_changed = True

                self.handle_subblocks(block, visitor)

        if "blocks" in block_value:
            for block in block_value['blocks'].values():
                if visitor(block):
                    self.context._p_changed = True

                self.handle_subblocks(block, visitor)

        # if block_value.get('@type') in image_card_types:
        #     visitor(block_value.get('cards', {}))


class ResolveUIDDeserializerBase(object):
    """The "url" smart block field.

    This is a generic handler. In all blocks, it converts any "url"
    field from using resolveuid to an "absolute" URL
    """

    order = 1
    block_type = None
    fields = ["url", "href", "provider_url", "link", 'getRemoteUrl',
              "attachedImage", 'attachedimage', 'getPath', 'getURL', '@id']

    def __init__(self, context):
        self.context = context

    def __call__(self, block):
        dirty = False
        # Convert absolute links to resolveuid
        for field in self.fields:
            link = block.get(field, "")
            if link and isinstance(link, str):
                if 'resolveuid' not in link:
                    block[field] = path2uid(context=self.context,
                                            link=clean_url(link))
                    dirty = True
                    logger.info("fixed block field:'%s' in %s (%s) => (%s)",
                                field, self.context.absolute_url(), link,
                                block[field])
            elif link and isinstance(link, list):
                # Detect if it has an object inside with an
                # "@id" key (object_widget)
                if link and isinstance(link[0], dict) \
                        and "@id" in link[0]:
                    for item in link:
                        if 'resolveuid' not in item['@id']:
                            old = item['@id']
                            item["@id"] = path2uid(
                                context=self.context,
                                link=clean_url(item["@id"])
                            )
                            dirty = True
                            logger.info(
                                "fixed block field:'%s' in %s (%s) => (%s)",
                                field, self.context.absolute_url(), old,
                                item['@id'])
                elif link and isinstance(link[0], str):
                    dirty = any(
                        ['resolveuid' not in bit for bit in link]) or dirty
                    block[field] = [
                        path2uid(context=self.context, link=clean_url(bit))
                        for bit in link
                    ]

        return dirty


class SlateBlockTransformer(object):
    """SlateBlockTransformer."""

    def __init__(self, context):
        self.context = context

    def handle_a(self, child):
        """Convert absolute links to resolveuid
        http://localhost:55001/plone/link-target
        ->
        ../resolveuid/023c61b44e194652804d05a15dc126f4"""

        dirty = False

        data = child.get("data", {})
        if data.get("link", {}).get("external", {}).get("external_link"):
            link = data["link"]["external"]["external_link"]
            if "demo-freshwater" in link:
                old = data['link']['external']['external_link']
                data['link']['external']['external_link'] = path2uid(
                    self.context,
                    clean_url(link)
                )
                logger.info(
                    "fixed type:'internal_link' in %s (%s) => (%s)",
                    self.context.absolute_url(), old, link
                )
                dirty = True

        if child.get('url'):
            link = child['url']
            if 'demo-freshwater' in link:
                child['url'] = path2uid(self.context, clean_url(link))
                logger.info(
                    "fixed type:'internal_link' in %s (%s) => (%s)",
                    self.context.absolute_url(), link, child['url']
                )
                dirty = True

        return dirty

    def __call__(self, block):
        if (block or {}).get('@type') != 'slate':
            return None
        if 'value' not in block:        # avoid empty blocks
            return None
        value = block['value']
        children = iterate_children(value or [])
        status = []

        for child in children:
            node_type = child.get("type")
            if node_type:
                handler = getattr(self, "handle_" + node_type, None)
                if handler:
                    status.append(handler(child))

        return any(status)


class ContainerBlockFixer(object):
    """ContainerBlockFixer"""
    def __init__(self, context):
        self.context = context
        self.fixer = ResolveUIDDeserializerBase(self.context)

    def __call__(self, block):
        dirty = False

        for card in block.get('cards', []):
            if self.fixer(card):
                dirty = True

            for source in card.get('source', []):
                if self.fixer(source):
                    dirty = True

        for tab in block.get('tabs', []):
            for source in tab.get('source', []):
                if self.fixer(source):
                    dirty = True

        if dirty:
            self.context._p_changed = True


def run_upgrade(setup_context):
    """ run upgrade to 1003
    """

    catalog = api.portal.get_tool("portal_catalog")

    brains = catalog(_nonsense=True)

    for _, brain in enumerate(brains):
        obj = brain.getObject()

        if hasattr(obj.aq_inner.aq_self, 'blocks') and \
                hasattr(obj.aq_inner.aq_self, 'blocks_layout'):
            traverser = BlocksTraverser(obj)

            slate_fixer = SlateBlockTransformer(obj)
            traverser(slate_fixer)

            imagecards_fixer = ContainerBlockFixer(obj)
            traverser(imagecards_fixer)

            dumped = json.dumps(obj.blocks)

            if 'backend' in dumped:
                import pdb
                pdb.set_trace()
            if 'localhost' in dumped:
                import pdb
                pdb.set_trace()
            if 'demo-freshwater' in dumped:
                import pdb
                pdb.set_trace()

            assert 'backend' not in dumped
            assert 'localhost' not in dumped
            assert 'demo-freshwater' not in dumped

        # if i % 200 == 0:
        #     transaction.savepoint()
