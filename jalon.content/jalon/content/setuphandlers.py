# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import AccessContentsInformation

def updateCatalog(self, clear=True):
    if self.readDataFile('jalon.content-install.txt') is None:
        return

    portal = self.getSite()
    portal.setTitle("Jalon 4.5")

    if not getattr(portal.Members, "admin", None):
        portal.Members.invokeFactory(type_name='JalonFolder', id="admin")
        home = getattr(portal.Members, "admin")
        home.addSubJalonFolder("admin")

        portal.cours.invokeFactory(type_name='JalonFolder', id="admin")
        cours = getattr(portal.cours, "admin")
        cours.setTitle("Mes cours")
        cours.setPortlets()

        modMember = portal.portal_membership.getMemberById("admin")
        modMember.fullname = "Administrateur Jalon"
        modMember.email = "no-reply@jalon.unice.fr"

        logger = self.getLogger('jalon.content updateCatalog')
        logger.info('Updating catalog (with clear=%s) so items in profiles/default/structure are indexed...' % clear)
        catalog = portal.portal_catalog
        err = catalog.refreshCatalog(clear=clear)
        if not err:
            logger.info('...done.')
        else:
            logger.warn('Could not update catalog.')

    etudiants = getattr(portal, "etudiants")
    etudiants.manage_permission(AccessContentsInformation, roles=['Anonymous', 'Member', 'Authenticated', 'Manager'])
