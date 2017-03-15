# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[DepositBoxEvaluationView]')


class DepositBoxEvaluationView(BrowserView):
    """Class pour le first_page
    """

    def __init__(self, context, request):
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
        deposit_box_link = self.context.absolute_url()
        return [{"title": _(u"Mes cours"),
                 "icon":  "fa fa-university",
                 "link":  "%s/mes_cours" % portal.absolute_url()},
                {"title": parent.Title(),
                 "icon":  "fa fa-book",
                 "link":  parent.absolute_url()},
                {"title": self.context.Title(),
                 "icon":  "fa fa-inbox",
                 "link":  "%s?tab=peers" % deposit_box_link},
                {"title": "Mon évaluation",
                 "icon":  "fa fa-trophy",
                 "link":  "%s/deposit_box_evaluation_view" % deposit_box_link}]

    def getStudentEvaluationView(self, student_id):
        # LOG.info("----- getStudentEvaluationView (Start) -----")
        deposit_box = self.context
        deposit_box_id = deposit_box.getId()
        student_name = deposit_box.getIndividu(student_id, "dict")["fullname"]
        #student_infos = deposit_box.getIndividu(student_id, "dict")
        #if student_infos:
        #    student_name = "%s %s" % (student_infos["nom"], student_infos["prenom"])
        #else:
        #    student_name = student_id

        my_view = {"is_anonymous":          self.isAnonymous(),
                   "student_name":          student_name,
                   "acces_evaluations":     deposit_box.getAccesEvaluation(),
                   "acces_self_evaluation": deposit_box.getAutoriserAutoEvaluation(),
                   "has_self_evaluation":   False,
                   "has_evaluation":        True}
        jalon_bdd = self.context.portal_jalon_bdd

        if my_view["acces_self_evaluation"]:
            self_evaluation_note = jalon_bdd.getSelfEvaluationNote(deposit_box_id, student_id).first()
            if self_evaluation_note:
                my_view["has_self_evaluation"] = True
                my_view["self_evaluation_note"] = self_evaluation_note[0]

                my_view["self_evaluation_dict"] = {}
                for line in jalon_bdd.getSelfEvaluate(deposit_box_id, student_id).all():
                    my_view["self_evaluation_dict"][line[0]] = {"criteria_note":    line[1],
                                                                "criteria_comment": line[-1]}

        if my_view["acces_evaluations"]:
            peer_evaluation_list = jalon_bdd.getPeerEvaluation(deposit_box_id, student_id)
            my_view["peer_evaluation"] = {}
            for ligne in peer_evaluation_list.all():
                # LOG.info("***** ligne : %s" % str(ligne))
                try:
                    my_view["peer_evaluation"][ligne[0]].append({"corrected_stu": ligne[1], "criteria_note": ligne[2], "criteria_comment": ligne[-1]})
                except:
                    my_view["peer_evaluation"][ligne[0]] = [{"corrected_stu": ligne[1], "criteria_note": ligne[2], "criteria_comment": ligne[-1]}]
            # LOG.info("***** peer_evaluation : %s" % str(my_view["peer_evaluation"]))

            my_view["peer_average"] = {}
            average_list = jalon_bdd.getPeerAverage(deposit_box_id, student_id)
            for ligne in average_list.all():
                criteria_state = True if ligne[2] != 1 else False
                my_view["peer_average"][ligne[0]] = {"criteria_state": criteria_state, "criteria_note": ligne[1], "criteria_note_t": ligne[-2], "criteria_comment": ligne[-1]}
            # LOG.info("***** peer_average : %s" % str(my_view["peer_average"]))
            try:
                my_view["evaluation_note"] = jalon_bdd.getEvaluationNoteByDeposiSTU(deposit_box_id, student_id).first()[0]
            except:
                my_view["has_evaluation"] = False
                my_view["evaluation_note"] = "Non noté"
        my_view["criteria_dict"] = deposit_box.getCriteriaDict()
        my_view["criteria_order"] = deposit_box.getCriteriaOrder()
        my_view["comment_dict"] = {"0": "Aucun",
                                   "1": "Optionnel",
                                   "2": "Obligatoire"}
        # LOG.info("----- getStudentEvaluationView (End) -----")

        return my_view

    def getDetailsVerificationEvaluations(self, user, mode_etudiant, tab):
        # LOG.info("----- getDetailsVerificationEvaluations -----")
        deposit_box = self.context
        deposit_box_id = deposit_box.getId()

        my_view = {}
        my_view["is_personnel"] = deposit_box.isPersonnel(user, mode_etudiant)
        my_view["mode_etudiant"] = "false" if (not mode_etudiant) and my_view["is_personnel"] else mode_etudiant

        portal = deposit_box.portal_url.getPortalObject()
        parent = deposit_box.aq_parent
        my_view["deposit_box_link"] = deposit_box.absolute_url()
        jalon_bdd = deposit_box.portal_jalon_bdd
        evaluations_notes = jalon_bdd.getCountEvaluationsNotes(deposit_box_id).first()[0]
        evaluations_notes_uncheck = jalon_bdd.getCountVerifEvaluationsNotes(deposit_box_id).first()[0]
        evaluations_notes_check = evaluations_notes - evaluations_notes_uncheck

        if not tab:
            if evaluations_notes_uncheck == 0:
                tab = "2"
            else:
                tab = "1"

        my_view["breadcrumbs"] = [{"title": _(u"Mes cours"),
                                   "icon":  "fa fa-university",
                                   "link":  "%s/mes_cours" % portal.absolute_url()},
                                  {"title": parent.Title(),
                                   "icon":  "fa fa-book",
                                   "link":  parent.absolute_url()},
                                  {"title": deposit_box.Title(),
                                   "icon":  "fa fa-inbox",
                                   "link":  "%s?tab=peers" % my_view["deposit_box_link"]},
                                  {"title": "Évaluations à vérifier",
                                   "icon":  "fa fa-list",
                                   "link":  "%s/deposit_box_details_evaluations_view?tab=%s&amp;mode_etudiant=%s" % (my_view["deposit_box_link"], tab, my_view["mode_etudiant"])}]

        my_view["peers_average_dict"] = {}
        my_view["criteria_dict"] = deposit_box.getCriteriaDict()
        my_view["criteria_order"] = deposit_box.getCriteriaOrder()

        my_view["details_evaluations_tabs"] = []
        my_view["is_uncheck_tab"] = True if tab == "1" else False
        my_view["details_evaluations_tabs"].append({"href":      "%s/deposit_box_details_evaluations_view?tab=1&amp;mode_etudiant=%s" % (my_view["deposit_box_link"], mode_etudiant),
                                                    "css_class": " selected" if my_view["is_uncheck_tab"] else "",
                                                    "icon":      "fa-times",
                                                    "text":      "Évaluations à vérifier",
                                                    "nb":        evaluations_notes_uncheck})
        if my_view["is_uncheck_tab"]:
            check = 2
            my_view["title"] = "Évaluations à vérifier"

        my_view["is_check_tab"] = True if tab == "2" else False
        my_view["details_evaluations_tabs"].append({"href":      "%s/deposit_box_details_evaluations_view?tab=2&amp;mode_etudiant=%s" % (my_view["deposit_box_link"], mode_etudiant),
                                                    "css_class": " selected" if my_view["is_check_tab"] else "",
                                                    "icon":      "fa-check-square-o",
                                                    "text":      "Évaluations correctes",
                                                    "nb":        evaluations_notes_check})
        if my_view["is_check_tab"]:
            check = 1
            my_view["title"] = "Évaluations correctes"

        my_view["is_all_tab"] = True if tab == "3" else False
        my_view["details_evaluations_tabs"].append({"href":      "%s/deposit_box_details_evaluations_view?tab=3&amp;mode_etudiant=%s" % (my_view["deposit_box_link"], mode_etudiant),
                                                    "css_class": " selected" if my_view["is_all_tab"] else "",
                                                    "icon":      "fa-list-ul",
                                                    "text":      "Toutes les évaluations",
                                                    "nb":        evaluations_notes})
        if my_view["is_all_tab"]:
            check = None
            my_view["title"] = "Toutes les évaluations"
            """
            my_view["peers_list"] = deposit_box.getPeersOrder()

            for criteria_note in jalon_bdd.getInfoCriteriaNoteByDepositStu(deposit_box_id).all():
                if not criteria_note[0] in my_view["peers_average_dict"]:
                    my_view["peers_average_dict"][criteria_note[0]] = {criteria_note[1]: {"criteria_note":  criteria_note[2],
                                                                                          "criteria_error": True if criteria_note[3] in [2, 3] else False}}
                else:
                    my_view["peers_average_dict"][criteria_note[0]][criteria_note[1]] = {"criteria_note":  criteria_note[2],
                                                                                         "criteria_error": True if criteria_note[3] in [2, 3] else False}

            for evaluation_note in jalon_bdd.getInfoEvaluationNoteByDepositStu(deposit_box_id).all():
                my_view["peers_average_dict"][evaluation_note[0]]["evaluation_note"] = evaluation_note[1]
                my_view["peers_average_dict"][evaluation_note[0]]["evaluation_error"] = evaluation_note[2]
            """

        evaluations = self.getEvaluations(jalon_bdd, deposit_box, deposit_box_id, check)
        my_view["peers_list"] = evaluations["peers_list"]
        my_view["peers_average_dict"] = evaluations["peers_average_dict"]
        return my_view

    def getEvaluations(self, jalon_bdd, deposit_box, deposit_box_id, check=None):
        peers_list = []
        peers_average_dict = {}
        infos_peers = deposit_box.getInfosPeersDict()

        for evaluation_note in jalon_bdd.getInfoEvaluationNoteByDepositStu(deposit_box_id, check).all():
            peers_average_dict[evaluation_note[0]] = {"evaluation_note":  evaluation_note[1],
                                                      "evaluation_error": evaluation_note[2]}
            peers_list.append({"id":  evaluation_note[0],
                               "nom": infos_peers[evaluation_note[0]]})

        for criteria_note in jalon_bdd.getInfoCriteriaNoteByDepositStu(deposit_box_id).all():
            if criteria_note[0] in peers_average_dict:
                peers_average_dict[criteria_note[0]][criteria_note[1]] = {"criteria_note":  criteria_note[2],
                                                                          "criteria_error": True if criteria_note[3] in [2, 3] else False}

        peers_list.sort(lambda x, y: cmp(x["nom"], y["nom"]))
        return {"peers_list":         peers_list,
                "peers_average_dict": peers_average_dict}
