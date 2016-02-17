# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from jalon.content.content import jalon_utils

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

        folder = jalon_utils.getCourseUserFolder(self.context, user.getId())
        folder_link = folder.absolute_url()
        context_link = self.context.absolute_url()

        is_manager = user.has_role("Manager")
        is_student = user.has_role("Etudiant") or user.has_role("EtudiantJalon")

        actions_list = [{"css_class":   "button create expand",
                         "action_link": "%s/create_course_form" % folder_link,
                         "action_icon": "fa fa-plus-circle",
                         "action_name": "Créer un cours"},
                        {"css_class":   "button",
                         "action_link": "%s/lister_auteur" % context_link,
                         "action_icon": "fa fa-code-fork",
                         "action_name": "Dupliquer un cours"}]
        if not is_manager:
            del actions_list[-1]

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

        courses_list = self.getTeacherCoursesList(user, tab, folder)
        return {"tab":          tab,
                "is_manager":   is_manager,
                "is_student":   is_student,
                "actions_list": actions_list,
                "tabs_list":    tabs_list,
                "courses_list": courses_list}

    def getTeacherCoursesList(self, member, tab, folder):
        LOG.info("----- getListeCoursEns -----")
        """ Renvoi la liste des cours pour authMember."""
        courses_list = []
        courses_ids_list = []
        courses_list_filter = []
        member_id = member.getId()
        member_login_time = member.getProperty('login_time', None)
        portal_catalog = getToolByName(self, "portal_catalog")

        actions_list = [{"action_link": "/add_favorite_course_form?course_id=",
                         "action_icon": "fa fa-star fa-fw",
                         "action_name": "Ajouter aux favoris"},
                        {"action_link": "/duplicate_course_form?course_id=",
                         "action_icon": "fa fa-code-fork fa-fw",
                         "action_name": "Dupliquer"},
                        {"action_link": "/purge_course_form?tab=%s&amp;course_id=" % tab,
                         "action_icon": "fa fa-filter fa-fw",
                         "action_name": "Purger les travaux étudiants"},
                        {"action_link": "/delete_wims_activity_form?tab=%s&amp;course_id=" % tab,
                         "action_icon": "fa fa-trash-o fa-fw",
                         "action_name": "Supprimer les activités WIMS"},
                        {"action_link": "/add_archive_course_form?course_id=",
                         "action_icon": "fa fa-folder fa-fw",
                         "action_name": "Archiver ce cours"},
                        {"action_link": "/delete_course_form?tab=%s&amp;course_id=" % tab,
                         "action_icon": "fa fa-trash-o fa-fw",
                         "action_name": "Supprimer ce cours"}]

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
            del actions_list[1]
            del actions_list[-1]
        if tab == "4":
            courses_list.extend(
                list(portal_catalog.searchResults(portal_type="JalonCours", getCoLecteurs=member_id)))
            del actions_list[1]
            del actions_list[1]
            del actions_list[1]
            del actions_list[-1]
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
                         "2": "Vous n'avez pas encore de cours dans Jalon. Pour ajouter un nouveau cours, cliquez sur la barre « Créer un cours » ci-dessus.",
                         "3": "Vous n'êtes co-auteur d'aucun cours.",
                         "4": "Vous n'êtes lecteur d'aucun cours.",
                         "5": "Vous n'avez aucun cours en archives."}
        if not courses_list:
            return {"is_courses_list": False,
                    "message": messages_dict[tab]}
        authors_dict = {}
        for course_brain in courses_list:
            if not course_brain.getId in courses_ids_list:
                if not tab in ["1", "5"]:
                    if (not member_id in course_brain.Subject) and (not member_id in course_brain.getArchive):
                        courses_list_filter.append(
                            self.getCourseData(course_brain, authors_dict, member_id, member_login_time, tab, actions_list))
                else:
                    courses_list_filter.append(
                        self.getCourseData(course_brain, authors_dict, member_id, member_login_time, tab, actions_list))
                courses_ids_list.append(course_brain.getId)
        return {"is_courses_list": True,
                "courses_list":    list(courses_list_filter)}

    def getCourseData(self, course_brain, authors_dict, member_id, member_login_time, tab, actions_list):
        LOG.info("----- getCourseData -----")

        course_infos = {"course_id":                course_brain.getId,
                        "course_title":             course_brain.Title,
                        "course_short_title":       jalon_utils.getShortText(course_brain.Title),
                        "course_short_description": jalon_utils.getPlainShortText(course_brain.Description, 210),
                        "course_is_nouveau":        "fa fa-bell-o fa-fw no-pad" if cmp(course_brain.getDateDerniereActu, member_login_time) > 0 else "",
                        "course_modified":          course_brain.modified,
                        "course_link":              course_brain.getURL,
                        "course_is_etudiants":      "fa fa-check fa-lg no-pad success" if len(course_brain.getRechercheAcces) > 0 else "fa fa-times fa-lg no-pad warning",
                        "course_is_password":       "fa fa-check fa-lg no-pad success" if course_brain.getLibre else "fa fa-times fa-lg no-pad warning",
                        "course_is_public":         "fa fa-check fa-lg no-pad success" if course_brain.getAcces == "Public" else "fa fa-times fa-lg no-pad warning",
                        "course_actions_list":      actions_list}
        if tab != "2":
            course_author = course_brain.getAuteurPrincipal
            if not course_author:
                course_author = course_brain.Creator
            if course_author in authors_dict:
                course_infos["course_author_name"] = authors_dict[course_author]
            else:
                course_author_name = jalon_utils.getInfosMembre(course_author)["fullname"]
                authors_dict[course_author] = course_author_name
                course_infos["course_author_name"] = course_author_name

        return course_infos
