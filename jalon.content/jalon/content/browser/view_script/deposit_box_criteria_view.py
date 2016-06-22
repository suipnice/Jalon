# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _

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

    def getCriteriaView(self):
        LOG.info("----- getCriteriaView (Start) -----")
        deposit_box = self.context
        #deposit_box_id = deposit_box.getId()
        my_view = {"is_anonymous":     self.isAnonymous(),
                   "deposit_box_link": deposit_box.absolute_url()}

        my_view["criteria_dict"] = deposit_box.getCriteriaDict()
        my_view["criteria_order"] = deposit_box.getCriteriaOrder()
        my_view["comment_dict"] = {"0": "Aucun",
                                   "1": "Optionnel",
                                   "2": "Obligatoire"}
        LOG.info("----- getCriteriaView (End) -----")

        return my_view
