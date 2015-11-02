# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.Archetypes.public import *
#from Products.ATExtensions.ateapi import *

from Products.ATContentTypes.content.folder import ATFolder, ATFolderSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.utils import getToolByName

from persistent.dict import PersistentDict

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonBoiteDepot

from DateTime import DateTime
from os import close
from zipfile import ZipFile, ZIP_DEFLATED

import jalon_utils
import ldap
import os
import copy

ressourceType = [u"Lien web".encode("utf-8"), u"Lecteur exportable".encode("utf-8"), u"Ressource bibliographie".encode("utf-8")]

JalonBoiteDepotSchema = ATFolderSchema.copy() + Schema((
    DateTimeField("dateDepot",
                  required=False,
                  accessor="getDateDepot",
                  searchable=False,
                  widget=CalendarWidget(label=_(u"Date limite de dépôt affichée aux étudiants"),)),
    DateTimeField("dateRetard",
                  required=False,
                  accessor="getDateRetard",
                  searchable=False,
                  widget=CalendarWidget(label=_(u"Tolérer les dépôts jusqu'au"),)),
    LinesField("listeSujets",
               required=False,
               accessor="getListeSujets",
               searchable=False,
               widget=LinesWidget(label=_(u"Liste des sujets"),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("listeDevoirs",
               required=False,
               accessor="getListeDevoirs",
               searchable=False,
               widget=LinesWidget(label=_(u"Liste des devoirs des étudiants"),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("listeCorrections",
               required=False,
               accessor="getListeCorrections",
               searchable=False,
               widget=LinesWidget(label=_(u"Liste des corrections"),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    StringField("dateAff",
                required=False,
                accessor="getDateAff",
                searchable=False,
                widget=StringWidget(label=_(u"Date d'affichage de la boite de dépôts"),)),
    StringField("dateMasq",
                required=False,
                accessor="getDateMasq",
                searchable=False,
                widget=StringWidget(label=_(u"Date à laquelle la boite de dépôts est masquée"),)),
    BooleanField("correctionIndividuelle",
                 required=False,
                 accessor="getCorrectionIndividuelle",
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Activer les corrections individuelles"),)),
    BooleanField("notificationCorrection",
                 required=False,
                 accessor="getNotificationCorrection",
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Activer la notification des corrections"),)),
    BooleanField("notation",
                 required=False,
                 accessor="getNotation",
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Activer la notation des dépôts des étudiants"),)),
    BooleanField("notificationNotation",
                 required=False,
                 accessor="getNotificationNotation",
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Activer la notification des notations"),)),
    BooleanField("accesDepots",
                 required=False,
                 accessor="getAccesDepots",
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Autoriser la visualisation des dépôts entre étudiants"),)),
    BooleanField("accesCompetences",
                 required=False,
                 accessor="getAccesCompetences",
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Afficher les compétences aux enseignants"),)),
    BooleanField("afficherCompetences",
                 required=False,
                 accessor="getAfficherCompetences",
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Afficher les compétences aux étudiants"),)),
    BooleanField("modifierCompetences",
                 required=False,
                 accessor="getModifierCompetences",
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Restreindre la modification des compétences au créateur de la boite de dépôts"),))
))


class JalonBoiteDepot(ATFolder):
    """ Une ressource externe pour Jalon
    """

    implements(IJalonBoiteDepot)
    meta_type = 'JalonBoiteDepot'
    schema = JalonBoiteDepotSchema
    schema['description'].required = False
    schema['description'].widget.label = "Consigne"
    schema['description'].widget.description = ""

    _infos_element = {}
    _competences = {}
    _comp_etudiants = {}

    def getElementCours(self, key):
        return self.getInfosElement(key)

    def getInfosElement(self, key=None):
        if key:
            return self._infos_element.get(key, None)
        return self._infos_element

    def getKeyInfosElement(self):
        return self._infos_element.keys()

    def setInfosElement(self, infos_element):
        if type(self._infos_element).__name__ != "PersistentMapping":
            self._infos_element = PersistentDict(infos_element)
        else:
            self._infos_element = infos_element

    def getOrdreCompetences(self):
        ordre = self._competences.keys()
        ordre.sort(lambda x, y: cmp(int(x), int(y)))
        return ordre

    def getCompetences(self, key=None):
        if key:
            return self._competences.get(key, None)
        return self._competences

    def setCompetences(self, competences):
        if type(self._competences).__name__ != "PersistentMapping":
            self._competences = PersistentDict(competences)
        else:
            self._competences = competences

    def getOrdreEtudiants(self):
        ordre = []
        for SESAME_ETU in self._comp_etudiants.keys():
            ordre.append({"id"  : SESAME_ETU,
                          "nom" : self.getNomEtudiant(SESAME_ETU)})
        ordre.sort(lambda x, y: cmp(x["nom"], y["nom"]))
        return ordre

    def getCompEtudiants(self, key=None):
        if key:
            return self._comp_etudiants.get(key, None)
        return self._comp_etudiants

    def getAffComEtu(self, SESAME_ETU):
        dicoCompEtudiants = self._comp_etudiants
        if not SESAME_ETU in dicoCompEtudiants:
            return {}

        dicoCompEtudiant = {}
        compEtu = dicoCompEtudiants[SESAME_ETU]
        dicoGradation = {"acquerir" : "À acquérir",
                         "encours"  : "En cours d'acquisition",
                         "partielle": "Partiellement acquis",
                         "acquise"  : "Acquis"}
        dicoCompetences = self._competences
        listeIdCompetences = self._competences.keys()
        listeIdCompetences.sort(lambda x, y: cmp(int(x), int(y)))
        for idcompetence in listeIdCompetences:
            competence = dicoCompetences[idcompetence]
            if idcompetence in compEtu:
                if competence["evaluation"] == "libre":
                    dicoCompEtudiant[idcompetence] = compEtu[idcompetence]
                if competence["evaluation"] == "validation":
                    dicoCompEtudiant[idcompetence] = "Acquis"
                if competence["evaluation"] == "gradation":
                    dicoCompEtudiant[idcompetence] = dicoGradation[compEtu[idcompetence]]
                if competence["evaluation"] == "note":
                    if "." in compEtu[idcompetence] or "," in compEtu[idcompetence]:
                        if competence["note_partielle"]:
                            note_partielle = float(competence["note_partielle"])
                        if competence["note_acquise"]:
                            note_acquise = float(competence["note_acquise"])
                        note = float(compEtu[idcompetence])
                    else:
                        if competence["note_partielle"]:
                            note_partielle = int(competence["note_partielle"])
                        if competence["note_acquise"]:
                            note_acquise = int(competence["note_acquise"])
                        try:
                            note = int(compEtu[idcompetence])
                        except:
                            note = "Pas de note"
                    if note_acquise and note >= note_acquise:
                        dicoCompEtudiant[idcompetence] = "Acquis"
                        #dicoCompEtudiant[idcompetence] = "%s / %s (Acquis)" % (compEtu[idcompetence], competence["note_max"])
                    elif note_partielle and note >= note_partielle:
                        dicoCompEtudiant[idcompetence] = "Partiellement acquis"
                        #dicoCompEtudiant[idcompetence] = "%s / %s (Partiellement acquis)" % (compEtu[idcompetence], competence["note_max"])
                    else:
                        dicoCompEtudiant[idcompetence] = "À acquérir"
                        #dicoCompEtudiant[idcompetence] = compEtu[idcompetence]
            else:
                dicoCompEtudiant[idcompetence] = 'À acquérir'
        return dicoCompEtudiant

    def getNomEtudiant(self, SESAME_ETU):
        if self.isLDAP() or "@" in SESAME_ETU:
            #Cas du ldap actif ou de l'etudiant EtudiantJalon
            portal_membership = getToolByName(self, "portal_membership")
            member = portal_membership.getMemberById(SESAME_ETU)
            if member:
                etudiantName = str(member.getProperty("fullname"))
                if not etudiantName:
                    etudiantName = str(member.getProperty("cn"))
            else:
                etudiantName = SESAME_ETU
        else:
            portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
            etudiant = portal_jalon_bdd.getIndividuLITE(SESAME_ETU)
            if etudiant:
                etudiantName = "%s %s" % (etudiant["LIB_NOM_PAT_IND"], etudiant["LIB_PR1_IND"])
            else:
                etudiantName = SESAME_ETU
        return etudiantName

    def setCompEtudiants(self, comp_etudiants):
        if type(self._comp_etudiants).__name__ != "PersistentMapping":
            self._comp_etudiants = PersistentDict(comp_etudiants)
        else:
            self._comp_etudiants = comp_etudiants

    def ajouterTag(self, tag):
        return jalon_utils.setTag(self, tag)

    def getTagDefaut(self):
        return jalon_utils.getTagDefaut(self)

    def getAttributsMod(self, info):
        dico = {"info":  ['title', 'description'],
                "date":  ['dateDepot', 'dateRetard']}
        return dico[info]

    def getInfosListeAttribut(self, attribut, personnel=False):
        retour = []
        listeElement = self.getListeAttribut(attribut)
        infos_element = self.getInfosElement()
        for idElement in listeElement:
            infos = infos_element.get(idElement, '')
            affElement = self.isAfficherElement(infos['affElement'], infos['masquerElement'])
            if personnel or not affElement['val'] == 0:
                new = {"idElement":       idElement,
                       "titreElement":    infos["titreElement"],
                       "typeElement":     infos["typeElement"].replace(" ", ""),
                       "createurElement": infos["createurElement"],
                       "affElement":      affElement,
                       "iconElement":     affElement["icon"],
                       "classElement":    self.test(affElement['val'] == 0, 'arrondi off', 'arrondi')
                       }
                retour.append(new)
        if retour:
            retour.sort(lambda x, y: cmp(x["titreElement"], y["titreElement"]))
        return retour

    def getListeAttribut(self, attribut):
        return self.__getattribute__("liste%s" % attribut.capitalize())

    def getAffDate(self, attribut):
        if attribut == "DateDepot":
            date = self.dateDepot
        if attribut == "DateRetard":
            date = self.dateRetard
        if not date:
            return "Aucune date limite de dépôt."
        else:
            return jalon_utils.getLocaleDate(date, '%d %B %Y - %Hh%M')

    def getDateDepot(self):
        if not self.dateDepot:
            return DateTime().strftime("%Y/%m/%d %H:%M")
        else:
            return self.dateDepot.strftime("%Y/%m/%d %H:%M")

    def getDateRetard(self):
        if not self.dateRetard:
            return DateTime().strftime("%Y/%m/%d %H:%M")
        else:
            return self.dateRetard.strftime("%Y/%m/%d %H:%M")

    def getNbDepots(self, personnel):
        if not personnel:
            nbDepots = 0
            authMember = self.portal_membership.getAuthenticatedMember().getId()
            for iddepot in self.objectIds():
                if authMember in iddepot:
                    nbDepots = nbDepots + 1
            return nbDepots
        depots = self.objectIds()
        if "corrections" in depots:
            return len(depots) - 1
        else:
            return len(depots)

    def getNbSujets(self):
        return len(self.getInfosListeAttribut("sujets", True))

    def getNbCompetences(self):
        return len(self._competences.keys())

    def getDepots(self, authMember, personnel, request):
        retour = {"total":              0,
                  "etudiantsTotal":     0,
                  "valides":            0,
                  "etudiantsValides":   0,
                  "invalides":          0,
                  "etudiantsInvalides": 0,
                  "listeDepots":  []}
        listeDepots = []
        valides = 0
        listeEtudiantsValides = []
        invalides = 0
        listeEtudiantsInvalides = []
        listeEtudiantsTotal = []
        if personnel or self.getAccesDepots():
            depots = self.getFolderContents(contentFilter={"portal_type": "JalonFile"})
            if not depots:
                return retour
            portal = self.portal_url.getPortalObject()
            portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
            #if not self.isLDAP():
            #    portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")

            for depot in depots:
                #etudiant = créateur du dépôt
                auteurDepot = str(depot.Creator)
                member = portal.portal_membership.getMemberById(auteurDepot)
                """
                if self.isLDAP() or member.has_role("EtudiantJalon"):
                    #Cas du ldap actif ou de l'etudiant EtudiantJalon
                    if member:
                        etudiantName = str(member.getProperty("fullname"))
                        if not etudiantName:
                            etudiantName = str(member.getProperty("cn"))
                    else:
                        etudiantName = auteurDepot
                else:
                    etudiant = portal_jalon_bdd.getIndividuLITE(auteurDepot)
                    if etudiant:
                        etudiantName = "%s %s" % (etudiant["LIB_NOM_PAT_IND"], etudiant["LIB_PR1_IND"])
                    else:
                        etudiantName = auteurDepot
                """
                etudiant = portal_jalon_bdd.getIndividuLITE(auteurDepot)
                if etudiant:
                    etudiantName = "%s %s" % (etudiant["LIB_NOM_PAT_IND"], etudiant["LIB_PR1_IND"])
                elif self.isLDAP() or member.has_role("EtudiantJalon"):
                    #Cas du ldap actif ou de l'etudiant EtudiantJalon
                    if member:
                        etudiantName = str(member.getProperty("fullname"))
                        if not etudiantName:
                            etudiantName = str(member.getProperty("cn"))
                    else:
                        etudiantName = auteurDepot
                else:
                    etudiantName = auteurDepot

                if not etudiantName in listeEtudiantsTotal:
                    listeEtudiantsTotal.append(etudiantName)
                if depot.getActif:
                    valides = valides + 1
                    if not etudiantName in listeEtudiantsValides:
                        listeEtudiantsValides.append(etudiantName)
                else:
                    invalides = invalides + 1
                    if not etudiantName in listeEtudiantsInvalides:
                        listeEtudiantsInvalides.append(etudiantName)
                correction = 0
                if not depot.getCorrection in ["", None, " ", "\n"]:
                    correction = 1
                if depot.getFichierCorrection:
                    correction = 1
                listeDepots.append({"etudiant":   ' '.join([item.capitalize() for item in etudiantName.split()]),
                                    "id":         depot.getId,
                                    "title":      depot.Title,
                                    "date":       self.getLocaleDate(depot.created, '%d/%m/%Y - %Hh%M'),
                                    "url":        depot.getURL,
                                    "actif":      depot.getActif,
                                    "correction": correction,
                                    "note":       depot.getNote,
                                    "size":       1000})
            retour = {"total":              len(listeDepots),
                      "etudiantsTotal":     len(listeEtudiantsTotal),
                      "valides":            valides,
                      "etudiantsValides":   len(listeEtudiantsValides),
                      "invalides":          invalides,
                      "etudiantsInvalides": len(listeEtudiantsInvalides),
                      "listeDepots":        listeDepots}
        else:
            for iddepot in self.objectIds():
                if authMember.getId() in iddepot:
                    depot = getattr(self, iddepot)
                    correction = 0
                    if depot.getCorrection() not in ["", None, " "]:
                        correction = 1
                    listeDepots.append({"etudiant":   authMember,
                                        "id":         depot.getId(),
                                        "title":      depot.title_or_id(),
                                        "date":       self.getLocaleDate(depot.created(), '%d/%m/%Y - %Hh%M'),
                                        "url":        depot.absolute_url(),
                                        "actif":      depot.getActif(),
                                        "correction": correction,
                                        "note":       depot.getNote(),
                                        "size":       depot.getSize()})
            retour = {"listeDepots": listeDepots}
        return retour

    def getLocaleDate(self, date, format="%d/%m/%Y"):
        return jalon_utils.getLocaleDate(date, format)

    def getOptionsAvancees(self):
        options = {}
        for option in ["getCorrectionIndividuelle", "getNotificationCorrection", "getNotation", "getNotificationNotation", "getAccesDepots", "getAccesCompetences"]:
            if self.__getattribute__(option)():
                options[option] = {"actif" : 1, "texte": _(u"Activée")}
            else:
                options[option] = {"actif": 0, "texte": _(u"Désactivée")}
        return options

    def getRubriqueEspace(self, ajout=None):
        return self.aq_parent.getRubriqueEspace(ajout)

    def getPermissionModifierCompetence(self, personnel, user_id):
        if not personnel:
            return False
        elif user_id == self.Creator():
            return True
        elif self.getModifierCompetences():
            return False
        else:
            return True

    def getElementView(self, idElement, createurElement, typeElement, indexElement, mode_etudiant=None):
        if typeElement == "JalonFile":
            retour = {"titreElement": "", "descriptionElement": "", "correctionElement": "", "noteElement": "", "urlElement": "", "indexElement": int(indexElement)}
            depot = getattr(getattr(self, createurElement), idElement)
            retour["titreElement"] = depot.Title()
            retour["descriptionElement"] = depot.Description().replace("\n", "<br/>")
            if retour["descriptionElement"] in ["", " "]:
                retour["descriptionElement"] = "Aucun commentaire"
            if self.getCorrectionIndividuelle():
               retour["correctionElement"] = depot.getCorrectionDepot().replace("\n", "<br/>")
            if self.getNotation():
               retour["noteElement"] = depot.getNote()
            retour["fichierElement"] = depot.getFichierCorrection()
            retour["urlElement"] = '%s/%s/%s/at_download/file' % (self.absolute_url(), createurElement, idElement)
            return retour
        else:
            return self.aq_parent.getElementView(idElement, createurElement, typeElement, indexElement, mode_etudiant)

    def getDepotDate(self, data, sortable=False):
        return jalon_utils.getDepotDate(data, sortable)

    def setProperties(self, dico):
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        self.reindexObject()

    def setAttributActivite(self, form):
        if "DateDepot" in form and form["DateDepot"] != self.getDateDepot():
            self.aq_parent.setActuCours({"reference": self.getId(),
                                         "code":      "datedepot",
                                         "dateDepot": form["DateDepot"]})
        self.setProperties(form)
        if "Title" in form:
            self.aq_parent.modifierInfosElementPlan(self.getId(), form["Title"])
        self.reindexObject()

    def isAfficherElement(self, affElement, masquerElement):
        return jalon_utils.isAfficherElement(affElement, masquerElement)

    def getParentPlanElement(self, idElement, idParent, listeElement):
        if idElement == self.getId():
            return self.aq_parent.getParentPlanElement(idElement, idParent, listeElement)
        return {"idElement": "racine", "affElement": "", "masquerElement": ""}

    def isChecked(self, idElement, formulaire, listeElement=None):
        if formulaire == "ajout-sujets":
            if idElement in list(self.getListeSujets()):
                return 1
            return 0
        if formulaire == "ajout-corrections":
            if idElement in list(self.getListeCorrections()):
                return 1
            return 0

    """
    isDepotActif renvoit :
        1 si les étudiants ont le droit de déposer.
        2 s'ils sont en retard.
        0 s'ils n'ont plus le droit.
    """
    def isDepotActif(self):
        now = DateTime(DateTime().strftime("%Y/%m/%d %H:%M"))
        date_depot = DateTime(self.getDateDepot())
        date_retard = DateTime(self.getDateRetard())
        # La date de dépot n'est pas encore passée.
        if now <= date_depot:
            return 1
        # La date de retard n'est pas encore passée.
        if date_retard > date_depot and now < date_retard:
            return 2
        return 0

    def isCorrigerNoter(self):
        corriger = self.getCorrectionIndividuelle()
        noter = self.getNotation()
        if corriger and noter:
            return {"title"    : "Corriger et Noter",
                    "corriger" : 1,
                    "noter"    : 1}
        if corriger:
            return {"title"    : "Corriger",
                    "corriger" : 1,
                    "noter"    : 0}
        if noter:
            return {"title"    : "Noter",
                    "corriger" : 0,
                    "noter"    : 1}

    def isLDAP(self):
        return jalon_utils.isLDAP()

    def activerDepot(self, idDepot, actif):
        depot = getattr(self, idDepot)
        depot.setProperties({"Actif": actif})

    def afficherRessource(self, idElement, dateAffichage, attribut):
        if idElement == self.getId():
            if attribut == "affElement":
                self.dateAff = dateAffichage
                self.dateMasq = ""

                portal = self.portal_url.getPortalObject()
                portal_workflow = getToolByName(portal, "portal_workflow")
                if portal_workflow.getInfoFor(self, "review_state", wf_id="jalon_workflow") != "pending":
                    portal_workflow.doActionFor(self, "submit", "jalon_workflow")
            else:
                self.dateMasq = dateAffichage
            self.aq_parent.modifierInfosBoitePlan(self.getId(), {"affElement": self.getDateAff(), "masquerElement": self.getDateMasq()})
            self.reindexObject()
        else:
            infos_element = copy.deepcopy(self.getInfosElement())
            if infos_element:
                infos_element[idElement][attribut] = dateAffichage
                if attribut == "affElement":
                    infos_element[idElement]["masquerElement"] = ""
                self.setInfosElement(infos_element)

                rep = {"Image":                     "Fichiers",
                       "File":                      "Fichiers",
                       "Lien web":                  "Externes",
                       "Lecteur exportable":        "Externes",
                       "Reference bibliographique": "Externes",
                       "Glossaire":                 "Glossaire",
                       "Webconference":             "Webconference",
                       "Presentations sonorisees":  "Sonorisation"}
                if infos_element[idElement]["typeElement"] in rep.keys():
                    idFichier = idElement
                    if "*-*" in idElement:
                        idFichier = idElement.replace("*-*", ".")
                    objet = getattr(getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), infos_element[idElement]["createurElement"]), rep[infos_element[idElement]["typeElement"]]), idFichier)
                    portal = self.portal_url.getPortalObject()
                    portal_workflow = getToolByName(portal, "portal_workflow")
                    boite_state = portal_workflow.getInfoFor(self, "review_state", wf_id="jalon_workflow")
                    objet_state = portal_workflow.getInfoFor(objet, "review_state", wf_id="jalon_workflow")
                    if boite_state != objet_state:
                        if boite_state == "pending" and objet_state != "published":
                            portal_workflow.doActionFor(objet, "submit", "jalon_workflow")
                self.reindexObject()

    def ajouterElement(self, idElement, typeElement, titreElement, createurElement, affElement=""):
        if "." in idElement:
            idElement = idElement.replace(".", "*-*")
        listeSujets = list(self.getListeSujets())
        listeSujets.append(idElement)
        setattr(self, "listeSujets", tuple(listeSujets))

        self.ajouterInfosElement(idElement, typeElement, titreElement, createurElement, affElement=affElement)
        rep = {"Image":                     "Fichiers",
               "File":                      "Fichiers",
               "Page":                      "Fichiers",
               "Lien web":                  "Externes",
               "Lecteur exportable":        "Externes",
               "Reference bibliographique": "Externes",
               "Catalogue BU":              "Externes",
               "Webconference":             "Webconference",
               "Presentations sonorisees":  "Sonorisation"}
        if typeElement in rep:
            if "*-*" in idElement:
                idElement = idElement.replace("*-*", ".")
            objet = getattr(getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), createurElement), rep[typeElement]), idElement)
            relatedItems = objet.getRelatedItems()
            if not self in relatedItems:
                relatedItems.append(self)
                objet.setRelatedItems(relatedItems)
                objet.reindexObject()
                depotRelatedItems = self.getRelatedItems()
                depotRelatedItems.append(objet)
                self.setRelatedItems(depotRelatedItems)

    def ajouterInfosElement(self, idElement, typeElement, titreElement, createurElement, affElement=""):
        infos_element = copy.deepcopy(self.getInfosElement())
        if not idElement in infos_element:
            infos_element[idElement] = {"titreElement": titreElement,
                                        "typeElement": typeElement,
                                        "createurElement": createurElement,
                                        "affElement": affElement,
                                        "masquerElement": ""}
            #self.setInfos_element(infos_element)
            self.setInfosElement(infos_element)

    def purgerDepots(self):
        self.manage_delObjects(self.objectIds())
        self.setListeDevoirs(())
        self.setCompEtudiants({})
        self.reindexObject()

    def retirerElement(self, idElement, menu):
        infos_element = self.getInfosElement()
        infosElement = infos_element[idElement]

        elements_list = list(self.__getattribute__("liste%s" % menu.capitalize()))
        elements_list.remove(idElement)

        self.__getattribute__("setListe%s" % menu.capitalize())(tuple(elements_list))
        del infos_element[idElement]

        dicoRep = {"Image":                      "Fichiers",
                   "File":                       "Fichiers",
                   "Page":                       "Fichiers",
                   "Lien web":                   "Externes",
                   "Lecteur exportable":         "Externes",
                   "Reference bibliographique":  "Externes",
                   "Catalogue BU":               "Externes",
                   "Webconference":              "Webconference",
                   "Presentations sonorisees":   "Sonorisation"}

        repertoire = infosElement["typeElement"]
        if repertoire in dicoRep:
            repertoire = dicoRep[repertoire]
        if "*-*" in idElement:
            idElement = idElement.replace("*-*", ".")
        objet = getattr(getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), infosElement["createurElement"]), repertoire), idElement, None)
        if objet:
            relatedItems = objet.getRelatedItems()
            try:
                relatedItems.remove(self)
                objet.setRelatedItems(relatedItems)
            except:
                pass
            objet.reindexObject()

    def retirerTousElements(self):
        dicoRep = {"Image":                     "Fichiers",
                   "File":                      "Fichiers",
                   "Page":                      "Fichiers",
                   "Lien web":                  "Externes",
                   "Lecteur exportable":        "Externes",
                   "Reference bibliographique": "Externes",
                   "Catalogue BU":              "Externes",
                   "Webconference":             "Webconference",
                   "Presentations sonorisees":  "Sonorisation"}
        infos_element = self.getInfosElement()
        for sujet in self.getListeSujets():
            infosElement = infos_element[sujet]
            repertoire = infosElement["typeElement"]
            if repertoire in dicoRep:
                repertoire = dicoRep[repertoire]
            if "*-*" in sujet:
                sujet = sujet.replace("*-*", ".")
            objet = getattr(getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), infosElement["createurElement"]), repertoire), sujet, None)
            if objet:
                relatedItems = objet.getRelatedItems()
                try:
                    relatedItems.remove(self)
                    objet.setRelatedItems(relatedItems)
                except:
                    pass
                objet.reindexObject()

    def telechargerDepots(self, HTTP_USER_AGENT):
        import tempfile
        fd, path = tempfile.mkstemp('.zipfiletransport')
        close(fd)

        zipFile = ZipFile(path, 'w', ZIP_DEFLATED)

        #dicoEtu = {}
        listeDepots = []
        listeEtudiants = []

        for obj in self.objectValues("JalonFile"):
            if obj.getActif() == "actif":
                idEtudiant = obj.Creator()
                if not idEtudiant in listeEtudiants:
                    listeEtudiants.append(idEtudiant)
                listeDepots.append({"idEtudiant" : idEtudiant,
                                    "filename"   : "(%s) %s" % (DateTime(obj.created()).strftime("%Y-%m-%d %Hh%Mm%Ss"), obj.file.filename),
                                    "file_data"  : str(obj.file.data)})

        dicoEtudiants = jalon_utils.getIndividus(listeEtudiants, type="dict")
        for depot in listeDepots:
            try:
                filename_path = "%s/%s %s (%s)/%s" % (self.Title(), dicoEtudiants[depot["idEtudiant"]]["nom"].encode("utf-8"), dicoEtudiants[depot["idEtudiant"]]["prenom"].encode("utf-8"), dicoEtudiants[depot["idEtudiant"]]["num_etu"], depot["filename"])
            except:
                filename_path = "%s/%s/%s" % (self.Title(), depot["idEtudiant"], depot["filename"])
            if 'Windows' in HTTP_USER_AGENT:
                try:
                    filename_path = filename_path.decode('utf-8').encode('cp437')
                except:
                    pass
            zipFile.writestr(filename_path, depot["file_data"])
        zipFile.close()

        fp = open(path, 'rb')
        data = fp.read()
        fp.close()
        return {"length": str(os.stat(path)[6]), "data": data}

    def telechargerListingDepots(self, HTTP_USER_AGENT):
        import tempfile
        from xlwt import Workbook

        isCorrection = self.getCorrectionIndividuelle()
        isNotation = self.getNotation()
        translation_service = getToolByName(self,'translation_service')
        portal_membership = getToolByName(self, "portal_membership")
        authMember = portal_membership.getAuthenticatedMember()

        fd, path = tempfile.mkstemp('.%s-xlfiletransport' % authMember.getId())
        close(fd)

        # création
        listing = Workbook(encoding="utf-8")

        # création de la feuille 1
        feuil1 = listing.add_sheet('feuille 1')

        # ajout des en-têtes
        feuil1.write(0, 0, 'Nom')
        feuil1.write(0, 1, 'Prénom')
        feuil1.write(0, 2, 'Numéro étudiant')
        feuil1.write(0, 3, 'Titre du dépôt')
        feuil1.write(0, 4, 'Date du dépôt')
        if isCorrection:
            feuil1.write(0, 5, 'Correction')
        if isNotation:
            feuil1.write(0, 6, 'Note')

        listeDepots = []
        listeEtudiants = []
        for obj in self.objectValues("JalonFile"):
            if obj.getActif() == "actif":
                idEtudiant = obj.Creator()
                depot = {"idEtudiant": idEtudiant,
                         "titreDepot": obj.Title(),
                         "dateDepot":  self.getLocaleDate(obj.created(), '%d/%m/%Y - %Hh%M')}
                if isCorrection:
                    correction = obj.getCorrection()
                    if not correction:
                        dummy = _(u"Non corrigé")
                        msg_correction = u"Non corrigé"
                        correction = translation_service.utranslate(domain='jalon.content',
                                                                    msgid=msg_correction,
                                                                    default=msg_correction,
                                                                    context=object)
                    depot["correctionDepot"] = correction
                if isNotation:
                    note = obj.getNote()
                    if not note:
                        dummy = _(u"Non noté")
                        msg_note = u"Non noté"
                        note = translation_service.utranslate(domain='jalon.content',
                                                              msgid=msg_note,
                                                              default=msg_note,
                                                              context=object)
                    depot["noteDepot"] = note
                listeDepots.append(depot)
                if not idEtudiant in listeEtudiants:
                    listeEtudiants.append(idEtudiant)
        dicoEtudiants = jalon_utils.getIndividus(listeEtudiants, type="dict")

        i = 1
        for depot in listeDepots:
            if depot["idEtudiant"] in dicoEtudiants.keys():
                # ajout des valeurs dans la ligne suivante
                ligne1 = feuil1.row(i)
                ligne1.write(0, dicoEtudiants[depot["idEtudiant"]]["nom"])
                ligne1.write(1, dicoEtudiants[depot["idEtudiant"]]["prenom"])
                ligne1.write(2, dicoEtudiants[depot["idEtudiant"]]["num_etu"])
                ligne1.write(3, depot["titreDepot"])
                ligne1.write(4, depot["dateDepot"])
                if isCorrection:
                    ligne1.write(5, depot["correctionDepot"])
                if isNotation:
                    ligne1.write(6, depot["noteDepot"])
                i = i + 1

        # ajustement éventuel de la largeur d'une colonne
        feuil1.col(2).width = 4000
        feuil1.col(3).width = 10000
        feuil1.col(4).width = 4000
        if isCorrection:
            feuil1.col(5).width = 10000

        listing.save(path)

        fp = open(path, 'rb')
        data = fp.read()
        fp.close()
        return {"length": str(os.stat(path)[6]), "data": data}

    def telechargerListingCompetences(self):
        import tempfile
        from xlwt import Workbook, XFStyle, Style, Pattern, Font

        dicoGradation = {"acquerir" : "À acquérir",
                         "encours"  : "En cours d'acquisition",
                         "partielle": "Partiellement acquis",
                         "acquise"  : "Acquis"}
        portal_membership = getToolByName(self, "portal_membership")
        authMember = portal_membership.getAuthenticatedMember()

        fd, path = tempfile.mkstemp('.%s-xlfiletransport' % authMember.getId())
        close(fd)

        # création
        listing = Workbook(encoding="utf-8")

        # création de la feuille 1
        try:
            feuil1 = listing.add_sheet(self.Title())
        except:
            feuil1 = listing.add_sheet("Boite de dépôts Jalon")

        styleAcquerir = XFStyle()
        patternAcquerir = Pattern()
        patternAcquerir.pattern = Pattern.SOLID_PATTERN
        patternAcquerir.pattern_fore_colour = Style.colour_map['gray25']
        styleAcquerir.pattern = patternAcquerir

        styleEnCours = XFStyle()
        patternEnCours = Pattern()
        patternEnCours.pattern = Pattern.SOLID_PATTERN
        patternEnCours.pattern_fore_colour = Style.colour_map['light_green']
        styleEnCours.pattern = patternEnCours

        styleAcquise = XFStyle()
        patternAcquise = Pattern()
        patternAcquise.pattern = Pattern.SOLID_PATTERN
        patternAcquise.pattern_fore_colour = Style.colour_map['sea_green']
        styleAcquise.pattern = patternAcquise
        styleAcquise.font.colour_index = Style.colour_map['white']

        bold = XFStyle()
        font = Font()
        font.bold = True
        bold.font = font

        feuil1.write(0, 0, "Légende", bold)
        feuil1.write(0, 1, "À acquérir", styleAcquerir)
        feuil1.write(0, 2, "En cours d'acquisition", styleEnCours)
        feuil1.write(0, 3, "Acquis", styleAcquise)

        styleEnTete = XFStyle()
        patternEnTete = Pattern()
        patternEnTete.pattern = Pattern.SOLID_PATTERN
        patternEnTete.pattern_fore_colour = Style.colour_map["black"]
        styleEnTete.pattern = patternEnTete
        styleEnTete.font.colour_index = Style.colour_map["white"]

        # ajout des en-têtes
        feuil1.write(2, 0, "Nom", styleEnTete)
        feuil1.write(2, 1, "Prénom", styleEnTete)
        feuil1.write(2, 2, "Numéro étudiant", styleEnTete)

        feuil1.col(0).width = 9 * 256
        feuil1.col(1).width = 12 * 256
        feuil1.col(2).width = 22 * 256

        listeIdCompetences = self._competences.keys()
        listeIdCompetences.sort(lambda x, y: cmp(int(x), int(y)))

        i = 3
        dicoCompetences = self._competences
        for idcompetence in listeIdCompetences:
            feuil1.write(2, i, dicoCompetences[idcompetence]["titre"], styleEnTete)
            feuil1.col(i).width = (len(dicoCompetences[idcompetence]["titre"]) + 2) * 256
            i = i + 1

        listeEtudiants = self._comp_etudiants.keys()
        dicoEtudiants = jalon_utils.getIndividus(listeEtudiants, type="dict")
        dicoCompEtudiant = self._comp_etudiants

        i = 3
        for etudiant in listeEtudiants:
            if etudiant in dicoEtudiants.keys():
                # ajout des valeurs dans la ligne suivante
                ligne1 = feuil1.row(i)
                ligne1.write(0, dicoEtudiants[etudiant]["nom"])
                ligne1.write(1, dicoEtudiants[etudiant]["prenom"])
                ligne1.write(2, dicoEtudiants[etudiant]["num_etu"])

                index_comp = 3
                compEtu = dicoCompEtudiant[etudiant]
                for idcompetence in listeIdCompetences:
                    competence = dicoCompetences[idcompetence]
                    if idcompetence in compEtu:
                        if competence["evaluation"] == "libre":
                            ligne1.write(index_comp, compEtu[idcompetence])
                        if competence["evaluation"] == "validation":
                            ligne1.write(index_comp, "Acquis", styleAcquise)
                        if competence["evaluation"] == "gradation":
                            if compEtu[idcompetence] == "acquerir":
                                ligne1.write(index_comp, dicoGradation[compEtu[idcompetence]], styleAcquerir)
                            if compEtu[idcompetence] == "encours":
                                ligne1.write(index_comp, dicoGradation[compEtu[idcompetence]], styleEnCours)
                            if compEtu[idcompetence] == "acquise":
                                ligne1.write(index_comp, dicoGradation[compEtu[idcompetence]], styleAcquise)
                        if competence["evaluation"] == "note":
                            style = XFStyle()
                            if "." in compEtu[idcompetence] or "," in compEtu[idcompetence]:
                                style.num_format_str = "0.00"
                                if competence["note_partielle"]:
                                    note_partielle = float(competence["note_partielle"])
                                if competence["note_acquise"]:
                                    note_acquise = float(competence["note_acquise"])
                                note = float(compEtu[idcompetence])
                            else:
                                style.num_format_str = "0"
                                if competence["note_partielle"]:
                                    note_partielle = int(competence["note_partielle"])
                                if competence["note_acquise"]:
                                    note_acquise = int(competence["note_acquise"])
                                note = int(compEtu[idcompetence])
                            if note_acquise and note >= note_acquise:
                                style.pattern = patternAcquise
                            elif note_partielle and note >= note_partielle:
                                style.pattern = patternEnCours
                            elif note_acquise and note_partielle:
                                style.pattern = patternAcquerir

                            ligne1.write(index_comp, note, style)
                    else:
                        ligne1.write(index_comp, 'À acquérir',styleAcquerir)
                    index_comp = index_comp + 1
            i = i + 1

        listing.save(path)

        fp = open(path, 'rb')
        data = fp.read()
        fp.close()
        return {"length": str(os.stat(path)[6]), "data": data}

    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

    def jalon_quote(self, encode):
        return jalon_utils.jalon_quote(encode)

    def jalon_unquote(self, decode):
        return jalon_utils.jalon_unquote(decode)

    def retirerEspace(self, mot):
        return jalon_utils.retirerEspace(mot)

    def getShortText( self, text, limit = 75 ):
        return jalon_utils.getShortText( text, limit )

    #   Suppression marquage HTML
    def supprimerMarquageHTML(self, chaine):
        return jalon_utils.supprimerMarquageHTML(chaine)

    def majBoite(self):
        """ Pour utiliser cette fonction :
                1 - décommenter import ATExtensions puis RecordField infos_element
                2 - mettre getInfosElement en commentaire
                3 - appeler cette fonction depuis un script en ZMI"""
        listeSujets = list(self.getListeSujets())
        listeDevoirs = list(self.getListeDevoirs())
        listeCorrections = list(self.getListeCorrections())
        listeSujets.extend(listeDevoirs)
        listeSujets.extend(listeCorrections)

        infos_element = self.getInfosElement()
        if infos_element:
            dico = {}
            dicoElements = copy.deepcopy(infos_element)
            for idElement in listeSujets:
                if idElement in dicoElements:
                    dico[idElement] = {"titreElement":     dicoElements[idElement]["titreElement"],
                                        "typeElement":     dicoElements[idElement]["typeElement"],
                                        "createurElement": dicoElements[idElement]["createurElement"],
                                        "affElement":      dicoElements[idElement]["affElement"],
                                        "masquerElement":  dicoElements[idElement]["masquerElement"]}
            self.setInfosElement(dico)

registerATCT(JalonBoiteDepot, PROJECTNAME)
