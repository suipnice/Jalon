# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from zope.component.hooks import getSite

from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

_marker = []


class MySection(GlobalSectionsViewlet):
    index = ViewPageTemplateFile('../templates/sections.pt')

    def __init__(self, *args, **kwargs):
        super(MySection, self).__init__(*args, **kwargs)
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        authMember = portal.portal_membership.getAuthenticatedMember()
        self.jalon_tabs = [{"id":          "index_html",
                            "url":         portal.absolute_url(),
                            "label":       'label_monespace',
                            "name":        _(u"Mon espace"),
                            "description": _(u"Mon espace"),
                            "roles":       ["Manager", "Secretaire", "Personnel"],
                            "visible":     False},
                           {"id":          "cours",
                            "url":         "%s/cours/%s" % (portal.absolute_url(), authMember.getId()),
                            "name":        _(u"Mes cours"),
                            "description": _(u"Mes cours"),
                            "roles":       ["Manager", "Personnel", "Etudiant", "EtudiantJalon"],
                            "visible":     False},
                           {"id":          "etudiants",
                            "url":         "%s/etudiants" % portal.absolute_url(),
                            "name":        _(u"Mes étudiants"),
                            "description": _(u"Mes étudiants"),
                            "roles":       ["Manager", "Secretaire", "Personnel"],
                            "visible":     False},
                           {"id":          "logout",
                            "url":         "%s/logout" % portal.absolute_url(),
                            "name":        _(u"Déconnexion"),
                            "description": _(u"Déconnexion"),
                            "roles":       ["Manager", "Personnel", "Etudiant", "EtudiantJalon", "Secretaire",  "Member", "Authenticated"],
                            "visible":     False}
                          ]
        """
                           {"id": "didacticiels",
                           "url": "%s/didacticiels" % portal.absolute_url(),
                          "name": _(u"Aide"),
                   "description": _(u"Aide"),
                         "roles": ["Manager", "Personnel", "Etudiant", "EtudiantJalon"],
                       "visible": True},
                           {"id":          "etudiants",
                            "url":         "%s/etudiants" % portal.absolute_url(),
                            "name":        _(u"Mes promos"),
                            "description": _(u"Mes promos"),
                            "roles":       ["Etudiant"],
                            "visible":     False},
        """

    def isAnonyme(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        if portal_state.anonymous():
            return True
        return False

    def isSygefor(self, authMember):
        if not (authMember.has_role("Etudiant") or authMember.has_role("EtudiantJalon") or authMember.has_role("Personnel") or authMember.has_role("Manager")):
            return True
        return False


    def getJalonTabs(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        portal = portal_state.portal()
        authMember = portal.portal_membership.getAuthenticatedMember()
        return [{"id":          "index_html",
                 "url":         portal.absolute_url(),
                 "label":       'label_monespace',
                 "name":        _(u"Mon espace"),
                 "description": _(u"Mon espace"),
                 "roles":       ["Manager", "Secretaire", "Personnel"],
                 "visible":     False},
                {"id":          "cours",
                 "url":         "%s/cours/%s" % (portal.absolute_url(), authMember.getId()),
                 "name":        _(u"Mes cours"),
                 "description": _(u"Mes cours"),
                 "roles":       ["Manager", "Personnel", "Etudiant", "EtudiantJalon"],
                 "visible":     False},
                {"id":          "etudiants",
                 "url":         "%s/etudiants" % portal.absolute_url(),
                 "name":        _(u"Mes étudiants"),
                 "description": _(u"Mes étudiants"),
                 "roles":       ["Manager", "Secretaire", "Personnel"],
                 "visible":     False},
                {"id":          "logout",
                 "url":         "%s/logout" % portal.absolute_url(),
                 "name":        _(u"Déconnexion"),
                 "description": _(u"Déconnexion"),
                 "roles":       ["Manager", "Personnel", "Etudiant", "EtudiantJalon", "Secretaire",  "Member", "Authenticated"],
                 "visible":     False}
               ]

    def getSelectedTabs(self, default_tab='index_html'):
        plone_url = getToolByName(self.context, 'portal_url')()
        plone_url_len = len(plone_url)

        request = self.request
        url = request['URL']
        path = url[plone_url_len:]

        for action in self.jalon_tabs[1:]:
            if path.startswith("/%s" % action["id"]):
                return action['id']

        return default_tab
