# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

from jalon.content.browser.config.jalonconfig import IJalonConfigControlPanel
from jalon.content.browser.config.jalonconfiguration import IJalonConfigurationControlPanel
from jalon.content.browser.config.jalonmaintenance import IJalonMaintenanceControlPanel

from jalon.content.content import jalon_utils


class FirstPage(BrowserView):
    """Class pour le first_page
    """

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    #def getMaintenance(self, portal):
    #    return IJalonMaintenanceControlPanel(portal).getMaintenance()

    def getInformation(self, portal):
        return IJalonMaintenanceControlPanel(portal).getInformation()

    def getViderCache(self, portal):
        return IJalonMaintenanceControlPanel(portal).getViderCache()

    def getConnexion(self):
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

    def getMonEspace(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
        authMember = portal.portal_membership.getAuthenticatedMember()
        fullname = authMember.getProperty("fullname", authMember.getId())
        if not fullname:
            fullname = authMember.getProperty("displayName", authMember.getId())
        podcast = False
        variablesPodcast = portal_jalon_properties.getVariablesPodcast()
        if variablesPodcast["activerPodcasts"] and portal.absolute_url().startswith(variablesPodcast["uploadPodcasts"]) and authMember.getId() in portal_jalon_properties.getUsersPodcast("tiny"):
            podcast = True
        return {"site"                 : portal.Title(),
                "activer"              : portal_jalon_properties.getPropertiesMonEspace(),
                "grid"                 : portal_jalon_properties.getGridMonEspace(),
                "podcast"              : podcast,
                "fullname"             : fullname,
                "maintenance"          : portal_jalon_properties.getPropertiesMaintenance(),
                "vidercache"           : portal_jalon_properties.getJalonProperty("annoncer_vider_cache"),
                "messages"             : portal_jalon_properties.getPropertiesMessages(),
                "url_news_maintenance" : portal_jalon_properties.getJalonProperty("url_news_maintenance"),
                "isCreer"              : authMember.has_role("Manager"),
                "lien_bug"             : portal_jalon_properties.getJalonProperty("lien_assitance"),
                "etablissement"        : portal_jalon_properties.getJalonProperty("etablissement")}

    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)
