# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

import urllib

from logging import getLogger
LOG = getLogger('[MyCoursesView]')


class MyCoursesView(BrowserView):
    """Class pour le first_page
    """

    def __init__(self, context, request):
        #LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getUserFolder(self, user_id):
        LOG.info("----- getUserFolder -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        return getattr(portal.cours, user_id)

    def getMyCoursesView(self, user, tab=None):
        LOG.info("----- getMyCoursesView -----")

        folder = self.getUserFolder(user.getId())
        folder_link = self.context.absolute_url()

        is_manager = user.has_role("Manager")
        is_student = user.has_role("Etudiant") or user.has_role("EtudiantJalon")

        actions_list = [{"css_class":   "button create expand",
                         "action_link": "%s/folder_form?macro=macro_mescours_actions&amp;formulaire=add_course" % folder_link,
                         "action_icon": "fa fa-plus-circle",
                         "action_name": "Créer un cours"},
                        {"css_class":   "button",
                         "action_link": "%s/lister_auteur" % folder_link,
                         "action_icon": "fa fa-code-fork",
                         "action_name": "Dupliquer un cours"}]
        if not is_manager:
            del actions_list[-1]

        if not tab:
            tab = "1" if self.context.getComplement() == "True" else "2"
        tabs_list = [{"css_class": "button small selected" if tab == "1" else "button small secondary",
                      "tab_link":  "%s?onglet=1" % folder_link,
                      "tab_icon":  "fa fa-star fa-fw",
                      "tab_name":  "Favoris"},
                     {"css_class": "button small selected" if tab == "2" else "button small secondary",
                      "tab_link":  "%s?onglet=2" % folder_link,
                      "tab_icon":  "fa fa-user fa-fw",
                      "tab_name":  "Auteur"},
                     {"css_class": "button small selected" if tab == "3" else "button small secondary",
                      "tab_link":  "%s?onglet=3" % folder_link,
                      "tab_icon":  "fa fa-users fa-fw",
                      "tab_name":  "Co-auteur"},
                     {"css_class": "button small selected" if tab == "4" else "button small secondary",
                      "tab_link":  "%s?onglet=4" % folder_link,
                      "tab_icon":  "fa fa-graduation-cap fa-fw",
                      "tab_name":  "Lecteur"},
                     {"css_class": "button small selected" if tab == "5" else "button small secondary",
                      "tab_link":  "%s?onglet=5" % folder_link,
                      "tab_icon":  "fa fa-folder fa-fw",
                      "tab_name":  "Archives"}]

        courses_list = folder.getListeCoursEns(user, tab)
        return {"tab":          tab,
                "is_manager":   is_manager,
                "is_student":   is_student,
                "actions_list": actions_list,
                "tabs_list":    tabs_list,
                "courses_list": courses_list}
