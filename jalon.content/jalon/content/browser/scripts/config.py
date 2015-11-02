# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getMultiAdapter

from jalon.content.content import jalon_utils


class JalonConfiguration(BrowserView):

    def getPropertiesTwitter(self, key=None):
        properties = getToolByName(self, "portal_jalon_properties")
        return properties.getPropertiesTwitter(key)

    def isAnonyme(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.anonymous()

    def traductions_fil(self, key):
        return jalon_utils.traductions_fil(key)

    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)
