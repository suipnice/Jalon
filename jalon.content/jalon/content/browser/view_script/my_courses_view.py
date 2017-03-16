# -*- coding: utf-8 -*-
"""Scripts de vue pour "Mes cours"."""
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from jalon.content import contentMessageFactory as _
from jalon.content.content import jalon_utils

from logging import getLogger
LOG = getLogger('[MyCoursesView]')


class MyCoursesView(BrowserView):
    """Classe de vue pour la page "Mes cours"."""

    def __init__(self, context, request):
        # LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        # LOG.info("----- isAnonymous -----")
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getBreadcrumbs(self):
        # LOG.info("----- getBreadcrumbs -----")
        return [{"title": _(u"Mes cours"),
                 "icon":  "fa fa-university",
                 "link":  self.context.absolute_url()}]

    def getUserFolder(self, user_id):
        # LOG.info("----- getUserFolder -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        return getattr(portal.cours, user_id)

    def getMyCoursesView(self, user, tab=None):
        # LOG.info("----- getMyCoursesView -----")

        folder = jalon_utils.getCourseUserFolder(self.context, user.getId())
        context_link = self.context.absolute_url()

        is_manager = user.has_role("Manager")
        is_student = user.has_role("Etudiant") or user.has_role("EtudiantJalon")

        macro_messages = "Etudiant"
        if is_manager:
            macro_messages = "Manager"
        if user.has_role("Personnel"):
            macro_messages = "Personnel"

        tabs_list = []
        actions_list = []
        if is_student:
            is_tab_password = True if tab == "2" else False
            my_courses_macro = "my_courses_list_student_macro"
            tab = tab if tab else "1"
            courses_dict = self.getStudentCoursesList(user, tab, folder, is_tab_password)
        else:
            my_courses_macro = "my_courses_list_teacher_macro"
            actions_list = [{"css_class":   "button create expand",
                             "action_link": "%s/create_course_form" % context_link,
                             "action_icon": "fa fa-plus-circle",
                             "action_name": "Créer un cours"},
                            {"css_class":   "button",
                             "action_link": "%s/choose_author_page" % context_link,
                             "action_icon": "fa fa-code-fork",
                             "action_name": "Dupliquer un cours"}]
            if not is_manager:
                del actions_list[-1]

            if "tab" in self.request:
                tab = self.request["tab"]
            if not tab:
                tab = "1" if folder.getComplement() == "True" else "2"
            tabs_list = [{"css_class": "button small selected" if tab == "1" else "button small secondary",
                          "tab_link":  "%s?tab=1" % context_link,
                          "tab_icon":  "fa fa-star fa-fw",
                          "tab_name":  "Favoris"},
                         {"css_class": "button small selected" if tab == "2" else "button small secondary",
                          "tab_link":  "%s?tab=2" % context_link,
                          "tab_icon":  "fa fa-user fa-fw",
                          "tab_name":  "Auteur"},
                         {"css_class": "button small selected" if tab == "3" else "button small secondary",
                          "tab_link":  "%s?tab=3" % context_link,
                          "tab_icon":  "fa fa-users fa-fw",
                          "tab_name":  "Co-auteur"},
                         {"css_class": "button small selected" if tab == "4" else "button small secondary",
                          "tab_link":  "%s?tab=4" % context_link,
                          "tab_icon":  "fa fa-graduation-cap fa-fw",
                          "tab_name":  "Lecteur"},
                         {"css_class": "button small selected" if tab == "5" else "button small secondary",
                          "tab_link":  "%s?tab=5" % context_link,
                          "tab_icon":  "fa fa-folder fa-fw",
                          "tab_name":  "Archives"}]

            courses_dict = self.getTeacherCoursesList(user, tab, folder)

        return {"macro_messages":   macro_messages,
                "my_courses_macro": my_courses_macro,
                "tab":              tab,
                "is_manager":       is_manager,
                "is_student":       is_student,
                "actions_list":     actions_list,
                "tabs_list":        tabs_list,
                "courses_dict":     courses_dict}

    def getTeacherCoursesList(self, member, tab, folder):
        """Renvoi la liste des cours pour l'enseignant member."""
        # LOG.info("----- getTeacherCoursesList -----")
        courses_list = []
        courses_ids_list = []
        courses_list_filter = []
        member_id = member.getId()
        member_login_time = member.getProperty('login_time', None)
        portal_catalog = getToolByName(self, "portal_catalog")

        actions_list = [{"action_link": "/add_favorite_course_form?course_id=",
                         "action_icon": "fa fa-star fa-fw",
                         "action_name": "Ajouter aux favoris"},
                        {"action_link": "/access_statistics_course?course_id=",
                         "action_icon": "fa fa-bar-chart fa-fw",
                         "action_name": "Voir les statistiques"},
                        {"action_link": "/duplicate_course_form?tab=%s&amp;course_id=" % tab,
                         "action_icon": "fa fa-code-fork fa-fw",
                         "action_name": "Dupliquer"},
                        {"action_link": "/add_archive_course_form?tab=%s&amp;course_id=" % tab,
                         "action_icon": "fa fa-folder fa-fw",
                         "action_name": "Archiver ce cours"},
                        {"action_link": "/delete_course_form?tab=%s&amp;course_id=" % tab,
                         "action_icon": "fa fa-trash-o fa-fw",
                         "action_name": "Supprimer ce cours"}]
        """
                        {"action_link": "/purge_course_form?tab=%s&amp;course_id=" % tab,
                         "action_icon": "fa fa-filter fa-fw",
                         "action_name": "Purger les travaux étudiants"},
                        {"action_link": "/delete_wims_activity_form?tab=%s&amp;course_id=" % tab,
                         "action_icon": "fa fa-trash-o fa-fw",
                         "action_name": "Supprimer les activités WIMS"},
        """

        filtre = {"portal_type": "JalonCours"}
        if tab == "1":
            filtre["Subject"] = member_id
            courses_list = list(portal_catalog.searchResults(portal_type="JalonCours", getAuteurPrincipal=member_id, Subject=member_id))
            courses_list.extend(list(portal_catalog.searchResults(
                portal_type="JalonCours", getCoAuteurs=member_id, Subject=member_id)))
            courses_list.extend(list(portal_catalog.searchResults(
                portal_type="JalonCours", getCoLecteurs=member_id, Subject=member_id)))
            courses_list.extend(list(folder.getFolderContents(contentFilter=filtre)))
            actions_list[0] = {"action_link": "/remove_favorite_course_form?course_id=",
                               "action_icon": "fa fa-star-o fa-fw warning",
                               "action_name": "Retirer des favoris"}
            if len(courses_list):
                folder.setComplement("True")
            else:
                folder.setComplement("False")
        if tab == "2":
            courses_list = list(portal_catalog.searchResults(
                portal_type="JalonCours", getAuteurPrincipal=member_id))
            courses_list.extend(list(folder.getFolderContents(contentFilter=filtre)))
        if tab == "3":
            courses_list.extend(
                list(portal_catalog.searchResults(portal_type="JalonCours", getCoAuteurs=member_id)))
            del actions_list[2]
            del actions_list[-1]
        if tab == "4":
            courses_list.extend(
                list(portal_catalog.searchResults(portal_type="JalonCours", getCoLecteurs=member_id)))
            actions_list = [{"action_link": "/display_course_page?course_id=",
                             "action_icon": "fa fa-book fa-fw",
                             "action_name": "Accéder à ce cours"}]
        if tab == "5":
            filtre["getArchive"] = member_id
            courses_list = list(portal_catalog.searchResults(
                portal_type="JalonCours", getAuteurPrincipal=member_id, getArchive=member_id))
            courses_list.extend(list(portal_catalog.searchResults(
                portal_type="JalonCours", getCoAuteurs=member_id, getArchive=member_id)))
            courses_list.extend(list(portal_catalog.searchResults(
                portal_type="JalonCours", getCoLecteurs=member_id, getArchive=member_id)))
            courses_list.extend(list(folder.getFolderContents(contentFilter=filtre)))
            actions_list[-2] = {"action_link": "/remove_archive_course_form?course_id=",
                                "action_icon": "fa fa-folder-open fa-fw warning",
                                "action_name": "Désarchiver ce cours"}

        messages_dict = {"1": "Vous n'avez aucun cours en favoris.",
                         "2": "Vous n'avez pas encore de cours dans Jalon. Pour ajouter un nouveau cours, cliquez sur le bouton « Créer un cours » ci-dessus.",
                         "3": "Vous n'êtes co-auteur d'aucun cours.",
                         "4": "Vous n'êtes lecteur d'aucun cours.",
                         "5": "Vous n'avez aucun cours archivé."}
        if not courses_list:
            return {"is_courses_list": False,
                    "message": messages_dict[tab]}
        authors_dict = {}
        for course_brain in courses_list:
            if course_brain.getId not in courses_ids_list:
                # if tab not in ["1", "5"]:
                if not tab == "5":
                    # if (member_id not in course_brain.Subject) and (member_id not in course_brain.getArchive):
                    if member_id not in course_brain.getArchive:
                        courses_list_filter.append(
                            self.getCourseData(course_brain, authors_dict, member_id, member_login_time, tab, actions_list))
                else:
                    courses_list_filter.append(
                        self.getCourseData(course_brain, authors_dict, member_id, member_login_time, tab, actions_list))
                courses_ids_list.append(course_brain.getId)
        return {"is_courses_list": True if courses_list_filter else False,
                "message": messages_dict[tab],
                "courses_list":    list(courses_list_filter)}

    def getStudentCoursesList(self, member, tab, folder, is_tab_password):
        # LOG.info("----- getStudentCoursesList -----")
        diploma_list = []
        authors_dict = {}
        portal = self.context.portal_url.getPortalObject()
        portal_catalog = portal.portal_catalog
        portal_jalon_bdd = portal.portal_jalon_bdd

        user_id = member.getId()
        member_login_time = member.getProperty('login_time', None)

        course_authorized_list = []
        if tab == "1":
            user_diploma_list = []
            for diploma_data in portal_jalon_bdd.getInscriptionIND(user_id, "etape"):
                user_diploma_list.append(diploma_data["COD_ELP"])

            if not user_diploma_list:
                # pour les nouveaux étudiant qui n'ont pas encore de diplome ou les étudiants invités par email
                courses_list = []
                search_courses_list = list(portal_catalog.searchResults(portal_type="JalonCours", getRechercheAcces=user_id))
                for course_brain in search_courses_list:
                    course_data = self.getCourseData(course_brain, authors_dict, user_id, member_login_time, tab, [])
                    # course_data["course_access"] = ["Invité"]
                    courses_list.append(course_data)
                    course_authorized_list.append(course_data["course_id"])
                diploma_list.append({"diploma_course_list": courses_list})
                self.request.SESSION.set("course_authorized_list", course_authorized_list)
                # LOG.info(course_authorized_list)
                return {"is_diploma_list": True,
                        "diploma_list":    diploma_list}

            # educational_unity_dict = {}
            educational_unity_list = []
            for user_diploma_id in user_diploma_list:
                user_diploma_data = portal_jalon_bdd.getVersionEtape(user_diploma_id)
                if user_diploma_data:
                    # educational_unity_dict["etape*-*%s" % user_diploma_id] = {"type":    "etape",
                    #                                                          "libelle": user_diploma_data[0]}
                    educational_unity_list.append("etape*-*%s" % user_diploma_id)
                    user_educational_registration_list = portal_jalon_bdd.getInscriptionPedago(user_id, user_diploma_id)
                    if not user_educational_registration_list:
                        user_educational_registration_list = portal_jalon_bdd.getUeEtape(user_diploma_id)
                    for user_educational_registration in user_educational_registration_list:
                        ELP = "*-*".join([user_educational_registration["TYP_ELP"], user_educational_registration["COD_ELP"]])
                        # if ELP not in educational_unity_dict:
                        if ELP not in educational_unity_list:
                            # educational_unity_dict[ELP] = {"type":    user_educational_registration["TYP_ELP"],
                            #                               "libelle": user_educational_registration["LIB_ELP"]}
                            educational_unity_list.append(ELP)
                    educational_unity_list.append(user_id)

                    query = {"query":    educational_unity_list,
                             "operator": "or"}
                    course_list = []
                    course_brain_list = list(portal_catalog.searchResults(portal_type="JalonCours", getRechercheAcces=query))
                    for course_brain in course_brain_list:
                        # course_access_list = []
                        course_data = self.getCourseData(course_brain, authors_dict, user_id, member_login_time, tab, [])
                        """
                        for course_access in course_brain.getListeAcces:
                            if course_access in educational_unity_dict:
                                course_access_list.append("%s : %s" % (educational_unity_dict[course_access]['type'], educational_unity_dict[course_access]['libelle']))
                        if user_id in course_brain.getGroupe:
                            course_access_list.append("Invité")
                        try:
                            if user_id in course_brain.getInscriptionsLibres:
                                course_access_list.append("Inscription par mot de passe")
                        except:
                            pass
                        course_data["course_access"] = course_access_list
                        """
                        course_list.append(course_data)
                        course_authorized_list.append(course_data["course_id"])
                        self.request.SESSION.set("course_authorized_list", course_authorized_list)
                    diploma_list.append({"diploma_name":        user_diploma_data[0],
                                         "diploma_course_list": course_list})
        else:
            course_list = []
            course_brain_list = list(portal_catalog.searchResults(portal_type="JalonCours", getCategorieCours=tab))
            for course_brain in course_brain_list:
                course_data = self.getCourseData(course_brain, authors_dict, user_id, member_login_time, tab, [], is_tab_password)
                course_list.append(course_data)
                if tab != "2":
                    course_authorized_list.append(course_data["course_id"])
            diploma_list.append({"diploma_course_list": course_list})

        self.request.SESSION.set("course_authorized_list", course_authorized_list)
        # LOG.info(course_authorized_list)
        if diploma_list:
            return {"is_diploma_list": True,
                    "diploma_list":    diploma_list}
        else:
            return {"is_diploma_list": False,
                    "message":         "Vous n'êtes inscrit(e) à aucun diplôme."}

    def getCourseData(self, course_brain, authors_dict, member_id, member_login_time, tab, actions_list, is_tab_password=False):
        # LOG.info("----- getCourseData -----")
        course_data = {"course_id":                course_brain.getId,
                       "course_title":             course_brain.Title,
                       "course_short_title":       jalon_utils.getShortText(course_brain.Title),
                       "course_short_description": jalon_utils.getPlainShortText(course_brain.Description, 210),
                       "course_creator":           course_brain.Creator,
                       "course_is_nouveau":        "fa fa-bell-o fa-fw no-pad" if cmp(course_brain.getDateDerniereActu, member_login_time) > 0 else "",
                       "course_modified":          course_brain.modified,
                       "course_link":              course_brain.getURL,
                       "course_is_etudiants":      "fa fa-check fa-lg no-pad success" if len(course_brain.getRechercheAcces) > 0 else "fa fa-times fa-lg no-pad warning",
                       "course_is_password":       "fa fa-check fa-lg no-pad success" if course_brain.getLibre else "fa fa-times fa-lg no-pad warning",
                       "course_is_public":         "fa fa-check fa-lg no-pad success" if course_brain.getAcces == "Public" else "fa fa-times fa-lg no-pad warning",
                       "course_actions_list":      actions_list}

        if is_tab_password:
            course_data["course_link"] = "%s/check_course_password_form" % course_data["course_link"]()
        course_author_id = course_brain.getAuteurPrincipal
        if not course_author_id:
            course_author_id = course_brain.Creator
        if course_author_id not in authors_dict:
            authors_dict[course_author_id] = jalon_utils.getIndividu(course_author_id, "dict")["fullname"]

        course_data["course_author_id"] = course_author_id
        course_data["course_author_name"] = authors_dict[course_author_id]

        return course_data
