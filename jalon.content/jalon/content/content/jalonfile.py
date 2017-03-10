# -*- coding: utf-8 -*-

from zope.interface import implements
from plone.app.blob.field import BlobField
from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.utils import getToolByName

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonFile

import jalon_utils

from logging import getLogger
LOG = getLogger('[JalonFile]')

JalonFileSchema = ATDocumentSchema.copy() + atpublic.Schema((
    BlobField('file',
              widget=atpublic.FileWidget(label='A file',
                                         description='Some file'),
              required=True,
              ),
    atpublic.StringField("actif",
                         required=False,
                         accessor="getActif",
                         searchable=False,
                         default="actif",
                         widget=atpublic.StringWidget(label=_(u"Actif"),)),
    atpublic.TextField("correction",
                       required=True,
                       accessor="getCorrection",
                       searchable=False,
                       widget=atpublic.TextAreaWidget(label=_(u"Correction"),)),
    atpublic.StringField("note",
                         required=False,
                         accessor="getNote",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Note ou appréciation"),)),
))


class JalonFile(ATDocumentBase):
    """ Un fichier pour une boite de dépot d'un cours Jalon
    """

    implements(IJalonFile)
    meta_type = 'JalonFile'
    schema = JalonFileSchema
    schema['description'].required = False
    schema['description'].widget.label = "Commentaire"
    schema['description'].widget.description = ""
    schema['text'].required = False
    schema['text'].mode = "r"

    def setProperties(self, dico):
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        self.reindexObject()

    def getAuteur(self):
        return jalon_utils.getIndividu(self.Creator(), "dict")["fullname"]

    def isNotStandard(self):
        # LOG.info("----- isNotStandard -----")
        return self.aq_parent.isNotStandard()

    def getCorrectionDepot(self):
        return str(self.correction)

    def getFichierCorrection(self):
        corrections = getattr(self.aq_parent, "corrections", None)
        if corrections:
            fichier_correction = getattr(corrections, "Correction_%s" % self.getId(), None)
            if fichier_correction:
                return "%s/at_download/file" % fichier_correction.absolute_url()
        return None

    def getSize(self):
        return self.file.get_size()

    def notifierCorrection(self, correction=False, note=False):
        LOG.info("----- notifierCorrection START -----")
        boite = self.aq_parent
        cours = boite.aq_parent
        #if not boite.getNotificationCorrection() and not boite.getNotificationNotation():
        #    LOG.info("Notification correction et notation désactivée")
        #    return None

        is_notifier_correction = True if correction and boite.getNotificationCorrection() else False
        is_notifier_note = True if note and boite.getNotificationNotation() else False

        if is_notifier_correction and is_notifier_note:
            LOG.info("Envoyer mail Correction et Note")
            self.envoyerMailCorrectionNote(boite, cours, correction, note)
            LOG.info("----- notifierCorrection END -----")
            return None

        if is_notifier_correction:
            LOG.info("Envoyer mail Correction")
            self.envoyerMailCorrectionNote(boite, cours, correction, note)
            LOG.info("----- notifierCorrection END -----")
            return None

        if is_notifier_note:
            LOG.info("Envoyer mail Note")
            self.envoyerMailCorrectionNote(boite, cours, correction, note)
            LOG.info("----- notifierCorrection END -----")
            return None

        LOG.info("Notification correction et notation désactivée")
        LOG.info("----- notifierCorrection END -----")

    def envoyerMailCorrectionNote(self, boite, cours, correction=False, note=False):
        LOG.info("----- envoyerMailCorrectionNote START -----")
        portal = getToolByName(self, "portal_url").getPortalObject()
        portal_membership = getToolByName(self, 'portal_membership')

        authMember = portal_membership.getAuthenticatedMember()
        send_from = authMember.getProperty("email")
        if not send_from:
            send_from = portal.getProperty("email_from_address")

        LOG.info(send_from)

        etudiant = portal_membership.getMemberById(self.Creator())
        send_to = etudiant.getProperty("email")
        if not send_to:
            LOG.info("Pas d'email de destinataire")
            return None

        LOG.info(send_to)

        if correction:
            objet = "Une correction est disponible"
        if note:
            objet = "Une note est disponible"
        if correction and note:
            objet = "Une correction et une note sont disponibles"

        form = {"de":    send_from,
                "a":     send_to,
                "objet": objet}

        message = ["Bonjour %s\n" % etudiant.getProperty("fullname")]
        message.append("%s pour votre dépôt \"%s\" dans :" % (objet, self.Title()))
        message.append("    - la boite \"%s\"" % boite.Title())
        message.append("    - du cours \"%s\"" % cours.Title())
        message.append("    - auteur du cours : \"%s\"" % cours.getAuteur()["fullname"])
        coAuteurs = cours.getCoAuteursCours()
        if coAuteurs:
            message.append("    - co-auteurs du cours :")
            for coAuteur in coAuteurs:
                message.append("        - %s" % coAuteur["fullname"])
        message.append("Consulter sur %s : %s.\n" % (portal.Title(), self.aq_parent.absolute_url()))
        message.append("Cordialement,")
        message.append("L'équipe %s" % portal.Title())
        form["message"] = "\n".join(message)
        LOG.info(form["message"])
        try:
            jalon_utils.envoyerMail(form)
        except:
            LOG.info("----- erreur envoi email -----")
        LOG.info("----- envoyerMailCorrectionNote END -----")

registerATCT(JalonFile, PROJECTNAME)
