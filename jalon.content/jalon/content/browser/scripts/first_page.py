# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

from jalon.content.content import jalon_utils

from logging import getLogger
LOG = getLogger('[FirstPage]')


class FirstPage(BrowserView):
    """Class pour le first_page
    """

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getConnexion(self):
        # LOG.info("----- getConnexion -----")
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        #jalon_configuration = IJalonConfigurationControlPanel(portal)
        portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
        return {"site": portal.Title(),
                "maintenance":              portal_jalon_properties.getPropertiesMaintenance(),
                "activer_message_general":  portal_jalon_properties.getJalonProperty("activer_message_general"),
                "message_general":          portal_jalon_properties.getJalonProperty("message_general"),
                "activer_lien_sesame":      portal_jalon_properties.getJalonProperty("activer_lien_sesame"),
                "lien_sesame":              portal_jalon_properties.getJalonProperty("lien_sesame"),
                "lien_bug":                 portal_jalon_properties.getJalonProperty("lien_assitance"),
                "etablissement":            portal_jalon_properties.getJalonProperty("etablissement"),
                "activer_cas":              portal_jalon_properties.getJalonProperty("activer_cas"),
                "activer_creationcompte":   portal_jalon_properties.getJalonProperty("activer_creationcompte"),
                }

    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)
