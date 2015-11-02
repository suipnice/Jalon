# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.site.hooks import getSite

from jalon.content.content import jalon_utils


class JalonUser(BrowserView):

    def isAnonyme(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        return portal_state.anonymous()

    """ retourne le fullname du membre courant """
    def getFullname(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        authMember = portal.portal_membership.getAuthenticatedMember()
        fullname = authMember.getProperty("fullname", authMember.getId())
        if fullname:
            return fullname
        else:
            return authMember.getProperty("displayName", authMember.getId())

    def getListeUtilisateur(self):
        portal = getSite()
        return portal.acl_users.source_users.getUsers()

    def traductions_fil(self, key):
        return jalon_utils.traductions_fil(key)

    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)
