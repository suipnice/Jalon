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
        is_personnel = self.context.isPersonnel(user, mode_etudiant)

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

        if is_personnel:
            #to : training offer
            course_to_actions_list = [{"action_link": "%s/course_delete_training_offer_form" % course_link,
                                       "action_icon": "fa fa-trash fa-lg fa-fw no-pad alert",
                                       "action_name": "Supprimer"},
                                      {"action_link": "%s/course_add_training_offer_form" % course_link,
                                       "action_icon": "fa fa-plus-circle fa-lg fa-fw no-pad",
                                       "action_name": "Ajouter"}]
            #nr : nominative registraion
            course_nr_actions_list = [{"action_link": "%s/course_delete_nominative_registration_form" % course_link,
                                       "action_icon": "fa fa-trash fa-lg fa-fw no-pad alert",
                                       "action_name": "Supprimer"},
                                      {"action_link": "%s/course_add_nominative_registration_form" % course_link,
                                       "action_icon": "fa fa-plus-circle fa-lg fa-fw no-pad",
                                       "action_name": "Ajouter"}]
            #er : email registraion
            course_er_actions_list = [{"action_link": "%s/course_delete_email_registration_form" % course_link,
                                       "action_icon": "fa fa-trash fa-lg fa-fw no-pad alert",
                                       "action_name": "Supprimer"},
                                      {"action_link": "%s/course_add_email_registration_form" % course_link,
                                       "action_icon": "fa fa-plus-circle fa-lg fa-fw no-pad",
                                       "action_name": "Ajouter"}]
            #pr : password registraion
            course_pr_actions_list = [{"action_link": "%s/course_delete_password_registration_form" % course_link,
                                       "action_icon": "fa fa-trash fa-lg fa-fw no-pad alert",
                                       "action_name": "Supprimer"},
                                      {"action_link": "%s/course_add_password_registration_form" % course_link,
                                       "action_icon": "fa fa-plus-circle fa-lg fa-fw no-pad",
                                       "action_name": "Ajouter"}]
            #cr : coreader registraion
            course_cr_actions_list = [{"action_link": "%s/course_delete_coreader_registration_form" % course_link,
                                       "action_icon": "fa fa-trash fa-lg fa-fw no-pad alert",
                                       "action_name": "Supprimer"},
                                      {"action_link": "%s/course_add_coreader_registration_form" % course_link,
                                       "action_icon": "fa fa-plus-circle fa-lg fa-fw no-pad",
                                       "action_name": "Ajouter"}]
        else:
            course_to_actions_list = [{"action_link": "%s/course_display_training_offer_page" % course_link,
                                       "action_icon": "fa fa-eye fa-lg fa-fw no-pad",
                                       "action_name": "Voir"}]
            course_nr_actions_list = [{"action_link": "%s/course_display_nominative_registration_page" % course_link,
                                       "action_icon": "fa fa-eye fa-lg fa-fw no-pad",
                                       "action_name": "Voir"}]
            course_er_actions_list = [{"action_link": "%s/course_display_email_registration_page" % course_link,
                                       "action_icon": "fa fa-eye fa-lg fa-fw no-pad",
                                       "action_name": "Voir"}]
            course_pr_actions_list = [{"action_link": "%s/course_display_password_registration_page" % course_link,
                                       "action_icon": "fa fa-eye fa-lg fa-fw no-pad",
                                       "action_name": "Voir"}]
            course_cr_actions_list = [{"action_link": "%s/course_display_coreader_registration_page" % course_link,
                                       "action_icon": "fa fa-eye fa-lg fa-fw no-pad",
                                       "action_name": "Voir"}]

        course_life_tabs_list = []

        course_news = self.context.getActualitesCours()
        course_life_tabs_list.append({"tab_link":   "#course_life-historique",
                                      "tab_number": course_news["nbActu"],
                                      "tab_icon":   "fa fa-bell fa-2x",
                                      "tab_name":   "Historique"})

        course_news_title = "La dernière nouveauté du cours"
        if course_news["nbActu"] >= 4:
            course_news_title = "Les dernières nouveautés du cours"
        else:
            course_news_title = "Les 3 dernières nouveautés du cours"

        course_advert = self.context.getAnnonces(user, self.request, mode_etudiant)
        course_life_tabs_list.append({"tab_link":   "#course_life-annonces",
                                      "tab_number": course_advert["nbAnnonces"],
                                      "tab_icon":   "fa fa-bullhorn fa-2x",
                                      "tab_name":   "Annonces"})

        course_forums = self.context.getDicoForums()
        course_life_tabs_list.append({"tab_link":   "#course_life-forum",
                                      "tab_number": course_forums["nbForums"],
                                      "tab_icon":   "fa fa-comments fa-2x",
                                      "tab_name":   "Forums"})

        return {"is_personnel":                    is_personnel,
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
                "course_glossary_letter_list":     course_glossary_letter_list,
                "is_course_author":                self.context.isAuteurs(user.getId()),
                "course_training_offer":           self.context.getAffichageFormation(),
                "course_to_actions_list":          course_to_actions_list,
                "course_nominative_registration":  len(self.context.getGroupe()),
                "course_nr_actions_list":          course_nr_actions_list,
                "course_email_registration":       len(self.context.getInvitations()),
                "course_er_actions_list":          course_er_actions_list,
                "course_password_registration":    len(self.context.getInscriptionsLibres()),
                "course_pr_actions_list":          course_pr_actions_list,
                "is_course_password":              self.context.getLibre() and is_personnel,
                "course_password":                 self.context.getLienMooc(),
                "course_coreader_registration":    len(self.context.getCoLecteurs()),
                "course_cr_actions_list":          course_cr_actions_list,
                "course_life_tabs_list":           course_life_tabs_list,
                "course_news":                     course_news,
                "course_news_title":               course_news_title,
                "course_advert":                   course_advert,
                "course_forums":                   course_forums}
