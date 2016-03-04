# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[JalonCourseView]')


class JalonCourseView(BrowserView):
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
        return [{"title": _(u"Mes cours"),
                 "icon":  "fa fa-university",
                 "link":  "%s/mes_cours" % portal.absolute_url()},
                {"title": self.context.Title(),
                 "icon":  "fa fa-book",
                 "link":  self.context.absolute_url()}]

    def getCourseView(self, user, mode_etudiant):
        course_acces = self.context.getAcces()

        return {"is_personnel": self.isPersonnel(user, mode_etudiant),
                "is_public":    "success" if course_acces == "Public" else "disabled"}

    def isPersonnel(self, user, mode_etudiant="false"):
        #self.plone_log("jaloncours/isPersonnel")
        if mode_etudiant == "true":
            #self.plone_log("isPersonnel = False (mode étudiant)")
            return False
        if user.has_role("Manager"):
            #self.plone_log("isPersonnel = True (manager role)")
            return True
        if user.has_role("Personnel") and self.context.isCoAuteurs(user.getId()):
            #self.plone_log("isPersonnel = True (Personnel & iscoAuteurs)")
            return True
        return False
