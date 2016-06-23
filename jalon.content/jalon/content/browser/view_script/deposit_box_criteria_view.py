# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _
from DateTime import DateTime

from logging import getLogger
LOG = getLogger('[DepositBoxCriteriaView]')


class DepositBoxCriteriaView(BrowserView):
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

    def getCriteriaView(self, user, mode_etudiant):
        LOG.info("----- getCriteriaView (Start) -----")
        deposit_box = self.context
        is_personnel = self.context.isPersonnel(user, mode_etudiant)
        mode_etudiant = "false" if (not mode_etudiant) and is_personnel else mode_etudiant
        my_view = {"is_anonymous":        self.isAnonymous(),
                   "deposit_box_link":    deposit_box.absolute_url(),
                   "is_depot_actif":      True,
                   "is_correction_actif": True,
                   "is_personnel":        is_personnel,
                   "mode_etudiant":       mode_etudiant}

        my_view["criteria_dict"] = deposit_box.getCriteriaDict()
        my_view["criteria_order"] = deposit_box.getCriteriaOrder()
        my_view["comment_dict"] = {"0": "Aucun",
                                   "1": "Optionnel",
                                   "2": "Obligatoire"}

        now = DateTime(DateTime()).strftime("%Y/%m/%d %H:%M")
        date_depot = DateTime(deposit_box.getDateDepot()).strftime("%Y/%m/%d %H:%M")
        if now >= date_depot:
            my_view["is_depot_actif"] = False
        date_correction = DateTime(deposit_box.getDateCorrection()).strftime("%Y/%m/%d %H:%M")
        if now >= date_correction:
            my_view["is_correction_actif"] = False
        LOG.info("----- getCriteriaView (End) -----")

        return my_view
