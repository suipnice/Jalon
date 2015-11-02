# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getMultiAdapter


class JalonConnecteurBDD(BrowserView):

    def getUrlConnexion(self):
        bdd = getToolByName(self, "portal_jalon_bdd")
        return bdd.getUrlConnexion()

    def setUrlConnexion(self, urlConnexion):
        bdd = getToolByName(self, "portal_jalon_bdd")
        return bdd.setUrlConnexion(self, urlConnexion)

    def getTypeBDD(self):
        bdd = getToolByName(self, "portal_jalon_bdd")
        return bdd.getTypeBDD()

    def setTypeBDD(self, typeBDD):
        bdd = getToolByName(self, "portal_jalon_bdd")
        return bdd.setTypeBDD(typeBDD)

    def traductions_fil(self, key):
        bdd = getToolByName(self, "portal_jalon_bdd")
        return bdd.traductions_fil(key)

    def isAnonyme(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.anonymous()
