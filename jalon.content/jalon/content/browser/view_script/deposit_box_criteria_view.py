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
                {"title": "Grille d'évaluation",
                 "icon":  "fa fa-th",
                 "link":  "%s/deposit_box_criteria_view" % deposit_box_link}]

    def getCriteriaView(self, user, mode_etudiant):
        # LOG.info("----- getCriteriaView (Start) -----")
        deposit_box = self.context
        is_personnel = self.context.isPersonnel(user, mode_etudiant)
        mode_etudiant = "false" if (not mode_etudiant) and is_personnel else mode_etudiant
        is_grid_access = True if deposit_box.getAccesGrille() or is_personnel else False
        my_view = {"is_anonymous":        self.isAnonymous(),
                   "deposit_box_link":    deposit_box.absolute_url(),
                   "is_depot_actif":      True,
                   "is_correction_actif": True,
                   "is_personnel":        is_personnel,
                   "mode_etudiant":       mode_etudiant,
                   "is_grid_access":      is_grid_access}

        my_view["criteria_dict"] = deposit_box.getCriteriaDict()
        my_view["criteria_order"] = deposit_box.getCriteriaOrder()
        my_view["comment_dict"] = {"0": "Aucun",
                                   "1": "Optionnel",
                                   "2": "Obligatoire"}

        my_view["is_authorized_deposit"] = deposit_box.isDepotActif()
        if my_view["is_authorized_deposit"] == 3:
            my_view["is_authorized_deposit"] = 0
            my_view["is_authorized_deposit_text"] = "Dans le profil évaluation par les pairs les \"dates limite de dépôts et d'évaluation\" sont obligatoires."
        else:
            now = DateTime(DateTime()).strftime("%Y/%m/%d %H:%M")
            date_depot = DateTime(deposit_box.getDateDepot()).strftime("%Y/%m/%d %H:%M")
            if now >= date_depot:
                my_view["is_depot_actif"] = False
            date_correction = DateTime(deposit_box.getDateCorrection()).strftime("%Y/%m/%d %H:%M")
            if now >= date_correction:
                my_view["is_correction_actif"] = False
        # LOG.info("----- getCriteriaView (End) -----")

        return my_view
