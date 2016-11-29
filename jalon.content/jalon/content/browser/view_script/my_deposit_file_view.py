# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[MyDepositFileBoxView]')


class MyDepositFileBoxView(BrowserView):
    """Class pour la vue du Cours."""

    def __init__(self, context, request):
        LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getMyDepositFileBoxView(self):
        #LOG.info("----- getMyDepositFileBoxView -----")
        context = self.context

        deposit_comment = context.Description().replace("\n", "<br/>")
        if not deposit_comment:
            deposit_comment = "Aucun commentaire"

        deposit_correction_text = "Aucune correction"
        if context.getCorrectionIndividuelle():
            deposit_correction_text = context.getCorrectionDepot().replace("\n", "<br/>")

        deposit_note = "Aucune note"
        if context.getNotation():
            deposit_note = context.getNote()

        return {"deposit_title":           context.Title(),
                "deposit_comment":         deposit_comment,
                "deposit_correction_text": deposit_correction_text,
                "deposit_note":            deposit_note,
                "deposit_link":            "%s/at_download/file" % context.absolute_url(),
                "deposit_correction_file": context.getFichierCorrection()}