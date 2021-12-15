""" Base test cases
"""
from Products.CMFPlone import setuphandlers
from plone.app.testing import TEST_USER_ID
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import setRoles
from plone.testing.zope import installProduct, uninstallProduct


class EEAFixture(PloneSandboxLayer):
    """ EEA Testing Policy
    """
    def setUpZope(self, app, configurationContext):
        """ Setup Zope
        """
        import plone.restapi
        import eea.restapi
        import freshwater.content
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=eea.restapi)
        self.loadZCML(package=freshwater.content)
        installProduct(app, 'freshwater.content')

    def setUpPloneSite(self, portal):
        """ Setup Plone
        """
        applyProfile(portal, 'freshwater.content:default')

        # Default workflow
        wftool = portal['portal_workflow']
        wftool.setDefaultChain('simple_publication_workflow')

        # Login as manager
        setRoles(portal, TEST_USER_ID, ['Manager'])

        # Add default Plone content
        try:
            applyProfile(portal, 'plone.app.contenttypes:plone-content')
        except KeyError:
            # BBB Plone 4
            setuphandlers.setupPortalContent(portal)

        # Create testing environment
        portal.invokeFactory("Folder", "sandbox", title="Sandbox")


    def tearDownZope(self, app):
        """ Uninstall Zope
        """
        uninstallProduct(app, 'freshwater.content')

EEAFIXTURE = EEAFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(EEAFIXTURE,),
                                       name='EEAcontent:Functional')
