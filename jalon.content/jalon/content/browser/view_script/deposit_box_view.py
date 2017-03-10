# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from course_view import CourseView
from jalon.content import contentMessageFactory as _

from DateTime import DateTime

from logging import getLogger
LOG = getLogger('[DepositBoxView]')


class DepositBoxView(CourseView):
    """Deposit Box View Class."""

    def __init__(self, context, request):
        """Deposit Box View init."""
        # LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getBreadcrumbs(self):
        portal = self.context.portal_url.getPortalObject()
        parent = self.context.aq_parent
        return [{"title": _(u"Mes cours"),
                 "icon":  "fa fa-university",
                 "link":  "%s/mes_cours" % portal.absolute_url()},
                {"title": parent.Title(),
                 "icon":  "fa fa-book",
                 "link":  parent.absolute_url()},
                {"title": self.context.Title(),
                 "icon":  "fa fa-inbox",
                 "link":  self.context.absolute_url()}]

    def getDepositBoxView(self, user, mode_etudiant, tab, is_ajax):
        # LOG.info("----- getDepositBoxView (Start) -----")
        user_id = user.getId()
        my_view = {"is_anonymous": self.isAnonymous()}

        my_deposit_box = self.context
        instruction_text = my_deposit_box.Description()
        if instruction_text:
            my_view["instruction_class"] = "panel callout radius"
            my_view["instruction_text"] = instruction_text
        else:
            my_view["instruction_class"] = "panel radius"
            my_view["instruction_text"] = "Consigne non renseignée"

        my_view["deposit_box_id"] = my_deposit_box.getId()
        my_view["deposit_box_link"] = my_deposit_box.absolute_url()

        my_view["is_personnel"] = my_deposit_box.isPersonnel(user, mode_etudiant)
        my_view["mode_etudiant"] = "false" if (not mode_etudiant) and my_view["is_personnel"] else mode_etudiant

        if is_ajax or my_view["is_anonymous"]:
            my_view["came_from"] = "%s/login_form?came_from=%s" % (my_view["deposit_box_link"], my_deposit_box.jalon_quote(my_view["deposit_box_link"]))
            return my_view

        # LOG.info("***** DateAff : %s" % my_deposit_box.getDateAff())
        my_view["deposit_box_visibility"] = my_deposit_box.isAfficherElement(my_deposit_box.getDateAff(), my_deposit_box.getDateMasq())

        my_view["deposit_box_edit"] = []
        # LOG.info("***** deposit_box_visibility : %s" % my_view["deposit_box_visibility"])
        if my_view["deposit_box_visibility"]["val"]:
            my_view["deposit_box_edit"].append({"href": "%s/edit_course_item_visibility_form?item_id=%s&amp;tab=%s" % (my_view["deposit_box_link"], my_view["deposit_box_id"], tab),
                                                "icon": "fa-eye-slash",
                                                "text": "Masquer"})
        else:
            my_view["deposit_box_edit"].append({"href": "%s/edit_course_item_visibility_form?item_id=%s&amp;tab=%s" % (my_view["deposit_box_link"], my_view["deposit_box_id"], tab),
                                                "icon": "fa-eye",
                                                "text": "Afficher"})
        my_view["deposit_box_edit"].append({"href": "%s/edit_deposit_box_form?tab=%s" % (my_view["deposit_box_link"], tab),
                                            "icon": "fa-pencil",
                                            "text": "Titre"})

        my_view["deposit_box_deposit_date"] = my_deposit_box.getAffDate('dateDepot')
        my_view["is_authorized_deposit"] = my_deposit_box.isDepotActif()
        if my_view["is_authorized_deposit"] == 2:
            my_view["is_late"] = True
            my_view["class_limit_date"] = "callout"
        else:
            my_view["is_late"] = False
            my_view["class_limit_date"] = "warning"
            if my_view["is_authorized_deposit"] == 3:
                my_view["is_authorized_deposit"] = 0
                my_view["is_authorized_deposit_text"] = "Dans le profil évaluation par les pairs les \"dates limite de dépôts et d'évaluation\" sont obligatoires."

        my_view["grid_access"] = True if my_deposit_box.getAccesGrille(my_view["is_personnel"]) else False
        #my_view["grid_link"] = "%s/deposit_box_criteria_view?mode_etudiant=true" % my_view["deposit_box_link"]

        my_view["deposit_box_tabs"] = []

        my_view["is_documents_tab"] = True if tab == "documents" else False
        my_view["deposit_box_tabs"].append({"href":      "%s?tab=documents&amp;mode_etudiant=%s" % (my_view["deposit_box_link"], mode_etudiant),
                                            "css_class": " selected" if my_view["is_documents_tab"] else "",
                                            "icon":      "fa-upload",
                                            "text":      "Documents enseignants",
                                            "nb":        my_deposit_box.getNbSujets(my_view["is_personnel"])})
        if my_view["is_documents_tab"]:
            portal = my_deposit_box.portal_url.getPortalObject()
            deposit_box_path = my_deposit_box.getPhysicalPath()
            my_view["documents_add"] = self.getCourseItemAdderMenuList(my_view["deposit_box_link"], "/".join([deposit_box_path[-3], deposit_box_path[-2], deposit_box_path[-1]]), portal)["my_space"]
            my_view["documents_list"] = my_deposit_box.displayDocumentsList(my_view["is_personnel"], portal)

        my_view["is_deposit_tab"] = True if tab == "deposit" else False
        my_view["deposit_box_tabs"].append({"href":      "%s?tab=deposit&amp;mode_etudiant=%s" % (my_view["deposit_box_link"], mode_etudiant),
                                            "css_class": " selected" if my_view["is_deposit_tab"] else "",
                                            "icon":      "fa-download",
                                            "text":      "Mes dépôts" if not my_view["is_personnel"] and not my_deposit_box.getAccesDepots() else "Dépôts étudiants",
                                            "nb":        my_deposit_box.getNbDepots(my_view["is_personnel"], user_id)})
        my_view["deposit_tab_options"] = []
        if my_view["is_deposit_tab"]:
            my_view["deposit_tab_options_link"] = "%s/edit_deposit_tab_form" % my_view["deposit_box_link"]
            my_view["deposit_tab_options"] = [{"icon": "fa-toggle-on success" if my_deposit_box.getCorrectionIndividuelle() else "fa-toggle-off",
                                               "text": "Correction des dépôts"},
                                              {"icon": "fa-toggle-on success" if my_deposit_box.getNotificationCorrection() else "fa-toggle-off",
                                               "text": "Notification des corrections"},
                                              {"icon": "fa-toggle-on success" if my_deposit_box.getNotation() else "fa-toggle-off",
                                               "text": "Notation des dépôts"},
                                              {"icon": "fa-toggle-on success" if my_deposit_box.getNotificationNotation() else "fa-toggle-off",
                                               "text": "Notification des notations"},
                                              {"icon": "fa-toggle-on success" if my_deposit_box.getAccesDepots() else "fa-toggle-off",
                                               "text": "Visualisation des dépôts entre étudiants"}]

        deposit_box_profile = my_deposit_box.getProfile() or "standard"

        my_view["is_skills_tab"] = True if tab == "skills" else False
        if (my_view["is_personnel"] and deposit_box_profile == "competences") or my_deposit_box.getAfficherCompetences():
            my_view["deposit_box_tabs"].append({"href":      "%s?tab=skills&amp;mode_etudiant=%s" % (my_view["deposit_box_link"], mode_etudiant),
                                                "css_class": " selected" if my_view["is_skills_tab"] else "",
                                                "icon":      "fa-tasks",
                                                "text":      "Compétences",
                                                "nb":        my_deposit_box.getNbCompetences()})
        if my_view["is_skills_tab"]:
            my_view["skills_macro"] = "skills_teacher" if my_view["is_personnel"] else "skills_student"
            my_view["deposit_tab_options_link"] = "%s/edit_deposit_box_skills_options_form" % my_view["deposit_box_link"]
            my_view["deposit_tab_options"] = [{"icon": "fa-toggle-on success" if my_deposit_box.getAfficherCompetences() else "fa-toggle-off",
                                               "text": "Affichage de l'onglet \"Compétences\" aux étudiants"}]
            if my_deposit_box.getPermissionModifierCompetence(my_view["is_personnel"], user_id):
                my_view["deposit_tab_options"].append({"icon": "fa-toggle-on success" if my_deposit_box.getModifierCompetences() else "fa-toggle-off",
                                                       "text": "Restriction de la gestion des compétences"})

        my_view["deposit_peer_options"] = []
        my_view["is_peers_tab"] = True if tab == "peers" else False
        if deposit_box_profile == "pairs":
            my_view["deposit_box_tabs"].append({"href":      "%s?tab=peers&amp;mode_etudiant=%s" % (my_view["deposit_box_link"], mode_etudiant),
                                                "css_class": " selected" if my_view["is_peers_tab"] else "",
                                                "icon":      "fa-users",
                                                "text":      "Dépôts à évaluer" if not my_view["is_personnel"] else "Par les pairs",
                                                "nb":        my_deposit_box.getPeerLength(my_view["is_personnel"], user_id)})
        if my_view["is_peers_tab"]:
            my_view["accessEvaluation"] = not my_view["is_personnel"] and my_deposit_box.getAccesEvaluation()
            my_view["accessSelfEvaluation"] = not my_view["is_personnel"] and my_deposit_box.getAutoriserAutoEvaluation()
            my_view["deposit_tab_options_link"] = ""
            my_view["deposit_peer_options"] = [{"link":  "%s/edit_peers_correction_number_form" % my_view["deposit_box_link"],
                                                "class": "panel callout radius",
                                                "icon":  "fa fa-users fa-fw no-pad",
                                                "text":  "Évaluation(s) par étudiants",
                                                "value": my_deposit_box.getNombreCorrection()},
                                               {"link":  "%s/edit_peers_adjustment_form" % my_view["deposit_box_link"],
                                                "class": "panel callout radius",
                                                "icon":  "fa fa-balance-scale fa-fw no-pad",
                                                "text":  "Ajustement",
                                                "value": my_deposit_box.getDisplayPenality()},
                                               {"link":  "%s/edit_peers_grid_access_form" % my_view["deposit_box_link"],
                                                "class": "panel callout radius",
                                                "icon":  "fa fa-th fa-fw no-pad",
                                                "text":  "Accès à la grille d'évaluation",
                                                "value": my_deposit_box.getDisplayGridAccess()},
                                               {"link":  "%s/edit_peers_self_evaluation_form" % my_view["deposit_box_link"],
                                                "class": "panel callout radius",
                                                "icon":  "fa fa-user fa-fw no-pad",
                                                "text":  "Autoriser l'auto-évaluation",
                                                "value": my_deposit_box.getDisplayAuthorizeSelfEvaluation()}]
            my_view["is_depot_actif"] = True
            my_view["is_correction_actif"] = True
            if my_view["is_authorized_deposit"] != 3:
                now = DateTime(DateTime()).strftime("%Y/%m/%d %H:%M")
                date_depot = DateTime(my_deposit_box.getDateDepot()).strftime("%Y/%m/%d %H:%M")
                if now >= date_depot:
                    my_view["is_depot_actif"] = False
                date_correction = DateTime(my_deposit_box.getDateCorrection()).strftime("%Y/%m/%d %H:%M")
                if now >= date_correction:
                    my_view["is_correction_actif"] = False

            if my_view["accessSelfEvaluation"]:
                self_evaluation_note = my_deposit_box.portal_jalon_bdd.getSelfEvaluationNote(my_view["deposit_box_id"], user_id).first()
                if self_evaluation_note:
                    my_view["self_evalution_button"] = "fa fa-trophy"
                    my_view["self_evalution_link"] = "%s/deposit_box_evaluation_view" % my_view["deposit_box_link"]
                    my_view["self_evalution_name"] = "Consulter mon auto-évaluation"
                else:
                    my_view["self_evalution_button"] = "fa fa-user"
                    my_view["self_evalution_link"] = "%s/evaluate_deposit_file_form?deposit_id=auto" % my_view["deposit_box_link"]
                    my_view["self_evalution_name"] = "Réaliser mon auto-évaluation"

        my_view["deposit_box_profile"] = {"href":  "%s/edit_deposit_box_profile_form?tab=%s" % (my_view["deposit_box_link"], tab),
                                          "icon": "fa-pencil",
                                          "text": "Profil"}
        my_view["deposit_box_profile_text"] = my_deposit_box.getDisplayProfile()
        my_view["deposit_box_date"] = {"href":  "%s/edit_deposit_box_date_form?tab=%s" % (my_view["deposit_box_link"], tab),
                                       "icon": "fa-pencil",
                                       "text": "Modifier"}
        my_view["is_peer_profile"] = False
        if my_deposit_box.getProfile() == "pairs":
            my_view["is_peer_profile"] = True
            my_view["deposit_box_correction_date"] = {"link":  "%s/edit_peers_correction_date_form?tab=%s" % (my_view["deposit_box_link"], tab),
                                                      "class": "panel warning radius",
                                                      "icon":  "fa fa-pencil fa-fw no-pad",
                                                      "text":  "Date limite d'évaluation",
                                                      "value": my_deposit_box.getAffDate('dateCorrection')}

        my_view["deposit_box_instruction"] = {"href":  "%s/edit_deposit_box_instruction_form?tab=%s" % (my_view["deposit_box_link"], tab),
                                              "icon":  "fa-pencil",
                                              "text":  "Modifier"}

        my_view["is_personnel_or_deposit_box_visible"] = True if my_view["is_personnel"] or my_view["deposit_box_visibility"]['val'] != 0 else False
        # LOG.info("***** is_personnel : %s" % my_view["is_personnel"])
        # LOG.info("***** affElement : %s" % my_view["deposit_box_visibility"]['val'])
        my_view["is_student_and_deposit_box_hidden"] = True if (not my_view["is_personnel"]) and my_view["deposit_box_visibility"]['val'] == 0 else False
        my_view["is_display_mod"] = my_deposit_box.isAuteurs(user.getId())
        # LOG.info("----- getDepositBoxView (End) -----")
        return my_view
