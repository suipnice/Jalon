# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[MyDepositFileBoxView]')


class MyDepositFileBoxView(BrowserView):
    """Class pour la vue du Cours."""

    def __init__(self, context, request):
        # LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getMyDepositFileBoxView(self):
        # LOG.info("----- getMyDepositFileBoxView -----")
        context = self.context
        deposit_box = context.aq_parent
        deposit_box_profil = deposit_box.getProfile()

        deposit_comment = "Aucun commentaire"
        if context.Description():
            deposit_comment = context.Description().replace("\n", "<br/>")

        deposit_correction_text = "Aucune correction"
        if context.getCorrectionDepot():
            deposit_correction_text = context.getCorrectionDepot().replace("\n", "<br/>")

        deposit_note = "Aucune note"
        if context.getNote():
            deposit_note = context.getNote()

        return {"deposit_title":           context.Title(),
                "deposit_comment":         deposit_comment,
                "deposit_correction_text": deposit_correction_text,
                "deposit_note":            deposit_note,
                "deposit_link":            "%s/at_download/file" % context.absolute_url(),
                "deposit_correction_file": context.getFichierCorrection(),
                "deposit_download":        True if deposit_box_profil != "examen" else False}
