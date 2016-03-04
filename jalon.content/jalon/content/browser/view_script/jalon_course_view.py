# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[JalonCourseView]')


class JalonCourseView(BrowserView):
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

    def getBreadcrumbs(self):
        portal = self.context.portal_url.getPortalObject()
        return [{"title": _(u"Mes cours"),
                 "icon":  "fa fa-university",
                 "link":  "%s/mes_cours" % portal.absolute_url()},
                {"title": self.context.Title(),
                 "icon":  "fa fa-book",
                 "link":  self.context.absolute_url()}]

    def getCourseView(self, user, mode_etudiant):
        course_acces = self.context.getAcces()

        course_author = self.context.getAuteur()
        course_author_link = "mailto:%s" % course_author['email']
        is_ladp_actived = self.context.isLDAP()
        if is_ladp_actived:
            base_user_book = self.context.getBaseAnnuaire()
            course_author_link = self.context.getFicheAnnuaire(course_author, base_user_book)

        course_coauthor_list = []
        if is_ladp_actived:
            for course_coauthor in self.context.getCoAuteursCours():
                course_coauthor_list.append({"course_coauthor_name": course_coauthor["fullname"],
                                             "course_coauthor_link": self.context.getFicheAnnuaire(course_coauthor, base_user_book)})
        else:
            for course_coauthor in self.context.getCoAuteursCours():
                course_coauthor_list.append({"course_coauthor_name": course_coauthor["fullname"],
                                             "course_coauthor_link": "mailto:%s" % course_coauthor["email"]})

        course_link = self.context.absolute_url()
        course_map_action_list = [{"action_link": "%s/download_wims_score_form" % course_link,
                                   "action_icon": "fa fa-download fa-fw",
                                   "action_name": "Télécharger les notes WIMS"},
                                  {"action_link": "%s/purge_course_form" % course_link,
                                   "action_icon": "fa fa-filter fa-fw",
                                   "action_name": "Purger les travaux étudiants"},
                                  {"action_link": "%s/delete_wims_activity_form" % course_link,
                                   "action_icon": "fa fa-trash-o  fa-fw",
                                   "action_name": "Supprimer les activités WIMS"}]

        course_bibliography_dict = self.context.getGloBib('bibliographie')
        course_bibliography_letter_list = course_bibliography_dict.keys()
        course_bibliography_letter_list.sort()
        course_has_bibliography = len(course_bibliography_letter_list)

        course_glossary_dict = self.context.getGloBib('glossaire')
        course_glossary_letter_list = course_glossary_dict.keys()
        course_glossary_letter_list.sort()
        course_has_glossary = len(course_glossary_letter_list)

        return {"is_personnel":                    self.context.isPersonnel(user, mode_etudiant),
                "is_public":                       "success" if course_acces == "Public" else "disabled",
                "course_short_description":        self.context.getDescriptionCourte(),
                "course_author_name":              course_author["fullname"],
                "course_author_link":              course_author_link,
                "course_coauthor_list":            course_coauthor_list,
                "course_map_action_list":          course_map_action_list,
                "course_has_bibliography":         course_has_bibliography,
                "course_bibliography_dict":        course_bibliography_dict,
                "course_bibliography_letter_list": course_bibliography_letter_list,
                "course_has_glossary":             course_has_glossary,
                "course_glossary_dict":            course_glossary_dict,
                "course_glossary_letter_list":     course_glossary_letter_list}
