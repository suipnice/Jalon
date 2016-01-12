# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('jalon.policy-various.txt') is None:
        return

    # Add additional setup code here


def installHandler(self):
    if self.readDataFile('jalon.policy-install.txt') is None:
        return

    listeInstall = ["collective.quickupload", "collective.js.jqueryui", "jalon.content", "jalon.theme", "jalon.bdd", "jalon.pas.bdd", "jalon.connect", "jalon.wims", "jalon.primo", "jalon.elasticsearch", "jalon.wowza", "anz.casclient", "plone.app.ldap", "Products.Ploneboard"]
    if self.readDataFile('jalon.policy-recipe.txt') is not None:
        listeInstall = listeInstall.append("jalon.theme")

    portal = self.getSite()
    qi = getToolByName(portal, 'portal_quickinstaller')
    for mod in listeInstall:
        if not qi.isProductInstalled(mod):
            # there is no GS profile for mod.
            qi.installProduct(mod)
            if mod == "jalon.bdd":
                try:
                    portal.portal_jalon_bdd.creerBDD()
                except:
                    "Echec : bdd déjà créée ?"


def updateCatalog(self, clear=True):
    if self.readDataFile('jalon.policy-install.txt') is None:
        return

    portal = self.getSite()
    portal.setLayout("firstpage_view")

    listeExclude = ["news", "events", "Members"]
    for rep in listeExclude:
        if hasattr(portal, rep):
            obj = getattr(portal, rep)
            obj.setTitle(rep)
            obj.setExcludeFromNav(True)

    logger = self.getLogger('jalon.policy updateCatalog')
    logger.info('Updating catalog (with clear=%s) so items in profiles/default/structure are indexed...' % clear)
    catalog = portal.portal_catalog
    err = catalog.refreshCatalog(clear=clear)
    if not err:
        logger.info('...done.')
    else:
        logger.warn('Could not update catalog.')
