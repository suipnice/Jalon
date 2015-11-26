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
import os
import copy

# Messages de debug :
#from logging import getLogger
#LOG = getLogger( '[JalonBoiteDepot]' )

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

    ##-------------------##
    # Fonctions générales #
    ##-------------------##
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

    def getAttributsMod(self, info):
        dico = {"info":  ['title', 'description'],
                "date":  ['dateDepot', 'dateRetard']}
        return dico[info]

    def setProperties(self, dico):
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        self.reindexObject()

    def getListeAttribut(self, attribut):
        return self.__getattribute__("liste%s" % attribut.capitalize())

    def getInfosListeAttribut(self, attribut, personnel=False):
        retour = []
        listeElement = self.getListeAttribut(attribut)
        infos_element = self.getInfosElement()
        for idElement in listeElement:
            infos = infos_element.get(idElement, '')
            if infos:
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

    def setAttributActivite(self, form):
        if "DateDepot" in form and form["DateDepot"] != self.getDateDepot():
            self.aq_parent.setActuCours({"reference": self.getId(),
                                         "code":      "datedepot",
                                         "dateDepot": form["DateDepot"]})
        self.setProperties(form)
        if "Title" in form:
            self.aq_parent.modifierInfosElementPlan(self.getId(), form["Title"])
        self.reindexObject()

    def getAffDate(self, attribut):
        if attribut == "DateDepot":
            date = self.dateDepot
        if attribut == "DateRetard":
            date = self.dateRetard
        if not date:
            return "Aucune date limite de dépôt."
        else:
            return jalon_utils.getLocaleDate(date, '%d %B %Y - %Hh%M')

    def getNbSujets(self):
        return len(self.getInfosListeAttribut("sujets", True))

    def getOptionsAvancees(self):
        options = {}
        for option in ["getCorrectionIndividuelle", "getNotificationCorrection", "getNotation", "getNotificationNotation", "getAccesDepots", "getAccesCompetences"]:
            if self.__getattribute__(option)():
                options[option] = {"actif": 1, "texte": _(u"Activée")}
            else:
                options[option] = {"actif": 0, "texte": _(u"Désactivée")}
        return options

    def getRubriqueEspace(self, ajout=None):
        return self.aq_parent.getRubriqueEspace(ajout)

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

    def getTemplateView(self, user, mode_etudiant, menu):
        is_anonymous = user.has_role('Anonymous')
        if is_anonymous:
            return {"is_anonymous": True}

        personnel = self.isPersonnel(user, mode_etudiant)
        affElement = self.isAfficherElement(self.getDateAff(), self.getDateMasq())

        id_boite = self.getId()
        url_boite = self.absolute_url()

        menu_options = []
        if affElement["val"]:
            menu_options.append({"href": "%s/folder_form?macro=macro_cours_afficher&amp;formulaire=masquer-element&amp;idElement=%s" % (url_boite, id_boite),
                                 "icon": "fa-eye-slash",
                                 "text": "Masquer"})
        else:
            menu_options.append({"href": "%s/folder_form?macro=macro_cours_afficher&amp;formulaire=afficher-element&amp;idElement=%s" % (url_boite, id_boite),
                                 "icon": "fa-eye",
                                 "text": "Afficher"})
        menu_options.append({"href": "%s/%s/folder_form?macro=macro_cours_boite&amp;formulaire=modifier-boite-info&amp;menu=%s" % (url_boite, id_boite, menu),
                             "icon": "fa-align-justify",
                             "text": "Titre et consigne"})

        onglets = []
        is_onglet_depots = True if menu == "depots" else False
        onglets.append({"href":      "%s?menu=depots&amp;mode_etudiant=%s" % (url_boite, mode_etudiant),
                        "css_class": " selected" if is_onglet_depots else "",
                        "icon":      "fa-download",
                        "text":      "Mes dépôts" if not personnel and not self.getAccesDepots() else "Dépôts étudiants",
                        "nb":        self.getNbDepots(personnel)})
        menu_option_depots = []
        if is_onglet_depots:
            menu_option_depots.append({"icon": "fa-toggle-on success" if self.getCorrectionIndividuelle() else "fa-toggle-off",
                                       "text": "Correction des dépôts"})
            menu_option_depots.append({"icon": "fa-toggle-on success" if self.getNotificationCorrection() else "fa-toggle-off",
                                       "text": "Notification des corrections"})
            menu_option_depots.append({"icon": "fa-toggle-on success" if self.getNotation() else "fa-toggle-off",
                                       "text": "Notation des dépôts"})
            menu_option_depots.append({"icon": "fa-toggle-on success" if self.getNotificationNotation() else "fa-toggle-off",
                                       "text": "Notification des notations"})
            menu_option_depots.append({"icon": "fa-toggle-on success" if self.getAccesDepots() else "fa-toggle-off",
                                       "text": "Visualisation des dépôts entre étudiants"})

        onglets.append({"href":      "%s?menu=sujets&amp;mode_etudiant=%s" % (url_boite, mode_etudiant),
                        "css_class": " selected" if menu == "sujets" else "",
                        "icon":      "fa-upload",
                        "text":      "Documents enseignants",
                        "nb":        self.getNbSujets()})

        is_onglet_competences = True if menu == "competences" else False
        if personnel or self.getAfficherCompetences():
            onglets.append({"href":      "%s?menu=competences&amp;mode_etudiant=%s" % (url_boite, mode_etudiant),
                            "css_class": " selected" if is_onglet_competences else "",
                            "icon":      "fa-tasks",
                            "text":      "Compétences",
                            "nb":        self.getNbCompetences()})
        menu_option_competences = []
        if is_onglet_competences:
            menu_option_competences.append({"icon": "fa-toggle-on success" if self.getAfficherCompetences() else "fa-toggle-off",
                                            "text": "Affichage de l'onglet \"Compétences\" aux étudiants"})
            if self.getPermissionModifierCompetence(personnel, user.getId()):
                menu_option_competences.append({"icon": "fa-toggle-on success" if self.getModifierCompetences() else "fa-toggle-off",
                                                "text": "Restriction de la gestion des compétences"})

        instructions = []
        instructions.append({"href":      "%s/%s/folder_form?macro=macro_cours_boite&amp;formulaire=modifier-boite-date&amp;menu=%s" % (url_boite, id_boite, menu),
                             "icon":      "fa-calendar",
                             "text":      "Date"})
        instructions.append({"href":      "%s/%s/folder_form?macro=macro_cours_boite&amp;formulaire=modifier-boite-info&amp;menu=%s" % (url_boite, id_boite, menu),
                             "icon":      "fa-align-justify",
                             "text":      "Titre et consigne"})

        is_depot_actif = self.isDepotActif()
        if is_depot_actif == 2:
            is_retard = True
            class_limit_date = "callout"
        else:
            is_retard = False
            class_limit_date = "warning"

        return {"id_boite":                      id_boite,
                "url_boite":                     url_boite,
                "is_anonymous":                  False,
                "is_personnel":                  personnel,
                "is_etu_and_boite_hidden":       True if (not personnel) and affElement['val'] == 0 else False,
                "is_personnel_or_boite_visible": True if personnel or affElement['val'] != 0 else False,
                "is_auteur":                     self.isAuteurs(user.getId()),
                "is_depot_actif":                is_depot_actif,
                "is_retard":                     is_retard,
                "is_afficher_comp":              self.getAfficherCompetences(),
                "menu_options":                  menu_options,
                "affElement":                    affElement,
                "came_from":                     "%s/login_form?came_from=%s" % (url_boite, self.jalon_quote(url_boite)),
                "class_limit_date":              class_limit_date,
                "date_depot_aff":                self.getAffDate('DateDepot'),
                "onglets":                       onglets,
                "instructions":                  instructions,
                "description":                   self.Description(),
                "is_onglet_depots":              is_onglet_depots,
                "menu_option_depots":            menu_option_depots,
                "is_onglet_competences":         is_onglet_competences,
                "menu_option_competences":       menu_option_competences}

    ##-----------------------##
    # Fonctions onglet Dépots #
    ##-----------------------##
    def getDepots(self, auth_member, is_personnel, is_depot_actif, is_retard):
        valides = 0
        liste_depots = []
        liste_etudiants = []
        liste_etudiants_valides = []
        dico_name_etudiants = {}
        auth_member_id = auth_member.getId()

        menus = []
        if is_personnel:
            menus.append({"href": "%s/cours_telecharger_depots" % self.absolute_url(),
                         "icon": "fa-file-archive-o",
                         "text": "Télécharger les dépôts (ZIP)"})
            menus.append({"href": "%s/cours_listing_depots" % self.absolute_url(),
                         "icon": "fa-list",
                         "text": "Télécharger listing"})
            menus.append({"href": "%s/folder_form?macro=macro_cours_boite&amp;formulaire=purger_depots" % self.absolute_url(),
                         "icon": "fa-filter",
                         "text": "Purger les dépôts"})

        table_title = "Dépôts étudiants"
        content_filter = {"portal_type": "JalonFile"}
        acces_depots = self.getAccesDepots()
        if not is_personnel and not acces_depots:
            table_title = "Mes dépôts"
            content_filter["Creator"] = auth_member_id
        depots = self.getFolderContents(contentFilter=content_filter)

        if not depots:
            return {"table_title":     table_title,
                    "is_infos_depots": False,
                    "infos_depots":    "",
                    "liste_depots":    [],
                    "acces_depots":    acces_depots,
                    "menus":           menus}

        is_corriger_noter = self.isCorrigerNoter()
        for depot in depots:
            # créateur du dépôt = etudiant
            depot_id = depot.getId
            etudiant_id = str(depot.Creator)
            if not etudiant_id in liste_etudiants:
                liste_etudiants.append(etudiant_id)
                etudiant_infos = jalon_utils.getInfosMembre(etudiant_id)
                if etudiant_infos:
                    etudiant_name = "%s %s" % (etudiant_infos["nom"], etudiant_infos["prenom"])
                else:
                    etudiant_name = etudiant_id
                dico_name_etudiants[etudiant_id] = etudiant_name
            else:
                etudiant_name = dico_name_etudiants[etudiant_id]

            columns_etat_correction_notation = []

            is_valide = {"value": False, "test": "is_column_etat", "css_class": "valide", "span_css_class": "label warning", "text": "Invalide"}
            if depot.getActif:
                is_valide = {"value": True, "test": "is_column_etat", "css_class": "valide", "span_css_class": "label success", "text": "Valide"}
                valides = valides + 1
                if not etudiant_id in liste_etudiants_valides:
                    liste_etudiants_valides.append(etudiant_id)
            columns_etat_correction_notation.append(is_valide)

            is_correction = {"value": False, "test": "is_column_correction", "css_class": "correction", "span_css_class": "label secondary", "text": "Non corrigé"}
            if depot.getCorrection not in ["", None, " "]:
                is_correction = {"value": True, "test": "is_column_correction", "css_class": "correction", "span_css_class": "label success", "text": "Corrigé"}
            if depot.getFichierCorrection:
                is_correction = {"value": True, "test": "is_column_correction", "css_class": "correction", "span_css_class": "label success", "text": "Corrigé"}
            columns_etat_correction_notation.append(is_correction)

            note = depot.getNote
            is_notation = {"value": False, "test": "is_column_notation", "css_class": "note", "span_css_class": "label secondary", "text": "Non noté"}
            if note:
                is_notation = {"value": True, "test": "is_column_notation", "css_class": "note", "span_css_class": "", "text": note}
            columns_etat_correction_notation.append(is_notation)

            is_corrupt = False
            depot_action = {"action_title": "Consulter",
                            "action_url":   "%s/cours_element_view?idElement=%s&amp;typeElement=JalonFile&amp;createurElement=%s&indexElement=0" % (self.absolute_url(), depot_id, etudiant_id),
                            "action_icon":  "fa-eye",
                            "action_text":  "Consulter"}
            if etudiant_id == auth_member_id:
                if depot.getObject().getSize() < 100:
                    is_corrupt = True
                if not is_correction["value"] or not is_notation["value"]:
                    if not is_valide["value"]:
                        depot_action = {"action_title": "Valider ce dépôt",
                                        "action_url":   "%s/cours_activer_depot?idElement=%s&amp;actif=" % (self.absolute_url(), depot_id),
                                        "action_icon":  "fa-check-circle success",
                                        "action_text":  "Valider"}
                    else:
                        depot_action = {"action_title": "Ignorer ce dépôt",
                                        "action_url":   "%s/cours_activer_depot?idElement=%s&amp;actif=actif" % (self.absolute_url(), depot_id),
                                        "action_icon":  "fa-times-circle warning",
                                        "action_text":  "Ignorer"}
            if is_personnel and is_corriger_noter:
                depot_action = {"action_title": is_corriger_noter["title"],
                                "action_url":   "%s/%s/folder_form?macro=macro_cours_boite&amp;formulaire=modifier-correction" % (self.absolute_url(), depot_id),
                                "action_icon":  "fa-legal",
                                "action_text":  is_corriger_noter["title"]}

            creation_date = self.getLocaleDate(depot.created, '%d/%m/%Y - %Hh%M')

            liste_depots.append({"etudiant_name":                    etudiant_name,
                                 "depot_id":                         depot_id,
                                 "depot_title":                      depot.Title,
                                 "depot_date":                       creation_date,
                                 "depot_url":                        depot.getURL(),
                                 "date_sort":                        self.getDepotDate(creation_date, 1),
                                 "date_aff":                         self.getDepotDate(creation_date),
                                 "is_corrupt":                       is_corrupt,
                                 "columns_etat_correction_notation": columns_etat_correction_notation,
                                 "depot_action":                     depot_action})

        infos_depots = {}
        is_infos_depots = False
        if is_personnel:
            if len(liste_depots):
                is_infos_depots = True
                infos_depots["css_class"] = "callout"
                text_infos_depots = ["Il y a actuellement"]
                if valides == 1:
                    text_infos_depots.append("<strong>%s</strong> dépôt valide envoyé par" % valides)
                else:
                    text_infos_depots.append("<strong>%s</strong> dépôts valides envoyés par" % valides)
                taille_liste_etudiants_valides = len(liste_etudiants_valides)
                if taille_liste_etudiants_valides == 1:
                    text_infos_depots.append("<strong>%s</strong> étudiant." % taille_liste_etudiants_valides)
                else:
                    text_infos_depots.append("<strong>%s</strong> étudiant." % taille_liste_etudiants_valides)
                infos_depots["text"] = " ".join(text_infos_depots)
        else:
            if not is_depot_actif:
                is_infos_depots = True
                infos_depots = {"css_class": "warning",
                                "text":      "<i class=\"fa fa-warning\"></i>La date limite autorisée a été dépassée. Vous ne pouvez plus déposer."}
            if is_retard:
                is_infos_depots = True
                infos_depots = {"css_class": "warning",
                                "text":      "<i class=\"fa fa-warning\"></i>Vous êtes en retard. Dernières minutes avant la fermeture des dépôts."}

        retour = {"table_title":     table_title,
                  "is_infos_depots": is_infos_depots,
                  "infos_depots":    infos_depots,
                  "liste_depots":    liste_depots,
                  "acces_depots":    acces_depots,
                  "menus":           menus}
        return retour

    def getInfosTableau(self, is_personnel, is_depot_actif):
        head_table = []
        is_column_correction = self.getCorrectionIndividuelle()
        is_column_notation = self.getNotation()
        #is_personnel_and_is_actions = True if is_personnel and (is_colmun_correction or is_colmun_notation) else False
        is_colmun_etudiant = True if is_personnel or self.getAccesDepots() else False
        if is_colmun_etudiant:
            head_table.append({"css_class":    "sort text-left has-tip",
                               "attr_title":   "Cliquer pour trier selon l'étudiant",
                               "data-sort":    "name",
                               "column_title": "Étudiant"})
        head_table.append({"css_class":    "sort text-left has-tip",
                           "attr_title":   "Cliquer pour trier selon la date",
                           "data-sort":    "title",
                           "column_title": "Dépôt"})
        head_table.append({"css_class":    "sort text-left has-tip",
                           "attr_title":   "Cliquer pour trier selon l'état",
                           "data-sort":    "valide",
                           "column_title": "État"})
        if is_column_correction:
            head_table.append({"css_class":    "sort text-left has-tip",
                               "attr_title":   "Cliquer pour trier selon la correction",
                               "data-sort":    "correction",
                               "column_title": "Correction"})
        if is_column_notation:
            head_table.append({"css_class":    "sort text-left has-tip",
                               "attr_title":   "Cliquer pour trier selon la note",
                               "data-sort":    "note",
                               "column_title": "Note"})
        #if is_personnel_and_is_actions:
        #    head_table.append({"css_class":    "nosort",
        #                       "attr_title":   "",
        #                       "data-sort":    "",
        #                       "column_title": "<i class=\"fa fa-cog\"></i>"})

        is_column_actions = False
        if is_personnel:
            if is_column_correction or is_column_notation:
                is_column_actions = True
        else:
            if is_depot_actif:
                is_column_actions = True
            if is_column_correction:
                is_column_actions = True
        if is_column_actions:
            head_table.append({"css_class":    "nosort",
                               "attr_title":   "",
                               "data-sort":    "",
                               "column_title": "<i class=\"fa fa-cog\"></i>"})
        return {"head_table":           head_table,
                "is_column_etudiant":   is_colmun_etudiant,
                "is_column_etat":       True,
                "is_column_correction": is_column_correction,
                "is_column_notation":   is_column_notation,
                "is_column_actions":    is_column_actions,
                "option":               self.getOptionsAvancees()}
        #        "is_personnel_and_is_actions": is_personnel_and_is_actions,

    def getDepotDate(self, data, sortable=False):
        return jalon_utils.getDepotDate(data, sortable)

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

    def getNbDepots(self, is_personnel):
        if not is_personnel and not self.getAccesDepots():
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

    def activerDepot(self, idDepot, actif):
        depot = getattr(self, idDepot)
        depot.setProperties({"Actif": actif})

    def purgerDepots(self):
        self.manage_delObjects(self.objectIds())
        self.setListeDevoirs(())
        self.setCompEtudiants({})
        self.reindexObject()

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

    ##----------------------------##
    # Fonctions onglet Compétences #
    ##----------------------------##
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

    def getNbCompetences(self):
        return len(self._competences.keys())

    def getPermissionModifierCompetence(self, personnel, user_id):
        if not personnel:
            return False
        elif user_id == self.Creator():
            return True
        elif self.getModifierCompetences():
            return False
        else:
            return True

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
                        ligne1.write(index_comp, 'À acquérir', styleAcquerir)
                    index_comp = index_comp + 1
            i = i + 1

        listing.save(path)

        fp = open(path, 'rb')
        data = fp.read()
        fp.close()
        return {"length": str(os.stat(path)[6]), "data": data}

    ##-----------------------------##
    # Fonctions appel à jalon_utils #
    ##-----------------------------##
    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

    def ajouterTag(self, tag):
        return jalon_utils.setTag(self, tag)

    def getTagDefaut(self):
        return jalon_utils.getTagDefaut(self)

    def isLDAP(self):
        return jalon_utils.isLDAP()

    def isAfficherElement(self, affElement, masquerElement):
        return jalon_utils.isAfficherElement(affElement, masquerElement)

    def getLocaleDate(self, date, format="%d/%m/%Y"):
        return jalon_utils.getLocaleDate(date, format)

    def jalon_quote(self, encode):
        return jalon_utils.jalon_quote(encode)

    def jalon_unquote(self, decode):
        return jalon_utils.jalon_unquote(decode)

    def retirerEspace(self, mot):
        return jalon_utils.retirerEspace(mot)

    def getShortText(self, text, limit=75):
        return jalon_utils.getShortText(text, limit)

    #   Suppression marquage HTML
    def supprimerMarquageHTML(self, chaine):
        return jalon_utils.supprimerMarquageHTML(chaine)

registerATCT(JalonBoiteDepot, PROJECTNAME)
