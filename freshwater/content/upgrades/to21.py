"""Upgrade to 21."""

from Products.CMFCore.utils import getToolByName


LEGACY_MISSING_PACKAGES = {
    'collective.z3cform.datagridfield',
    'eea.dexterity.rdfmarshaller',
    'eea.rabbitmq.plone',
    'plone.app.imagecropping',
    'plone.formwidget.autocomplete',
    'plone.formwidget.contenttree',
}


def run_upgrade(context):
    """Remove GenericSetup markers for add-ons no longer installed.

    The add-ons have been removed from the Python environment without their
    uninstall profiles being run.  Their profile-version markers therefore
    make Plone report missing add-ons during an upgrade.  This only removes
    GenericSetup bookkeeping; it does not attempt to remove data left by the
    add-ons.
    """
    setup = getToolByName(context, 'portal_setup')
    profile_versions = getattr(setup, '_profile_upgrade_versions', {})

    for profile_id in list(profile_versions):
        if profile_id.split(':', 1)[0] not in LEGACY_MISSING_PACKAGES:
            continue
        setup.unsetLastVersionForProfile(profile_id)
