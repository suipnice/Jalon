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
        portal = self.context.portal_url.getPortalObject()
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

        course_path = self.context.getPhysicalPath()
        course_map_item_adder = self.getCourseItemAdderList(course_link, "%s/%s" % (course_path[-2], course_path[-1]), portal)

        has_course_map = self.context.getPlan()

        course_news = self.context.getActualitesCours()
        course_map = self.context.getCourseMap(user.getId(), is_personnel, course_news['listeActu'], portal)

        is_course_map_help_text = False
        course_map_help_text = ""
        portal_jalon_properties = portal.portal_jalon_properties
        if portal_jalon_properties.getJalonProperty("activer_aide_plan"):
            is_course_map_help_text = True
            course_map_help_text = portal_jalon_properties.getJalonProperty("lien_aide_plan")

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
                "course_map_item_adder":           course_map_item_adder,
                "has_course_map":                  has_course_map,
                "course_map":                      course_map,
                "is_course_map_help_text":         is_course_map_help_text,
                "course_map_help_text":            course_map_help_text,
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
                "course_forums":                   course_forums,
                "portal":                          portal}

    def getCourseItemAdderList(self, course_link, course_path, portal):
        item_adder_list = self.getCourseItemAdderMenuList(course_link, course_path, portal)
        return [{"menu_adder_class":         "button small course-title dropdown",
                 "menu_adder_data-dropdown": "add-title-text",
                 "menu_adder_icon":          "fa fa-paragraph",
                 "menu_adder_name":          "Titre / texte",
                 "menu_adder_items":         [{"item_link": "%s/add_course_map_item_form?item_type=1" % self.context.absolute_url(),
                                               "item_icon": "fa fa-paragraph fa-fw",
                                               "item_name": "Titre"},
                                              {"item_link": "%s/add_course_map_item_form?item_type=2" % self.context.absolute_url(),
                                               "item_icon": "fa fa-align-justify fa-fw",
                                               "item_name": "Texte libre"}]},
                {"menu_adder_class":         "button small course-space_el dropdown",
                 "menu_adder_data-dropdown": "add-space_el",
                 "menu_adder_icon":          "fa fa-home",
                 "menu_adder_name":          "De mon espace",
                 "menu_adder_items":         item_adder_list["my_space"]},
                {"menu_adder_class":         "button small course-activity dropdown",
                 "menu_adder_data-dropdown": "add-activity",
                 "menu_adder_icon":          "fa fa-random",
                 "menu_adder_name":          "Activité",
                 "menu_adder_items":         item_adder_list["activity"]},
                {"menu_adder_class":         "button small course-direct dropdown",
                 "menu_adder_data-dropdown": "add-direct",
                 "menu_adder_icon":          "fa fa-cloud-upload",
                 "menu_adder_name":          "Ajout rapide",
                 "menu_adder_items":         item_adder_list["add"]}]

    def getCourseItemAdderMenuList(self, course_link, course_path, portal):
        portal_link = portal.absolute_url()
        my_space = portal.portal_jalon_properties.getPropertiesMonEspace()

        item_adder_list = {"my_space": [],
                           "activity": [],
                           "add":      []}
        # Menu Mon Espace
        if my_space["activer_fichiers"]:
            item_adder_list["my_space"].append({"item_link": "%s/mon_espace/mes_fichiers/course_add_view?course_path=%s" % (portal_link, course_path),
                                                "item_icon": "fa fa-files-o fa-fw",
                                                "item_name": "Fichiers"})
        if my_space["activer_presentations_sonorisees"]:
            item_adder_list["my_space"].append({"item_link": "%s/mon_espace/mes_presentations_sonorisees/course_add_view?course_path=%s" % (portal_link, course_path),
                                                "item_icon": "fa fa-microphone fa-fw",
                                                "item_name": "Présentations sonorisées"})
        if my_space["activer_liens"]:
            item_adder_list["my_space"].append({"item_link": "%s/mon_espace/mes_ressources_externes/course_add_view?course_path=%s" % (portal_link, course_path),
                                                "item_icon": "fa fa-external-link fa-fw",
                                                "item_name": "Ressources externes"})
        if my_space["activer_webconferences"]:
            item_adder_list["my_space"].append({"item_link": "%s/mon_espace/mes_webconferences/course_add_view?course_path=%s" % (portal_link, course_path),
                                                "item_icon": "fa fa-headphones fa-fw",
                                                "item_name": "Webconférence"})
        if my_space["activer_lille1pod"]:
            item_adder_list["my_space"].append({"item_link": "%s/mon_espace/mes_videos_pod/course_add_view?course_path=%s" % (portal_link, course_path),
                                                "item_icon": "fa fa-youtube-play fa-fw",
                                                "item_name": "Vidéos"})
        if my_space["activer_vod"]:
            item_adder_list["my_space"].append({"item_link": "%s/mon_espace/mes_vods/course_add_view?course_path=%s" % (portal_link, course_path),
                                                "item_icon": "fa fa-video-camera fa-fw",
                                                "item_name": "VOD"})
        # Menu Activités
        item_adder_list["activity"].append({"item_link": "%s/add_course_activity_form?activity_type=1" % course_link,
                                            "item_icon": "fa fa-fw fa-inbox",
                                            "item_name": "Boite de dépôts"})
        if my_space["activer_exercices_wims"]:
            item_adder_list["activity"].append({"item_link": "%s/add_course_activity_form?activity_type=2" % course_link,
                                                "item_icon": "fa fa-fw fa-gamepad",
                                                "item_name": "Auto évaluation WIMS"})
            item_adder_list["activity"].append({"item_link": "%s/add_course_activity_form?activity_type=3" % course_link,
                                                "item_icon": "fa fa-fw fa-graduation-cap",
                                                "item_name": "Examen WIMS"})
        if my_space["activer_webconferences"]:
            item_adder_list["activity"].append({"item_link": "%s/activate_webconference_form" % course_link,
                                                "item_icon": "fa fa-fw fa-globe",
                                                "item_name": "Salle virtuelle"})
        # Menu Ajout rapide
        if my_space["activer_fichiers"]:
            item_adder_list["add"].append({"item_link": "%s/create_and_add_course_file_form" % course_link,
                                           "item_icon": "fa fa-files-o fa-fw",
                                           "item_name": "Fichiers"})
        if my_space["activer_liens"]:
            item_adder_list["add"].append({"item_link": "%s/create_and_add_course_external_resource_form" % course_link,
                                           "item_icon": "fa fa-external-link fa-fw",
                                           "item_name": "Ressources externes"})
        return item_adder_list
