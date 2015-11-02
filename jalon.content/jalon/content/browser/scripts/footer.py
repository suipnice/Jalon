# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import ViewletBase

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

import copy


class Footer(ViewletBase):
    """Class pour le footer
    """

    def getFooter(self):
        context = aq_inner(self.context)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        jalon_properties = getToolByName(portal, 'portal_jalon_properties')

        dico = copy.copy(jalon_properties.getPropertiesInfos())
        dico["site"] = portal.Title()
        dico["activer_aide"] = jalon_properties.getJalonProperty("activer_aide")
        dico["lien_aide"] = jalon_properties.getJalonProperty("lien_aide")
        return dico
