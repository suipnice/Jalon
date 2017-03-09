# -*- coding: utf-8 -*-
""" Annonces Jalon. """
from zope.interface import implements
from Products.Archetypes.public import *
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.utils import getToolByName

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonAnnonce

import jalon_utils

JalonAnnonceSchema = ATDocumentSchema.copy() + Schema((
    LinesField("publics",
               required=False,
               accessor="getPublics",
               searchable=False,
               widget=LinesWidget(label=_(u"Publics cible d'une annonce"),
                                  visible={'view': 'visible', 'edit': 'invisible'})
               ),
))


class JalonAnnonce(ATDocumentBase):

    """ Une annonce dans un cours. """

    implements(IJalonAnnonce)
    meta_type = 'JalonAnnonce'
    schema = JalonAnnonceSchema
    schema['description'].required = True
    schema['description'].widget.label = "Description"
    schema['text'].required = False
    schema['text'].mode = "r"

    def setProperties(self, dico):
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        self.reindexObject()

    def getDescriptionAff(self):
        return self.Description().replace("\n", "<br/>")

    def getLocaleDate(self):
        return jalon_utils.getLocaleDate(self.modified())

    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

    def envoyerAnnonce(self):
        parent = self.aq_parent.aq_parent
        portal = self.portal_url.getPortalObject()
        portal_membership = getToolByName(portal, 'portal_membership')
        jalon_properties = getToolByName(portal, 'portal_jalon_properties')
        authMember = portal_membership.getAuthenticatedMember()
        de = authMember.getProperty("email")
        fullname = authMember.getProperty("fullname")
        if not fullname:
            fullname = authMember.getProperty("displayName")
        dico = {"de": de,
                "a": "",
                "objet": self.Title(),
                "message": self.Description(),
                "cours": parent.Title(),
                "auteur": fullname}
        diffusion = {"activer_diffusion": jalon_properties.getJalonProperty("activer_liste_diffusion"),
                     "type_diffusion": jalon_properties.getJalonProperty("type_diffusion").split(",")}
        for public in self.getPublics():
            typeELP, codeELP = public.split("*-*")
            if typeELP == "invitationsemail":
                for invitation in parent.getInvitations():
                    dico["a"] = invitation
                    jalon_utils.envoyerMail(dico)
            listeEtudiants = []
            if diffusion["activer_diffusion"] and typeELP in diffusion["type_diffusion"]:
                dico["a"] = diffusion["format_diffusion"].replace("*-*code*-*", codeELP)
                jalon_utils.envoyerMail(dico)
            elif typeELP in ["etape", "ue", "uel", "groupe"]:
                listeEtudiants = parent.aq_parent.getListeEtudiants(codeELP, typeELP)
                for etudiant in listeEtudiants:
                    if etudiant["EMAIL_ETU"]:
                        dico["a"] = etudiant["EMAIL_ETU"]
                        jalon_utils.envoyerMail(dico)
            else:
                if typeELP == "groupeperso":
                    listeEtudiants = parent.getNominativeRegistration()
                if typeELP == "coauteurs":
                    listeEtudiants = parent.getCoAuteursCours()
                if typeELP == "colecteurs":
                    listeEtudiants = parent.getCourseReader()
                if listeEtudiants:
                    for etudiant in listeEtudiants:
                        if etudiant["email"]:
                            dico["a"] = etudiant["email"]
                            jalon_utils.envoyerMail(dico)
        jalon_utils.envoyerMail({"de":      de,
                                 "a":       de,
                                 "objet":   self.Title(),
                                 "message": self.Description(),
                                 "cours":   parent.Title(),
                                 "auteur":  fullname})
        cours = self.aq_parent.aq_parent
        auteurCours = cours.getAuteurPrincipal()
        if not auteurCours:
            auteurCours = cours.Creator()
        if self.Creator() != auteurCours:
            infosAuteurCours = jalon_utils.getIndividu(auteurCours, "dict")
            jalon_utils.envoyerMail({"de":      de,
                                     "a":       infosAuteurCours["email"],
                                     "objet":   self.Title(),
                                     "message": self.Description(),
                                     "cours":   parent.Title(),
                                     "auteur":  fullname})

registerATCT(JalonAnnonce, PROJECTNAME)
