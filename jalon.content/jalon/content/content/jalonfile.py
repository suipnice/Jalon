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
                         widget=atpublic.StringWidget(label=_(u"Actif"),
                         )),
    atpublic.TextField("correction",
                       required=True,
                       accessor="getCorrection",
                       searchable=False,
                       widget=atpublic.TextAreaWidget(label=_(u"Correction"),
                       )),
    atpublic.StringField("note",
                         required=False,
                         accessor="getNote",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Note ou appréciation"),
                         )),
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

    def getCorrectionDepot(self):
        return str(self.correction)

    def getFichierCorrection(self):
        corrections = getattr(self.aq_parent, "corrections", None)
        if corrections:
            fichier_correction = getattr(corrections, "Correction_%s" %self.getId(), None)
            if fichier_correction:
                return "%s/at_download/file" % fichier_correction.absolute_url()
        return None

    def getSize(self):
        return self.file.get_size()

    def notifierCorrection(self, correction=False, note=False):
        self.plone_log("----- notifierCorrection -----")
        boite = self.aq_parent
        cours = boite.aq_parent
        if not boite.getNotificationCorrection():
            self.plone_log("Notification correction désactivée")
            return None

        self.plone_log("Notification correction activée")
        portal = getToolByName(self,"portal_url").getPortalObject()
        portal_membership = getToolByName(self, 'portal_membership')

        authMember = portal_membership.getAuthenticatedMember()
        send_from = authMember.getProperty("email")
        if not send_from:
            send_from = portal.getProperty("email_from_address")

        self.plone_log(send_from)

        etudiant = portal_membership.getMemberById(self.Creator())
        send_to = etudiant.getProperty("email")
        if not send_to:
            self.plone_log("Pas d'email de destinataire")
            return None


        self.plone_log(send_to)
        """
        for auteur in cours.getCoAuteursCours():
            send_to.append(auteur["email"])
        send_to.append(cours.getAuteur()["email"])
        """
        self.plone_log(send_to)

        if correction:
            objet = "Une correction est disponible"
        if note:
            objet = "Une note est disponible"
        if correction and note:
            objet ="Une correction et une note sont disponibles"

        form = {"de"    : send_from,
                "a"     : send_to,
                "objet" : objet}

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
        message.append("Consulter sur %s : %s.\n" % (portal.Title(), portal.absolute_url()))
        message.append("Cordialement,")
        message.append("L'équipe %s" % portal.Title())
        form["message"] = "\n".join(message)
        self.plone_log(form["message"])
        try:
            jalon_utils.envoyerMail(form)
        except:
            self.plone_log("----- erreur envoi email -----")

        self.plone_log("----- notifierCorrection -----")

registerATCT(JalonFile, PROJECTNAME)
