# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

from jalon.content.content import jalon_utils


class MonEspaceView(BrowserView):
    """Class pour le first_page
    """

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()
