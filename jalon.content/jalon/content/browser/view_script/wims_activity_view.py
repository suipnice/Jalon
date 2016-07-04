# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from course_view import CourseView
from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[WimsActivityView]')


class WimsActivityView(CourseView):
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

    def getWimsActivityView(self, user, mode_etudiant, tab, is_ajax):
        LOG.info("----- getWimsActivityView (Start) -----")
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
        my_view["wims_activity_link"] = my_deposit_box.absolute_url()
        my_view["is_personnel"] = my_deposit_box.isPersonnel(user, mode_etudiant)
        my_view["mode_etudiant"] = "false" if (not mode_etudiant) and my_view["is_personnel"] else mode_etudiant
        LOG.info("----- getWimsActivityView (End) -----")
        return my_view
