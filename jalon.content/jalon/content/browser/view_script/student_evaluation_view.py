# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[StudentEvaluationView]')


class StudentEvaluationView(BrowserView):
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

    def getStudentEvaluationView(self, student_id):
        LOG.info("----- getDepositBoxView (Start) -----")
        deposit_box = self.context
        deposit_box_id = deposit_box.getId()
        my_view = {"is_anonymous": self.isAnonymous()}
        jalon_bdd = self.context.portal_jalon_bdd
        peer_evaluation_list = jalon_bdd.getPeerEvaluation(deposit_box_id, student_id)
        my_view["peer_evaluation"] = {}
        for ligne in peer_evaluation_list.all():
            LOG.info("***** ligne : %s" % str(ligne))
            try:
                my_view["peer_evaluation"][ligne[0]].append({"corrected_stu": ligne[1], "criteria_note": ligne[2], "criteria_comment": ligne[-1]})
            except:
                my_view["peer_evaluation"][ligne[0]] = [{"corrected_stu": ligne[1], "criteria_note": ligne[2], "criteria_comment": ligne[-1]}]
        LOG.info("***** peer_evaluation : %s" % str(my_view["peer_evaluation"]))

        my_view["peer_average"] = {}
        average_list = jalon_bdd.getPeerAverage(deposit_box_id, student_id)
        for ligne in average_list.all():
            criteria_note = ligne[2] if ligne[1] else ligne[3]
            try:
                my_view["peer_average"][ligne[0]] = {"criteria_state": ligne[1], "criteria_note": criteria_note, "criteria_comment": ligne[-1]}
            except:
                my_view["peer_average"] = {ligne[0]: {"criteria_state": ligne[1], "criteria_note": criteria_note, "criteria_comment": ligne[-1]}}

        my_view["criteria_dict"] = deposit_box.getCriteriaDict()
        my_view["criteria_order"] = deposit_box.getCriteriaOrder()

        return my_view
