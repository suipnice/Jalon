# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[JalonCourseView]')


class JalonCourseView(BrowserView):
    """Class pour le first_page
    """

    #to : training offer
    _course_to_actions_list = [{"action_link": "course_delete_training_offer_form",
                                "action_icon": "fa fa-trash fa-lg fa-fw no-pad alert",
                                "action_name": "Supprimer"},
                               {"action_link": "course_add_training_offer_form",
                                "action_icon": "fa fa-plus-circle fa-lg fa-fw no-pad",
                                "action_name": "Ajouter"},
                               {"action_link": "course_display_training_offer_page",
                                "action_icon": "fa fa-eye fa-lg fa-fw no-pad",
                                "action_name": "Voir"}]
    #nr : nominative registraion
    _course_nr_actions_list = [{"action_link": "course_delete_nominative_registration_form",
                                "action_icon": "fa fa-trash fa-lg fa-fw no-pad alert",
                                "action_name": "Supprimer"},
                               {"action_link": "course_add_nominative_registration_form",
                                "action_icon": "fa fa-plus-circle fa-lg fa-fw no-pad",
                                "action_name": "Ajouter"},
                               {"action_link": "course_display_nominative_registration_page",
                                "action_icon": "fa fa-eye fa-lg fa-fw no-pad",
                                "action_name": "Voir"}]
    #er : email registraion
    _course_er_actions_list = [{"action_link": "course_delete_email_registration_form",
                                "action_icon": "fa fa-trash fa-lg fa-fw no-pad alert",
                                "action_name": "Supprimer"},
                               {"action_link": "course_add_email_registration_form",
                                "action_icon": "fa fa-plus-circle fa-lg fa-fw no-pad",
                                "action_name": "Ajouter"},
                               {"action_link": "course_display_email_registration_page",
                                "action_icon": "fa fa-eye fa-lg fa-fw no-pad",
                                "action_name": "Voir"}]
    #pr : password registraion
    _course_pr_actions_list = [{"action_link": "course_delete_password_registration_form",
                                "action_icon": "fa fa-trash fa-lg fa-fw no-pad alert",
                                "action_name": "Supprimer"},
                               {"action_link": "course_add_password_registration_form",
                                "action_icon": "fa fa-plus-circle fa-lg fa-fw no-pad",
                                "action_name": "Ajouter"},
                               {"action_link": "course_display_password_registration_page",
                                "action_icon": "fa fa-eye fa-lg fa-fw no-pad",
                                "action_name": "Voir"}]
    #cr : coreader registraion
    _course_cr_actions_list = [{"action_link": "course_delete_coreader_registration_form",
                                "action_icon": "fa fa-trash fa-lg fa-fw no-pad alert",
                                "action_name": "Supprimer"},
                               {"action_link": "course_add_coreader_registration_form",
                                "action_icon": "fa fa-plus-circle fa-lg fa-fw no-pad",
                                "action_name": "Ajouter"},
                               {"action_link": "course_display_coreader_registration_page",
                                "action_icon": "fa fa-eye fa-lg fa-fw no-pad",
                                "action_name": "Voir"}]

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

        my_view = {"portal":                       portal,
                   "course_short_description":     self.context.getDescriptionCourte(),
                   "is_personnel":                 self.context.isPersonnel(user, mode_etudiant),
                   "is_public":                    "success" if self.context.getAcces() == "Public" else "disabled",
                   "is_course_author":             self.context.isAuteurs(user.getId()),
                   "course_training_offer":        self.context.getAffichageFormation(),
                   "course_coreader_registration": len(self.context.getCoLecteurs())}

        my_view["is_course_password"] = self.context.getLibre() and my_view["is_personnel"]
        my_view["course_password"] = self.context.getLienMooc()

        course_author = self.context.getAuteur()
        my_view["course_author_name"] = course_author["fullname"]

        course_author_link = "mailto:%s" % course_author['email']
        is_ladp_actived = self.context.isLDAP()
        if is_ladp_actived:
            base_user_book = self.context.getBaseAnnuaire()
            course_author_link = self.context.getFicheAnnuaire(course_author, base_user_book)
        my_view["course_author_link"] = course_author_link

        course_coauthor_list = []
        if is_ladp_actived:
            for course_coauthor in self.context.getCoAuteursCours():
                course_coauthor_list.append({"course_coauthor_name": course_coauthor["fullname"],
                                             "course_coauthor_link": self.context.getFicheAnnuaire(course_coauthor, base_user_book)})
        else:
            for course_coauthor in self.context.getCoAuteursCours():
                course_coauthor_list.append({"course_coauthor_name": course_coauthor["fullname"],
                                             "course_coauthor_link": "mailto:%s" % course_coauthor["email"]})
        my_view["course_coauthor_list"] = course_coauthor_list

        course_link = self.context.absolute_url()
        my_view["course_map_action_list"] = [{"action_link": "%s/download_wims_score_form" % course_link,
                                              "action_icon": "fa fa-download fa-fw",
                                              "action_name": "Télécharger les notes WIMS"},
                                             {"action_link": "%s/purge_course_form" % course_link,
                                              "action_icon": "fa fa-filter fa-fw",
                                              "action_name": "Purger les travaux étudiants"},
                                             {"action_link": "%s/delete_wims_activity_form" % course_link,
                                              "action_icon": "fa fa-trash-o  fa-fw",
                                              "action_name": "Supprimer les activités WIMS"}]

        course_path = self.context.getPhysicalPath()
        my_view["course_map_item_adder"] = self.getCourseItemAdderList(course_link, "%s/%s" % (course_path[-2], course_path[-1]), portal)

        my_view["has_course_map"] = self.context.getPlan()

        my_view["course_news"] = self.context.getActualitesCours()
        my_view["user_last_login_time"] = user.getProperty('login_time', "")
        my_view["item_jalonner"] = self.context.getCourseMapItemJalonner()
        my_view["course_map"] = self.context.getCourseMap(user.getId(), my_view["user_last_login_time"], my_view["is_personnel"], my_view["course_news"]['listeActu'], my_view["item_jalonner"], portal)

        my_view["is_course_map_help_text"] = False
        my_view["course_map_help_text"] = ""
        portal_jalon_properties = portal.portal_jalon_properties
        if portal_jalon_properties.getJalonProperty("activer_aide_plan"):
            my_view["is_course_map_help_text"] = True
            my_view["course_map_help_text"] = portal_jalon_properties.getJalonProperty("lien_aide_plan")

        my_view["course_bibliography_dict"] = self.context.getGloBib('bibliographie')
        my_view["course_bibliography_letter_list"] = my_view["course_bibliography_dict"].keys()
        my_view["course_bibliography_letter_list"].sort()
        my_view["course_has_bibliography"] = len(my_view["course_bibliography_letter_list"])

        my_view["course_glossary_dict"] = self.context.getGloBib('glossaire')
        my_view["course_glossary_letter_list"] = my_view["course_glossary_dict"].keys()
        my_view["course_glossary_letter_list"].sort()
        my_view["course_has_glossary"] = len(my_view["course_glossary_letter_list"])

        my_view["course_to_actions_list"] = self.getActionsList(my_view["is_personnel"], self._course_to_actions_list)
        my_view["course_nominative_registration"] = len(self.context.getGroupe())
        my_view["course_nr_actions_list"] = self.getActionsList(my_view["is_personnel"], self._course_nr_actions_list)
        my_view["course_email_registration"] = len(self.context.getInvitations())
        my_view["course_er_actions_list"] = self.getActionsList(my_view["is_personnel"], self._course_er_actions_list)
        my_view["course_password_registration"] = len(self.context.getInscriptionsLibres())
        my_view["course_pr_actions_list"] = self.getActionsList(my_view["is_personnel"], self._course_pr_actions_list)
        my_view["course_cr_actions_list"] = self.getActionsList(my_view["is_personnel"], self._course_cr_actions_list)

        my_view["course_life_tabs_list"] = [{"tab_link":   "#course_life-historique",
                                             "tab_number": my_view["course_news"]["nbActu"],
                                             "tab_icon":   "fa fa-bell fa-2x",
                                             "tab_name":   "Historique"}]

        my_view["course_news_title"] = "La dernière nouveauté du cours"
        if my_view["course_news"]["nbActu"] >= 4:
            my_view["course_news_title"] = "Les dernières nouveautés du cours"
        else:
            my_view["course_news_title"] = "Les 3 dernières nouveautés du cours"

        my_view["course_advert"] = self.context.getAnnonces(user, self.request, mode_etudiant)
        my_view["course_life_tabs_list"].append({"tab_link":   "#course_life-annonces",
                                                 "tab_number": my_view["course_advert"]["nbAnnonces"],
                                                 "tab_icon":   "fa fa-bullhorn fa-2x",
                                                 "tab_name":   "Annonces"})

        my_view["course_forums"] = self.context.getDicoForums()
        my_view["course_life_tabs_list"].append({"tab_link":   "#course_life-forum",
                                                 "tab_number": my_view["course_forums"]["nbForums"],
                                                 "tab_icon":   "fa fa-comments fa-2x",
                                                 "tab_name":   "Forums"})

        return my_view

    def getCourseItemAdderList(self, course_link, course_path, portal):
        item_adder_list = self.getCourseItemAdderMenuList(course_link, course_path, portal)
        return [{"menu_adder_class":         "button small course-title dropdown",
                 "menu_adder_data-dropdown": "add-title-text",
                 "menu_adder_icon":          "fa fa-paragraph",
                 "menu_adder_name":          "Titre / texte",
                 "menu_adder_items":         [{"item_link": "%s/edit_course_map_item_form?item_type=1" % self.context.absolute_url(),
                                               "item_icon": "fa fa-paragraph fa-fw",
                                               "item_name": "Titre"},
                                              {"item_link": "%s/edit_course_map_item_form?item_type=2" % self.context.absolute_url(),
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

    def getActionsList(self, is_personnel, actions_list):
        tmp_list = actions_list[:]
        if is_personnel:
            del tmp_list[-1]
        else:
            tmp_list = [tmp_list[-1]]
        return tmp_list
