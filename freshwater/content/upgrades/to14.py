''' Upgrade to 14 '''

from plone import api


def run_upgrade(setup_context):
    """ Run upgrade to 14
    """

    pl = api.portal.get_tool('portal_languages')
    default_language = pl.getDefaultLanguage()
    root = api.portal.get()
    root.language = default_language
