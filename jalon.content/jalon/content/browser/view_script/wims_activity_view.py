# -*- coding: utf-8 -*-
"""WimsActivityView python Class."""
# from Products.Five.browser import BrowserView
# from zope.component import getMultiAdapter
from course_view import CourseView
from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[WimsActivityView]')


class WimsActivityView(CourseView):
    """Wims Activity View Class."""

    """def __init__(self, context, request):
        # initialize WimsActivityView.
        # LOG.info("----- Init -----")
        CourseView.__init__(self, context, request)
    """

    def getBreadcrumbs(self):
        """Get current page breadcrumbs."""
        # LOG.info("----- getBreadcrumbs -----")
        portal = self.context.portal_url.getPortalObject()
        parent = self.context.aq_parent
        self_link = self.context.absolute_url()
        response = [{"title": _(u"Mes cours"),
                     "icon":  "fa fa-university",
                     "link":  "%s/mes_cours" % portal.absolute_url()},
                    {"title": parent.Title(),
                     "icon":  "fa fa-book",
                     "link":  parent.absolute_url()},
                    {"title": self.context.Title(),
                     "icon":  self.context.getIconClass(),
                     "link":  self_link}]
        if self.request.ACTUAL_URL.split("/")[-1] == "wims_activity_exercice_view":
            response.append({"title": _("Exercice(s)"), "icon":  "fa fa-random", "link": "%s/wims_activity_exercice_view" % self_link})
        return response

    def getWimsActivityView(self, user, mode_etudiant, tab, is_ajax):
        """Get Wims Activity View."""
        # LOG.info("----- getWimsActivityView (Start) tab='%s' -----" % tab)
        user_id = user.getId()
        my_view = {"is_anonymous": self.isAnonymous()}

        if tab not in ["exercices", "documents", "results"]:
            tab = "exercices"
        my_view["tab"] = tab

        my_wims_activity = self.context
        portal = my_wims_activity.portal_url.getPortalObject()
        portal_link = portal.absolute_url()
        nb_exos = my_wims_activity.getNbExercices()
        instruction_text = my_wims_activity.Description()
        if instruction_text:
            my_view["instruction_class"] = "panel callout radius"
            my_view["instruction_text"] = instruction_text
        else:
            my_view["instruction_class"] = "panel radius"
            my_view["instruction_text"] = "Consigne non renseignée"

        my_view["activity_id"] = my_wims_activity.getId()
        my_view["activity_link"] = my_wims_activity.absolute_url()
        my_view["activity_type"] = my_wims_activity.getTypeWims()

        if my_view["activity_type"] == "Examen":
            my_view["activity_link_title"] = "Accéder à cet examen WIMS"
        else:
            my_view["activity_link_title"] = "Accéder à cet entrainement WIMS"

        my_view["activity_icon"] = my_wims_activity.getIconClass()
        my_view["duree"] = my_wims_activity.getDuree()

        my_view["is_personnel"] = my_wims_activity.isPersonnel(user, mode_etudiant)

        if (not mode_etudiant) and my_view["is_personnel"]:
            my_view["mode_etudiant"] = "false"
        else:
            my_view["mode_etudiant"] = mode_etudiant

        if is_ajax or my_view["is_anonymous"]:
            my_view["came_from"] = "%s/acl_users/credentials_cookie_auth/require_login?came_from=%s" % (portal_link, my_wims_activity.jalon_quote(my_view["activity_link"]))
            # my_view["came_from"] = "%s/login_form?came_from=%s" % (my_view["activity_link"], my_wims_activity.jalon_quote(my_view["activity_link"]))
            # LOG.info("----- getWimsActivityView (Early Ended : ajax or anonymous) -----")
            return my_view

        # my_view["wims_activity_instruction"] = {"href":  "%s/edit_wims_activity_instruction_form?tab=%s" % (my_view["activity_link"], tab),
        #                                        "icon":  "fa-pencil",
        #                                        "text":  "Modifier"}

        my_view["wims_activity_visibility"] = my_wims_activity.isAfficherElement(my_wims_activity.getDateAff(), my_wims_activity.getDateMasq())

        my_view["wims_activity_edit"] = []
        if my_view["wims_activity_visibility"]["val"]:
            my_view["wims_activity_edit"].append({"href": "%s/edit_course_item_visibility_form?item_id=%s&tab=%s" % (my_view["activity_link"], my_view["activity_id"], tab),
                                                  "icon": "fa-eye-slash",
                                                  "text": "Masquer"})
        else:
            my_view["wims_activity_edit"].append({"href": "%s/edit_course_item_visibility_form?item_id=%s&tab=%s" % (my_view["activity_link"], my_view["activity_id"], tab),
                                                  "icon": "fa-eye",
                                                  "text": "Afficher"})
            if my_view["activity_type"] == "Examen" and nb_exos > 0:
                my_view["wims_activity_edit"].append({"href": "%s/wims_activity_exercice_view" % my_view["activity_link"],
                                                      "icon": "fa-laptop",
                                                      "text": "Tester les exercices"})
        my_view["wims_activity_edit"].append({"href": "%s/edit_wims_activity_form?tab=%s" % (my_view["activity_link"], tab),
                                              "icon": "fa-pencil",
                                              "text": "Modifier"})

        my_view["is_personnel_or_wims_activity_visible"] = True if my_view["is_personnel"] or my_view["wims_activity_visibility"]['val'] != 0 else False
        my_view["is_student_and_wims_activity_hidden"] = True if (not my_view["is_personnel"]) and my_view["wims_activity_visibility"]['val'] == 0 else False
        my_view["is_display_mod"] = my_wims_activity.isAuteurs(user_id)

        my_view["wims_activity_tabs"] = []

        my_view["wims_activity_tabs"].append({"href":      "%s?tab=exercices&mode_etudiant=%s" % (my_view["activity_link"], mode_etudiant),
                                              "css_class": " selected" if tab == "exercices" else "",
                                              "icon":      "fa-random",
                                              "text":      "Exercices",
                                              "nb":        my_wims_activity.getNbExercices()})
        activity_path = my_wims_activity.getPhysicalPath()
        activity_path = "/".join([activity_path[-3], activity_path[-2], activity_path[-1]])

        # Boutons d'ajouts d'exercices, affichés uniquement pour le créateur d'une activité masquée et qui n'est pas un examen déjà activé
        if (tab == "exercices" and
                my_view['is_personnel'] and
                not my_view['wims_activity_visibility']['val'] and
                not my_wims_activity.getIdExam() and
                my_wims_activity.getCreateur() == user_id):
            my_view["id_groupement"] = my_wims_activity.getGroupement()
            my_view["exercices_add"] = self.getExerciceAdderMenuList(portal_link, activity_path)
            # my_view["exercices_list"] = my_wims_activity.displayDocumentsList(my_view["is_personnel"], portal)

        my_view["wims_activity_tabs"].append({"href":      "%s?tab=documents&mode_etudiant=%s" % (my_view["activity_link"], mode_etudiant),
                                              "css_class": " selected" if tab == "documents" else "",
                                              "icon":      "fa-upload",
                                              "text":      "Documents enseignants",
                                              "nb":        my_wims_activity.getNbSujets(my_view["is_personnel"])})
        if tab == "documents":
            my_view["documents_add"] = self.getCourseItemAdderMenuList(my_view["activity_link"], activity_path, portal)["my_space"]
            my_view["documents_list"] = my_wims_activity.displayDocumentsList(my_view["is_personnel"], portal)

        # my_view["is_resultats_tab"] = True if tab == "results" else False
        if my_view["is_personnel"]:
            my_view["wims_activity_tabs"].append({"href":      "%s?tab=results&mode_etudiant=%s" % (my_view["activity_link"], mode_etudiant),
                                                  "css_class": " selected" if tab == "results" else "",
                                                  "icon":      "fa-trophy",
                                                  "text":      "Résultats"})

        # LOG.info("----- getWimsActivityView (End) -----")
        return my_view

    def getWimsSession(self, user, isCoAuteur, isAnonymous):
        """Obtain a new or existing session from WIMS, and returns wims params."""
        if isAnonymous:
            message = _(u"Désolé, seul un utilisateur connecté peux participer aux activités d'un cours.")
            # message = _(u"Le coefficient de l'exercice '${item_title}' a bien été modifié.",
            #            mapping={'item_title': param["title"]})
            self.context.plone_utils.addPortalMessage(message, type='warning')
            return None
        elif isCoAuteur:
            user_id = 'supervisor'
        elif not isAnonymous:
            user_id = user.getId()
        return self.context.authUser(user_id, self.context.getClasse(), self.request, session_keep=True)

    def getExerciceAdderMenuList(self, portal_link, activity_path):
        """Fournit la liste des liens permettant d'ajouter des exercices à une activité WIMS."""
        # portal_link = portal.absolute_url()
        # portal_link = self.portal_url
        item_adder_list = [{"item_link":  "%s/mes_ressources/mes_exercices_wims/course_add_view?course_path=%s" % (portal_link, activity_path),
                                "item_title": "Attacher un exercice WIMS de Mes ressources",
                                "item_icon":  "fa fa-fw fa-random",
                                "item_name":  "Exercice WIMS"},
                           {"item_link":  "%s/cours/%s/import_wims_activity_form?type=hotpot" % (portal_link, activity_path),
                                "item_title": "Importer des exercices",
                                "item_icon":  "fa fa-fw fa-level-down",
                                "item_name":  "Import HotPotatoes"}]

        return item_adder_list
