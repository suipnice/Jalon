# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.Archetypes.public import *
# from Products.ATExtensions.ateapi import *

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
from jalon_activity import JalonActivity
import os
import copy
import random
import string

# Messages de debug :
from logging import getLogger
LOG = getLogger("[JalonBoiteDepot]")

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
                widget=StringWidget(label=_(u"Date de masquage de la boite de dépôts"),)),
    StringField("profile",
                required=False,
                accessor="getProfile",
                default="standard",
                searchable=False,
                widget=StringWidget(label=_(u"Profil de la boite de dépots"),)),
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
                 widget=BooleanWidget(label=_(u"Restreindre la modification des compétences au créateur de la boite de dépôts"),)),
    DateTimeField("dateCorrection",
                  required=False,
                  accessor="getDateCorrection",
                  searchable=False,
                  widget=CalendarWidget(label=_(u"Date limite de correction"),)),
    IntegerField("nombreCorrection",
                 required=False,
                 accessor="getNombreCorrection",
                 default=2,
                 searchable=False,
                 widget=IntegerWidget(label=_(u"Nombre de correction"),)),
    StringField("penalite",
                required=False,
                accessor="getPenalite",
                default="none",
                searchable=False,
                widget=StringWidget(label=_(u"Pénalité"),)),
    IntegerField("adjustementPoints",
                 required=False,
                 accessor="getAdjustementPoints",
                 default=2,
                 searchable=False,
                 widget=IntegerWidget(label=_(u"Nombre de points d'ajustement"),)),
    BooleanField("accesGrille",
                 required=False,
                 accessor="getAccesGrille",
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Accéder à la grille d'évaluation avant d'évaluer"),)),
    BooleanField("accesEvaluation",
                 required=False,
                 accessor="getAccesEvaluation",
                 default=False,
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Autoriser les étudiants à voir les résultats des évaluations"),)),
    BooleanField("autoriserAutoEvaluation",
                 required=False,
                 accessor="getAutoriserAutoEvaluation",
                 default=False,
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Autoriser les étudiants à réaliser une auto-évaluation"),)),
    BooleanField("affectationEvaluation",
                 required=False,
                 accessor="getAffectationEvaluation",
                 default=False,
                 searchable=False,
                 widget=BooleanWidget(label=_(u"Indique si l'affectation des évaluations a été faite."),)),
))


class JalonBoiteDepot(JalonActivity, ATFolder):
    u"""Une boite de dépôts pour Jalon."""

    implements(IJalonBoiteDepot)
    meta_type = 'JalonBoiteDepot'
    schema = JalonBoiteDepotSchema
    schema['description'].required = False
    schema['description'].widget.label = "Consigne"
    schema['description'].widget.description = ""

    _infos_element = {}
    _competences = {}
    _comp_etudiants = {}
    _crietria_dict = {}
    _peers_dict = {}

    _penality_title = {"none":     "Aucun",
                       "negative": "points en moins si évaluations non réalisées",
                       "positive": "points en plus si évaluations réalisées"}

    _profile_title = {"standard":    "Standard",
                      "examen":      "Examen",
                      "competences": "Évaluation par compétences",
                      "pairs":       "Évaluation par les pairs"}

    def __init__(self, *args, **kwargs):
        super(JalonBoiteDepot, self).__init__(*args, **kwargs)
        super(ATFolder, self).__init__(*args, **kwargs)
        self.setDocumentsProperties({})

    # #-------------------# #
    #  Fonctions générales  #
    # #-------------------# #

    def addMySpaceItem(self, folder_object, item_id, item_type, user_id, display_item, map_position, display_in_plan, portal_workflow):
        """addMySpaceItem."""
        item = super(JalonBoiteDepot, self).addMySpaceItem(folder_object, item_id, item_type, user_id, display_item, map_position, display_in_plan, portal_workflow)
        self.addItemProperty(item["item_id_no_dot"], item["item_type"], item["item_title"], user_id, display_item, item["item_complement"])

    def getDisplayProfile(self, profile_id=None):
        # LOG.info("----- getDisplayProfile -----")
        deposit_box_profil = profile_id or self.getProfile() or "standard"
        return self._profile_title[deposit_box_profil]

    def getDocumentsList(self):
        # LOG.info("----- getDocumentsList -----")
        return self._infos_element.keys()

    def setDocumentsProperties(self, infos_element):
        if type(self._infos_element).__name__ != "PersistentMapping":
            self._infos_element = PersistentDict(infos_element)
        else:
            self._infos_element = infos_element

    def getAttributsMod(self, info):
        dico = {"info":  ['title', 'description'],
                "date":  ['dateDepot', 'dateRetard']}
        return dico[info]

    def getDepositBoxProperty(self, property_name):
        # LOG.info("----- getDepositBoxProperty -----")
        return getattr(self, property_name, None)

    def setProperties(self, dico):
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        self.reindexObject()

    def getListeAttribut(self, attribut):
        return self.__getattribute__("liste%s" % attribut.capitalize())

    def getInfosListeAttribut(self, attribut, personnel=False):
        retour = []
        listeElement = self.getListeAttribut(attribut)
        infos_element = self.getDocumentsProperties()
        # LOG.info(infos_element)
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

    def isPersonnel(self, user, mode_etudiant="false"):
        # LOG.info("----- isPersonnel -----")
        if mode_etudiant == "true":
            # isPersonnel = False (mode étudiant)
            return False
        if user.has_role("Manager"):
            # isPersonnel = True (manager role)
            return True
        if user.has_role("Personnel") and self.isCoAuteurs(user.getId()):
            # isPersonnel = True (Personnel & iscoAuteurs)
            return True
        return False

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
        date = getattr(self, attribut, None)
        if not date:
            return "Aucune date limite de dépôt."
        else:
            return jalon_utils.getLocaleDate(date, '%d %B %Y - %Hh%M')

    def getNbSujets(self, is_personnel=False):
        return len(self.getInfosListeAttribut("sujets", is_personnel))

    def getDepositFileOptions(self):
        options = {}
        for option in ["getCorrectionIndividuelle", "getNotificationCorrection", "getNotation", "getNotificationNotation", "getAccesDepots", "getAccesCompetences"]:
            if self.__getattribute__(option)():
                options[option] = {"actif": 1, "texte": _(u"Activée")}
            else:
                options[option] = {"actif": 0, "texte": _(u"Désactivée")}
        return options

    """
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
    """

    def getIconClass(self):
        """Return the Activity icon CSS class."""
        # LOG.info("----- getIconClass -----")
        return "fa fa-inbox"

    def getDepositBoxProfile(self):
        # LOG.info("----- getDepositBoxProfile -----")
        deposit_box_profil = self.getProfile() or "standard"
        # LOG.info("***** deposit_box_profil : %s" % deposit_box_profil)
        return [{"deposit_box_profile_text":    "Standard",
                 "deposit_box_profile_value":   "standard",
                 "deposit_box_profile_checked": "selected" if deposit_box_profil == "standard" else "",
                 "deposit_box_profile_help":    "Les étudiants peuvent avoir autant de fichiers actifs qu'ils le désirent, les télécharger et les invalider. La date limite de dépôts est facultative."},
                {"deposit_box_profile_text":    "Examen",
                 "deposit_box_profile_value":   "examen",
                 "deposit_box_profile_checked": "selected" if deposit_box_profil == "examen" else "",
                 "deposit_box_profile_help":    "Les étudiants ne peuvent avoir qu'un seul fichier actif. Ils ne peuvent pas télécharger les fichiers qu'ils ont déposé. La date limite de dépôts est facultative."},
                {"deposit_box_profile_text":    "Évaluation par compétences",
                 "deposit_box_profile_value":   "competences",
                 "deposit_box_profile_checked": "selected" if deposit_box_profil == "competences" else "",
                 "deposit_box_profile_help":    "Les étudiants ne peuvent avoir qu'un seul fichier actif. La date limite de dépôts est facultative. Vous pouvez créer et évaluer vos étudiants à l'aide d'une grille de compétences accessible depuis l'onglet Compétences."},
                {"deposit_box_profile_text":    "Évaluation par les pairs",
                 "deposit_box_profile_value":   "pairs",
                 "deposit_box_profile_checked": "selected" if deposit_box_profil == "pairs" else "",
                 "deposit_box_profile_help":    "Les étudiants ne peuvent avoir qu'un seul fichier actif. À partir de l'onglet Par les pairs, vous pourrez créer une grille d'évaluations et demander à vos étudiants d'évaluer leurs pairs. Les dates limites de dépots et d'évaluation sont obligatoires."}]

    def isExamen(self):
        # LOG.info("----- isExamen -----")
        return True if self.getProfile() == "examen" else False

    def isNotStandard(self):
        # LOG.info("----- isNotStandard -----")
        return True if self.getProfile() != "standard" else False

    # #-----------------------# #
    #  Fonctions onglet Dépots  #
    # #-----------------------# #

    def addDepositFile(self, deposit_title, desposit_comment, deposit_file, user_id):
        # LOG.info("----- addDepositFile -----")
        if self.isNotStandard():
            content_filter = {"portal_type": "JalonFile", "Creator": user_id}
            depots = self.getFolderContents(contentFilter=content_filter)
            for depot_brain in depots:
                depot = depot_brain.getObject()
                # LOG.info("***** object_id : %s" % depot.getId())
                depot.setProperties({"Actif": ""})

        part1 = ''.join([random.choice(string.ascii_lowercase) for i in range(3)])
        part2 = ''.join([random.choice(string.digits[1:]) for i in range(3)])
        file_id = "Depot-%s%s-%s" % (part1, part2, DateTime().strftime("%Y%m%d%H%M%S"))
        self.invokeFactory(type_name='JalonFile', id=file_id)

        deposit_object = getattr(self, file_id)
        deposit_object.setProperties({"Title":       deposit_title,
                                      "Description": desposit_comment,
                                      "File":        deposit_file})
        self.aq_parent.setActuCours({"reference": self.getId(),
                                     "code":      "nouveauxdepots"})

        comp_etudiants = dict(self.getCompEtudiants())
        listeEtu = comp_etudiants.keys()
        if not user_id in listeEtu:
            comp_etudiants[user_id] = {}
            self.setCompEtudiants(comp_etudiants)

        peers_dict = dict(self.getPeersDict())
        peers_list = peers_dict.keys()
        if not user_id in peers_list:
            peers_dict[user_id] = []
            self.setPeersDict(peers_dict)

    def getDepots(self, auth_member, is_personnel, is_depot_actif, is_retard):
        valides = 0
        liste_depots = []
        liste_etudiants = []
        liste_etudiants_valides = []
        dico_name_etudiants = {}
        auth_member_id = auth_member.getId()
        is_not_standard = self.isNotStandard()

        menus = []
        if is_personnel:
            menus.append({"href": "%s/download_deposit_zip_form" % self.absolute_url(),
                          "icon": "fa-file-archive-o",
                          "text": "Télécharger les dépôts (ZIP)"})
            menus.append({"href": "%s/download_deposit_list_form" % self.absolute_url(),
                          "icon": "fa-list",
                          "text": "Télécharger listing"})
            menus.append({"href": "%s/delete_deposit_files_form" % self.absolute_url(),
                          "icon": "fa-trash-o alert",
                          "text": "Supprimer les dépôts"})

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
                etudiant_name = self.getIndividu(etudiant_id, "dict")["fullname"]
                #if etudiant_infos:
                #    etudiant_name = "%s %s" % (etudiant_infos["nom"], etudiant_infos["prenom"])
                #else:
                #    etudiant_name = etudiant_id
                dico_name_etudiants[etudiant_id] = etudiant_name
            else:
                etudiant_name = dico_name_etudiants[etudiant_id]

            columns_etat_correction_notation = []

            is_valide = {"value": False, "test": "is_column_etat", "css_class": "valide", "span_css_class": "label warning", "text": "Invalide"}
            if depot.getActif:
                # LOG.info("getActif : %s" % depot.getActif)
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
                            "action_url":   "%s/%s" % (self.absolute_url(), depot_id),
                            "action_icon":  "fa-eye",
                            "action_text":  "Consulter"}
            if etudiant_id == auth_member_id:
                if depot.getObject().getSize() < 100:
                    is_corrupt = True
                if not is_not_standard:
                    if not (is_correction["value"] or is_notation["value"]):
                        depot_action = {"action_title": "Modifier l'état ce dépôt",
                                        "action_url":   "%s/edit_validate_deposit_form" % depot.getURL(),
                                        "action_icon":  "fa-pencil",
                                        "action_text":  "Modifier"}
            if is_personnel and is_corriger_noter:
                depot_action = {"action_title": is_corriger_noter["title"],
                                "action_url":   "%s/%s/correct_and_evaluate_deposit_file_form" % (self.absolute_url(), depot_id),
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
                               "attr_title":   "Trier selon l'étudiant",
                               "data-sort":    "name",
                               "column_title": "Étudiant"})
        head_table.append({"css_class":    "sort text-left has-tip",
                           "attr_title":   "Trier selon la date",
                           "data-sort":    "title",
                           "column_title": "Dépôt"})
        head_table.append({"css_class":    "sort text-left has-tip",
                           "attr_title":   "Trier selon l'état",
                           "data-sort":    "valide",
                           "column_title": "État"})
        if is_column_correction:
            head_table.append({"css_class":    "sort text-left has-tip",
                               "attr_title":   "Trier selon la correction",
                               "data-sort":    "correction",
                               "column_title": "Correction"})
        if is_column_notation:
            head_table.append({"css_class":    "sort text-left has-tip",
                               "attr_title":   "Trier selon la note",
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
                "option":               self.getDepositFileOptions()}
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

    def getDateCorrection(self):
        try:
            return self.dateCorrection.strftime("%Y/%m/%d %H:%M")
        except:
            return DateTime().strftime("%Y/%m/%d %H:%M")
        #if not self.dateCorrection:
        #    return DateTime().strftime("%Y/%m/%d %H:%M")
        #else:
        #    return self.dateCorrection.strftime("%Y/%m/%d %H:%M")

    def isFinishDeposit(self):
        # LOG.info("----- isFinishDeposit -----")
        now = DateTime(DateTime()).strftime("%Y/%m/%d %H:%M")
        return True if now > self.getDateDepot() else False

    def isFinishEvaluation(self):
        # LOG.info("----- isFinishEvaluation -----")
        now = DateTime(DateTime()).strftime("%Y/%m/%d %H:%M")
        return True if now > self.getDateCorrection() else False

    def isPossibleAffection(self):
        # LOG.info("----- isPossibleAffection -----")
        return True if (not self.getAffectationEvaluation()) and self.getPeerLength(True, "") else False

    def getNbDepots(self, is_personnel, user_id):
        # LOG.info("----- getNbDepots -----")
        if not is_personnel and not self.getAccesDepots():
            # LOG.info("***** 1")
            #nbDepots = 0
            #authMember = self.portal_membership.getAuthenticatedMember().getId()
            #for iddepot in self.objectIds():
            #    if authMember in iddepot:
            #        nbDepots = nbDepots + 1
            #return nbDepots
            return len(self.getFolderContents(contentFilter={"portal_type": "JalonFile", "Creator": user_id}))
        return len(self.getFolderContents(contentFilter={"portal_type": "JalonFile"}))
        #depots = self.objectIds()
        #if "corrections" in depots:
        #    # LOG.info("***** 2")
        #    return len(depots) - 1
        #else:
        #    # LOG.info("***** 3")
        #    # LOG.info(depots)
        #    return len(depots)

    """
    isDepotActif renvoit :
        1 si les étudiants ont le droit de déposer.
        2 s'ils sont en retard.
        0 s'ils n'ont plus le droit.
    """
    def isDepotActif(self):
        # LOG.info("----- isDepotActif -----")
        profile = self.getProfile()
        now = DateTime(DateTime()).strftime("%Y/%m/%d %H:%M")
        date_depot = DateTime(self.getDateDepot()).strftime("%Y/%m/%d %H:%M")

        # LOG.info("***** profile : %s" % profile)
        # LOG.info("***** now : %s" % now)
        # LOG.info("***** date_depot : %s" % date_depot)
        # En profil évaluation par les pairs la date de dépôts est obligatoire
        if profile == "pairs" and date_depot == now:
            return 3

        date_correction = DateTime(self.getDateCorrection()).strftime("%Y/%m/%d %H:%M")
        # LOG.info("***** date_correction : %s" % date_correction)
        # En profil évaluation par les pairs la date de correction est obligatoire
        if profile == "pairs" and date_correction == now:
            return 3

        # La date de dépot n'est pas encore passée.
        if now <= date_depot:
            return 1

        date_retard = DateTime(self.getDateRetard()).strftime("%Y/%m/%d %H:%M")
        # La date de retard n'est pas encore passée.
        if date_retard > date_depot and now < date_retard:
            return 2
        return 0

    def isCorrigerNoter(self):
        corriger = self.getCorrectionIndividuelle()
        noter = self.getNotation()
        if corriger and noter:
            return {"title":   "Corriger et Noter",
                    "corriger": 1,
                    "noter":    1}
        if corriger:
            return {"title":   "Corriger",
                    "corriger": 1,
                    "noter":    0}
        if noter:
            return {"title":    "Noter",
                    "corriger": 0,
                    "noter":    1}

    def activerDepot(self, idDepot, actif):
        depot = getattr(self, idDepot)
        depot.setProperties({"Actif": actif})

    def purgerDepots(self):
        object_ids = [obj_brain.getId for obj_brain in self.getFolderContents(contentFilter={"portal_type": "JalonFile"})]
        self.manage_delObjects(object_ids)
        self.setListeDevoirs(())
        self.setCompEtudiants({})
        self.setPeersDict({})
        self.setProperties({"AffectationEvaluation": False})
        portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
        portal_jalon_bdd.deletePeersEvaluation(self.getId())
        self.reindexObject()

    def telechargerDepots(self, HTTP_USER_AGENT):
        LOG.info("----- telechargerDepots START -----")
        import tempfile
        fd, path = tempfile.mkstemp('.zipfiletransport')
        close(fd)

        zipFile = ZipFile(path, 'w', ZIP_DEFLATED)

        #dicoEtu = {}
        listeDepots = []
        listeEtudiants = []

        for obj_brain in self.getFolderContents(contentFilter={"portal_type": "JalonFile"}):
            obj = obj_brain.getObject()
            if obj.getActif() == "actif":
                idEtudiant = obj.Creator()
                if not idEtudiant in listeEtudiants:
                    listeEtudiants.append(idEtudiant)
                listeDepots.append({"idEtudiant": idEtudiant,
                                    "filename":   "(%s) %s" % (DateTime(obj.created()).strftime("%Y-%m-%d %Hh%Mm%Ss"), obj.file.filename),
                                    "file_data":  str(obj.file.data)})

        dicoEtudiants = jalon_utils.getIndividus(listeEtudiants, type="dict")
        LOG.info("dicoEtudiants")
        LOG.info(dicoEtudiants)
        for depot in listeDepots:
            try:
                filename_path = "%s/%s %s (%s)/%s" % (self.Title(), dicoEtudiants[depot["idEtudiant"]]["nom"].encode("utf-8"), dicoEtudiants[depot["idEtudiant"]]["prenom"].encode("utf-8"), dicoEtudiants[depot["idEtudiant"]]["num_etu"].encode("utf-8"), depot["filename"])
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
        LOG.info("----- telechargerDepots END -----")
        return {"length": str(os.stat(path)[6]), "data": data}

    def telechargerListingDepots(self, HTTP_USER_AGENT):
        # LOG.info("----- telechargerListingDepots -----")
        import tempfile
        from xlwt import Workbook

        isCorrection = self.getCorrectionIndividuelle()
        isNotation = self.getNotation()
        translation_service = getToolByName(self, 'translation_service')
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

        for obj in self.getFolderContents(contentFilter={"portal_type": "JalonFile"}):
            # LOG.info("JalonFile")
            if obj.getActif == "actif":
                # LOG.info("actif")
                idEtudiant = obj.Creator
                depot = {"idEtudiant": idEtudiant,
                         "titreDepot": obj.Title,
                         "dateDepot":  self.getLocaleDate(obj.created, '%d/%m/%Y - %Hh%M')}
                if isCorrection:
                    correction = obj.getCorrection
                    if not correction:
                        dummy = _(u"Non corrigé")
                        msg_correction = u"Non corrigé"
                        correction = translation_service.utranslate(domain='jalon.content',
                                                                    msgid=msg_correction,
                                                                    default=msg_correction,
                                                                    context=object)
                    depot["correctionDepot"] = correction
                if isNotation:
                    note = obj.getNote
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
        # LOG.info(listeEtudiants)
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

    # #----------------------------# #
    #  Fonctions onglet Compétences  #
    # #----------------------------# #
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
            ordre.append({"id":  SESAME_ETU,
                          "nom": self.getNomEtudiant(SESAME_ETU)})
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

        dicoGradation = {"acquerir":  "À acquérir",
                         "encours":   "En cours d'acquisition",
                         "partielle": "Partiellement acquis",
                         "acquise":   "Acquis"}
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

    # #------------------------# #
    #  Évaluation par les pairs  #
    # #------------------------# #
    def isEvaluationByPeers(self):
        # LOG.info("----- isEvaluationByPeers -----")
        return True if self.getProfile() == "pairs" else False

    def getAccesGrille(self, is_personnel=False):
        # LOG.info("----- getAccesGrille -----")
        try:
            return True if is_personnel else self.accesGrille
        except:
            return True if is_personnel else False

    def getEvaluationByPeers(self, user, is_personnel):
        # LOG.info("----- getEvaluationByPeers -----")
        evaluation_by_peers_dict = {}
        deposit_box_link = self.absolute_url()
        evaluation_by_peers_dict["is_evaluable"] = self.isEvaluable()
        evaluation_by_peers_dict["criteria_dict"] = self.getCriteriaDict()
        evaluation_by_peers_dict["criteria_order"] = self.getCriteriaOrder()
        if is_personnel:
            evaluation_by_peers_dict["macro_peers"] = "peers_teacher_macro"
            evaluation_by_peers_dict["table_title"] = "Évaluation par les pairs"

            evaluation_by_peers_dict["options"] = [{"text": "Affecter",
                                                    "link": "%s/affect_deposit_file_form" % deposit_box_link,
                                                    "icon": "fa fa-rss fa-fw"},
                                                   {"text": "Moyenne",
                                                    "link": "%s/average_deposit_file_form" % deposit_box_link,
                                                    "icon": "fa fa-calculator fa-fw"},
                                                   {"text": "Résultats",
                                                    "link": "%s/edit_peers_results_form" % deposit_box_link,
                                                    "icon": "fa-trophy"},
                                                   {"text": "Télécharger les notes",
                                                    "link": "%s/download_peers_results_page" % deposit_box_link,
                                                    "icon": "fa-list"}]

            #if not evaluation_by_peers_dict["criteria_dict"]:
            #    evaluation_by_peers_dict["grid_button"] = "fa fa-plus-circle fa-lg fa-fw"
            #else:
            #    evaluation_by_peers_dict["grid_button"] = "fa fa-pencil fa-lg fa-fw"
            evaluation_by_peers_dict["peers_list"] = self.getPeersOrder()
            evaluation_by_peers_dict["peers_average_dict"] = self.getAveragePeer()

            jalon_bdd = self.portal_jalon_bdd
            evaluation_by_peers_dict["evaluations_notes"] = jalon_bdd.getCountEvaluationsNotes(self.getId()).first()[0]
            evaluation_by_peers_dict["verif_evaluations_notes"] = jalon_bdd.getCountVerifEvaluationsNotes(self.getId()).first()[0]
            evaluation_by_peers_dict["evaluations_validate"] = evaluation_by_peers_dict["evaluations_notes"] - evaluation_by_peers_dict["verif_evaluations_notes"]
            # LOG.info("***** evaluations_notes : %s" % evaluation_by_peers_dict["evaluations_notes"])
            # LOG.info("***** verif_evaluations_notes : %s" % evaluation_by_peers_dict["verif_evaluations_notes"])
            # LOG.info("***** evaluations_validate : %s" % evaluation_by_peers_dict["evaluations_validate"])

            evaluations_notes_informations = jalon_bdd.getInfoEvaluationsNotes(self.getId()).first()
            if evaluations_notes_informations:
                evaluation_by_peers_dict["evaluations_notes_min"] = "%.2f" % evaluations_notes_informations[0] if evaluations_notes_informations[0] else 0
                evaluation_by_peers_dict["evaluations_notes_max"] = "%.2f" % evaluations_notes_informations[1] if evaluations_notes_informations[1] else 0
                evaluation_by_peers_dict["evaluations_notes_avg"] = "%.2f" % evaluations_notes_informations[2] if evaluations_notes_informations[2] else 0

            criteria_notes_dict = {}
            criteria_notes_informations = jalon_bdd.getInfoCriteriaNotes(self.getId())
            for criteria_note in criteria_notes_informations:
                criteria_notes_dict[criteria_note[0]] = {"min": "%.2f" % criteria_note[1],
                                                         "max": "%.2f" % criteria_note[2],
                                                         "avg": "%.2f" % criteria_note[3]}
            evaluation_by_peers_dict["criteria_notes_dict"] = criteria_notes_dict
            # LOG.info("***** criteria_notes_dict : %s" % str(criteria_notes_dict))
        else:
            evaluation_by_peers_dict["macro_peers"] = "peers_student_macro"
            evaluation_by_peers_dict["table_title"] = "Dépôts à évaluer"
            evaluation_by_peers_dict["evaluate_link"] = "%s/evaluate_deposit_file_form?mode_etudiant=true" % deposit_box_link

            user_id = user.getId()
            evaluation_number = self.getNombreCorrection()
            evaluation_by_peers_dict["evaluate_button"] = False
            evaluation_by_peers_dict["corrected_evaluation_list"] = []
            evaluation_by_peers_dict["peers_correction_indication"] = "Vous n'avez aucun dépôt à évaluer."

            evaluations_note_dict = {}
            evaluation_by_peers_dict["peers_evaluations"] = self.getPeersDict(user_id)
            if len(evaluation_by_peers_dict["peers_evaluations"]):
                number = 0
                for evaluation in evaluation_by_peers_dict["peers_evaluations"]:
                    if evaluation["corrected"]:
                        number = number + 1
                        # LOG.info("***** evaluation['corrected'] : %s" % number)
                        evaluations_note_dict[number] = evaluation.get("note", "Non renseignée")
                        # LOG.info("***** evaluations_note_dict[%s] : %s" % (number, evaluations_note_dict[number]))
                evaluation_by_peers_dict["evaluations_note_dict"] = evaluations_note_dict
                # LOG.info("evaluation_by_peers_dict['evaluations_note_dict'] : %s" % evaluation_by_peers_dict["evaluations_note_dict"])
                evaluation_by_peers_dict["peers_correction_indication"] = "Vous avez évalué %i dépôts sur les %i évaluations attendues" % (number, evaluation_number)

                if number == 0:
                    evaluation_by_peers_dict["evaluate_button_name"] = "Commencer l'évaluation des dépôts"
                    evaluation_by_peers_dict["evaluate_button"] = True
                elif number < evaluation_number and not self.isFinishEvaluation():
                    evaluation_by_peers_dict["evaluate_button_name"] = "Poursuivre l'évaluation des dépôts"
                    evaluation_by_peers_dict["evaluate_button"] = True

                evaluation_by_peers_dict["corrected_evaluation_list"] = range(1, number + 1)
                # LOG.info("***** corrected_evaluation_list : %s" % evaluation_by_peers_dict["corrected_evaluation_list"])
                #jalon_bdd = self.portal_jalon_bdd
                #corrected_evaluations_dict = {}
                #corrected_evaluations = jalon_bdd.getEvaluationByCorrectedSTU(self.getId(), user_id)
                #for criteria_id in evaluation_by_peers_dict["criteria_dict"].keys():
                #    corrected_evaluations_dict[criteria_id] = {}
                #for corrected_evaluation in corrected_evaluations.all():
                #    corrected_evaluations_dict[str(corrected_evaluation[0])][corrected_evaluation[1]] = corrected_evaluation[2]
                #evaluation_by_peers_dict["corrected_evaluations_dict"] = corrected_evaluations_dict
                # LOG.info("***** corrected_evaluations_dict : %s" % corrected_evaluations_dict)
        return evaluation_by_peers_dict

    def getCriteriaDict(self, key=None):
        # LOG.info("----- getCriteriaDict -----")
        # LOG.info("***** self._crietria_dict : %s" % str(self._crietria_dict))
        if key:
            return self._crietria_dict.get(key, None)
        return dict(self._crietria_dict)

    def setCriteriaDict(self, crietria_dict):
        # LOG.info("----- setCriteriaDict -----")
        if type(self._crietria_dict).__name__ != "PersistentMapping":
            self._crietria_dict = PersistentDict(crietria_dict)
        else:
            self._crietria_dict = crietria_dict

    def getCriteriaOrder(self):
        # LOG.info("----- getCriteriaOrder -----")
        order = self._crietria_dict.keys()
        order.sort(lambda x, y: cmp(int(x), int(y)))
        # LOG.info("***** order : %s" % str(order))
        return order

    def getPeersDict(self, key=None):
        # LOG.info("----- getPeersDict -----")
        # LOG.info("***** peers_dict : %s" % str(self._peers_dict))
        if key:
            return self._peers_dict.get(key, [])
        return self._peers_dict

    def setPeersDict(self, peers_dict):
        # LOG.info("----- setPeersDict -----")
        if type(self._peers_dict).__name__ != "PersistentMapping":
            self._peers_dict = PersistentDict(peers_dict)
        else:
            self._peers_dict = peers_dict

    def getPeersOrder(self):
        # LOG.info("----- getPeersOrder -----")
        order = []
        for SESAME_ETU in self._peers_dict.keys():
            order.append({"id":  SESAME_ETU,
                          "nom": self.getNomEtudiant(SESAME_ETU)})
        order.sort(lambda x, y: cmp(x["nom"], y["nom"]))
        return order

    def getInfosPeersDict(self):
        # LOG.info("----- getInfosPeersDict -----")
        infos_peers = {}
        for SESAME_ETU in self._peers_dict.keys():
            infos_peers[SESAME_ETU] = self.getNomEtudiant(SESAME_ETU)
        return infos_peers

    def getPeerLength(self, is_personnel, user_id):
        LOG.info("----- getPeerLength -----")
        if is_personnel:
            LOG.info("is_personnel")
            LOG.info(self._peers_dict.keys())
            return len(self._peers_dict.keys())
        else:
            LOG.info(self.getPeersDict(user_id))
            return len(self.getPeersDict(user_id))

    def getDisplayPenality(self):
        # LOG.info("----- getDisplayPenality -----")
        penality = self.getPenalite()
        if penality in ["negative", "positive"]:
            return "%i %s" % (self.getAdjustementPoints(), self._penality_title[penality])
        else:
            return self._penality_title[penality]

    def getDisplayGridAccess(self):
        # LOG.info("----- getDisplayGridAccess -----")
        return "Autorisée avant évaluation" if self.getAccesGrille() else "Interdit avant évaluation"

    def getDisplayAuthorizeSelfEvaluation(self):
        # LOG.info("----- getDisplayAuthoriezSelfEvaluation -----")
        return "Auto-évaluation possible" if self.getAutoriserAutoEvaluation() else "Pas d'auto-évaluation"

    def affectDepositFile(self):
        # LOG.info("----- affectDepositFile -----")
        peers_dict = copy.deepcopy(self._peers_dict)
        # LOG.info("INTRO peers_dict : %s" % str(peers_dict))
        peers_list = peers_dict.keys()
        # LOG.info("INTRO peers_list : %s" % str(peers_list))
        correction_file_number = self.getNombreCorrection()
        # LOG.info("INTRO correction_file_number : %s" % str(correction_file_number))
        correction_file_loop = range(0, correction_file_number)
        # LOG.info("INTRO correction_file_loop : %s" % str(correction_file_loop))

        random.shuffle(peers_list)
        # LOG.info("INTRO peers_list shulle : %s" % peers_list)

        interval_list = []
        for loop in correction_file_loop:
            new_interval = random.randint(1, len(peers_list) - 1)
            while new_interval in interval_list:
                new_interval = random.randint(1, len(peers_list) - 1)
            interval_list.append(new_interval)
        # LOG.info("INTRO interval_list : %s" % str(interval_list))

        peer_index = 0
        peers_list_len = len(peers_list)
        # LOG.info("INTRO peers_list_len : %s" % str(peers_list_len))
        for peer in peers_list:
            # LOG.info("PEER peer : %s" % peer)
            for interval in interval_list:
                peer_interval = peer_index + interval
                if peer_interval >= peers_list_len:
                    peer_interval = (peer_interval - peers_list_len)
                # LOG.info("PEER peer_interval : %s" % str(peer_interval))

                affected_peer = peers_list[peer_interval]
                # LOG.info("PEER affected_peer : %s" % affected_peer)
                try:
                    peers_dict[peer].append({"peer": affected_peer, "corrected": False, "note": "Non renseignée"})
                except:
                    peers_dict[peer] = [{"peer": affected_peer, "corrected": False, "note": "Non renseignée"}]
            peer_index = peer_index + 1

        self.setPeersDict(peers_dict)
        # LOG.info("***** FINAL peers_dict : %s" % str(peers_dict))
        self.setAttributActivite({"AffectationEvaluation": True})

    def getEvaluateDepositFileForm(self, user, mode_etudiant, student_id=None, deposit_id=None):
        # LOG.info("----- getEvaluateDepositFileForm -----")
        if deposit_id == "auto":
            student_id = deposit_id = user.getId()
        is_personnel = self.isPersonnel(user, mode_etudiant)
        mode_etudiant = "false" if (not mode_etudiant) and is_personnel else mode_etudiant
        if is_personnel:
            macro_form = "teacher_evaluate"
            my_evaluate_form = self.getTeacherEvaluateDepositFileForm(student_id)
        else:
            macro_form = "student_evaluate"
            my_evaluate_form = self.getStudentEvaluateDepositFileForm(user.getId(), deposit_id)

        return {"breadcrumbs":      self.getEvaluateBreadcrumbs(is_personnel),
                "is_personnel":     is_personnel,
                "mode_etudiant":    mode_etudiant,
                "comment_dict":     {"0": "Aucun",
                                     "1": "Optionnel",
                                     "2": "Obligatoire"},
                "is_evaluable":     self.isEvaluable(),
                "macro_form":       macro_form,
                "my_evaluate_form": my_evaluate_form}

    def getStudentEvaluateDepositFileForm(self, user_id, deposit_id=None):
        # LOG.info("----- getStudentEvaluateDepositFileForm -----")
        evaluation = {}
        criteria_evaluated_dict = {}
        peers_evaluations = self.getPeersDict(user_id)

        if not deposit_id:
            deposit_index = 1
            for corrected_evaluation in peers_evaluations:
                # LOG.info("***** corrected_evaluation : %s" % str(corrected_evaluation))
                if not corrected_evaluation["corrected"]:
                    evaluation = corrected_evaluation
                    break
                deposit_index = deposit_index + 1
            deposit_name = "le dépôt n°%i" % deposit_index
        elif user_id == deposit_id:
            evaluation["peer"] = deposit_id
            deposit_name = "mon dépôt"
        else:
            deposit_name = "le dépôt n°%i" % (int(deposit_id) + 1)
            evaluation = peers_evaluations[int(deposit_id)]
            # LOG.info("***** evaluation : %s" % str(evaluation))
            criteria_evaluated_list = self.portal_jalon_bdd.getEvaluationByCorrectedAndDepositSTU(self.getId(), user_id, evaluation["peer"])
            # LOG.info("***** criteria_evaluated_list : %s" % criteria_evaluated_list.all())
            for criteria_dict in criteria_evaluated_list.all():
                criteria_evaluated_dict[criteria_dict[0]] = {"criteria_note":    criteria_dict[1],
                                                             "criteria_comment": criteria_dict[2]}
            # LOG.info("****** criteria_evaluated_dict : %s" % criteria_evaluated_dict)

        deposit_link = ""
        if evaluation:
            deposit_files = self.getFolderContents(contentFilter={"portal_type": "JalonFile", "Creator": evaluation["peer"]})
            for deposit_brain in deposit_files:
                if deposit_brain.getActif:
                    deposit_link = deposit_brain.getURL()

        return {"deposit_name":       deposit_name,
                "evaluation":         evaluation,
                "deposit_link":       "%s/at_download/file" % deposit_link,
                "criteria_dict":      self.getCriteriaDict(),
                "criteria_order":     self.getCriteriaOrder(),
                "criteria_evaluated": criteria_evaluated_dict,
                "deposit_id":         deposit_id,
                "form_link":          "%s/evaluate_deposit_file_form" % self.absolute_url()}

    def getTeacherEvaluateDepositFileForm(self, student_id):
        # LOG.info("----- getTeacherEvaluateDepositFileForm -----")
        deposit_box_id = self.getId()
        deposit_files = self.getFolderContents(contentFilter={"portal_type": "JalonFile", "Creator": student_id})
        for deposit_brain in deposit_files:
            if deposit_brain.getActif:
                deposit_link = deposit_brain.getURL()

        jalon_bdd = self.portal_jalon_bdd

        self_evaluation_dict = {}
        self_evaluation_note = ""
        has_self_evaluation = False
        request = jalon_bdd.getSelfEvaluationNote(deposit_box_id, student_id).first()
        if request:
            has_self_evaluation = True
            self_evaluation_note = request[0]

            for line in jalon_bdd.getSelfEvaluate(deposit_box_id, student_id).all():
                self_evaluation_dict[line[0]] = {"criteria_note":    line[1],
                                                 "criteria_comment": line[-1]}

        evaluation = jalon_bdd.getPeerEvaluation(deposit_box_id, student_id)
        average = jalon_bdd.getPeerAverage(deposit_box_id, student_id)

        criteria_avg = {}
        evaluation_number = self.getNombreCorrection()
        for average_dict in average.all():
            # LOG.info("***** average_dict : %s" % str(average_dict))
            criteria_error = False
            criteria_text = ""
            criteria_style = ""
            criteria_value = []
            if average_dict[2] == 2:
                criteria_error = True
                criteria_style = "color: #f04124;"
                criteria_text = "Nombre d'évaluation attendu insuffisant : %s sur %s" % (average_dict[3], evaluation_number)
            if average_dict[2] == 3:
                criteria_error = True
                criteria_style = "color: #f04124;"
                criteria_text = "Marge dépassée entre la note minimale et la note maximale"
                criteria_value = average_dict[3].split(";")
            criteria_avg[average_dict[0]] = {"criteria_avg":     average_dict[1],
                                             "criteria_value":   criteria_value,
                                             "criteria_error":   criteria_error,
                                             "criteria_style":   criteria_style,
                                             "criteria_text":    criteria_text,
                                             "criteria_note":    average_dict[1],
                                             "criteria_comment": average_dict[-1]}
        # LOG.info("***** criteria_avg : %s" % str(criteria_avg))

        criteria_eval = {}
        corrected_stu_dict = {}
        portal = self.portal_url.getPortalObject()
        for evaluation_dict in evaluation.all():
            if not evaluation_dict[1] in corrected_stu_dict:
                student = self.getIndividu(evaluation_dict[1], "dict", portal)
                if student:
                    corrected_stu_dict[evaluation_dict[1]] = "%s %s" % (student["nom"].upper(), student["prenom"].capitalize())
                else:
                    corrected_stu_dict[evaluation_dict[1]] = evaluation_dict[1]

            criteria_error = True if str(evaluation_dict[2]) in criteria_avg[evaluation_dict[0]]["criteria_value"] else False
            criteria_style = "color: #f04124;" if criteria_error else ""
            try:
                criteria_eval[evaluation_dict[0]].append({"corrected_stu":    corrected_stu_dict[evaluation_dict[1]],
                                                          "criteria_note":    evaluation_dict[2],
                                                          "criteria_comment": evaluation_dict[3],
                                                          "criteria_error":   criteria_error,
                                                          "criteria_style":   criteria_style})
            except:
                criteria_eval[evaluation_dict[0]] = [{"corrected_stu":    corrected_stu_dict[evaluation_dict[1]],
                                                      "criteria_note":    evaluation_dict[2],
                                                      "criteria_comment": evaluation_dict[3],
                                                      "criteria_error":   criteria_error,
                                                      "criteria_style":   criteria_style}]
        # LOG.info("***** criteria_eval : %s" % str(criteria_eval))

        student = self.getIndividu(student_id, "dict")
        return {"student_name":         "%s %s" % (student["nom"].upper(), student["prenom"].capitalize()),
                "deposit_link":         "%s/at_download/file" % deposit_link,
                "criteria_dict":        self.getCriteriaDict(),
                "criteria_order":       self.getCriteriaOrder(),
                "has_self_evaluation":  has_self_evaluation,
                "self_evaluation_dict": self_evaluation_dict,
                "self_evaluation_note": self_evaluation_note,
                "criteria_eval":        criteria_eval,
                "criteria_avg":         criteria_avg,
                "form_link":            "%s/evaluate_deposit_file_form" % self.absolute_url()}

    def getEvaluateBreadcrumbs(self, is_personnel=False):
        # LOG.info("----- getEvaluateBreadcrumbs -----")
        portal = self.portal_url.getPortalObject()
        parent = self.aq_parent
        breadcrumbs = [{"title": _(u"Mes cours"),
                        "icon":  "fa fa-university",
                        "link":  "%s/mes_cours" % portal.absolute_url()},
                       {"title": parent.Title(),
                        "icon":  "fa fa-book",
                        "link":  parent.absolute_url()},
                       {"title": self.Title(),
                        "icon":  "fa fa-inbox",
                        "link":  "%s?tab=peers" % self.absolute_url()}]
        if is_personnel:
            breadcrumbs.append({"title": _(u"Évaluations à vérifier"),
                                "icon":  "fa fa-list",
                                "link":  "%s/deposit_box_details_evaluations_view" % self.absolute_url()})
        return breadcrumbs

    def setEvaluatePeer(self, param_dict):
        # LOG.info("----- setEvaluatePeer -----")
        user = self.portal_membership.getAuthenticatedMember()
        if self.isPersonnel(user):
            self.setTeacherEvaluatePeer(user.getId(), param_dict)
        else:
            if param_dict["deposit_id"] == param_dict["user_id"]:
                self.setAutoEvaluatePeer(param_dict)
            else:
                self.setStudentEvaluatePeer(param_dict)

    def setStudentEvaluatePeer(self, param_dict):
        # LOG.info("----- setStudentEvaluatePeer -----")
        evaluation = {}
        evaluation_note = 0
        evaluation_coeff = 0
        peers_dict = copy.deepcopy(self.getPeersDict())
        if param_dict["deposit_id"]:
            corrected_evaluation_index = int(param_dict["deposit_id"])
            evaluation = peers_dict[param_dict["user_id"]][corrected_evaluation_index]
        else:
            corrected_evaluation_index = 0
            for corrected_evaluation in peers_dict[param_dict["user_id"]]:
                if not corrected_evaluation["corrected"]:
                    evaluation = corrected_evaluation
                    break
                corrected_evaluation_index = corrected_evaluation_index + 1

        index = 1
        jalon_bdd = self.portal_jalon_bdd
        criteria_dict = self.getCriteriaDict()
        criteria_loop = param_dict["criteria_order"].split(",")
        for loop in criteria_loop:
            criteria_id = "criteria%i" % index
            criteria_coefficient = int(criteria_dict[str(param_dict[criteria_id])]["coefficient"])
            # LOG.info("***** criteria_coefficient : %s" % criteria_coefficient)

            evaluation_note = evaluation_note + (((int(param_dict["%s-note" % criteria_id]) * 10) / int(criteria_dict[str(param_dict[criteria_id])]["notation"])) * criteria_coefficient)
            evaluation_coeff = evaluation_coeff + criteria_coefficient
            jalon_bdd.setEvaluatePeer(self.getId(), evaluation["peer"], param_dict["user_id"], param_dict[criteria_id], param_dict["%s-note" % criteria_id], param_dict["%s-comment" % criteria_id])
            evaluation["corrected"] = True
            index = index + 1

        evaluation_note_20 = "%.2f" % ((float(evaluation_note) / float(evaluation_coeff)) * 2.0)

        # LOG.info("***** evaluation : %s" % str(evaluation))
        # LOG.info("***** evaluation_note : %s" % evaluation_note)
        # LOG.info("***** evaluation_coeff : %s" % evaluation_coeff)
        # LOG.info("***** evaluation_note_20 : %s" % evaluation_note_20)
        jalon_bdd.setPeerEvaluationNote(self.getId(), evaluation["peer"], param_dict["user_id"], evaluation_note_20)
        evaluation["note"] = evaluation_note_20
        peers_dict[param_dict["user_id"]][corrected_evaluation_index] = evaluation
        self.setPeersDict(peers_dict)

    def setAutoEvaluatePeer(self, param_dict):
        # LOG.info("----- setAutoEvaluatePeer -----")
        index = 1
        evaluation_note = 0
        evaluation_coeff = 0
        jalon_bdd = self.portal_jalon_bdd
        criteria_dict = self.getCriteriaDict()
        criteria_loop = param_dict["criteria_order"].split(",")
        for loop in criteria_loop:
            criteria_id = "criteria%i" % index
            criteria_coefficient = int(criteria_dict[str(param_dict[criteria_id])]["coefficient"])
            # LOG.info("***** criteria_coefficient : %s" % criteria_coefficient)

            evaluation_note = evaluation_note + (((int(param_dict["%s-note" % criteria_id]) * 10) / int(criteria_dict[str(param_dict[criteria_id])]["notation"])) * criteria_coefficient)
            evaluation_coeff = evaluation_coeff + criteria_coefficient
            jalon_bdd.setSelfEvaluate(self.getId(), param_dict["user_id"], param_dict[criteria_id], param_dict["%s-note" % criteria_id], param_dict["%s-comment" % criteria_id])
            index = index + 1

        evaluation_note_20 = "%.2f" % ((float(evaluation_note) / float(evaluation_coeff)) * 2.0)

        # LOG.info("***** evaluation_note : %s" % evaluation_note)
        # LOG.info("***** evaluation_coeff : %s" % evaluation_coeff)
        # LOG.info("***** evaluation_note_20 : %s" % evaluation_note_20)
        jalon_bdd.setSelfEvaluationNote(self.getId(), param_dict["user_id"], evaluation_note_20)

    def setTeacherEvaluatePeer(self, user_id, param_dict):
        # LOG.info("----- setTeacherEvaluatePeer -----")
        index = 1
        evaluation_note = 0
        evaluation_coeff = 0
        jalon_bdd = self.portal_jalon_bdd
        criteria_dict = self.getCriteriaDict()
        criteria_loop = param_dict["criteria_order"].split(",")
        for loop in criteria_loop:
            criteria_id = "criteria%i" % index
            criteria_coefficient = int(criteria_dict[str(param_dict[criteria_id])]["coefficient"])
            jalon_bdd.updateAveragePeer(self.getId(), param_dict["student_id"], param_dict[criteria_id], 1, "", param_dict["%s-note" % criteria_id], param_dict["%s-note" % criteria_id], param_dict["%s-comment" % criteria_id])

            #evaluation_note = evaluation_note + (int(param_dict["%s-note" % criteria_id]) * criteria_coefficient)
            evaluation_note = evaluation_note + (((int(param_dict["%s-note" % criteria_id]) * 10) / int(criteria_dict[str(param_dict[criteria_id])]["notation"])) * criteria_coefficient)
            evaluation_coeff = evaluation_coeff + criteria_coefficient
            index = index + 1

        evaluation_note_20 = "%.2f" % ((float(evaluation_note) / float(evaluation_coeff)) * 2.0)
        jalon_bdd.updateEvaluationAverage(self.getId(), param_dict["student_id"], evaluation_note_20, False)

    def setAveragePeer(self):
        # LOG.info("----- setAveragePeer -----")
        is_verification_evaluation = {}
        jalon_bdd = self.portal_jalon_bdd
        criteria_dict = self.getCriteriaDict()
        correction_number = self.getNombreCorrection()
        jalon_bdd.deleteAverageByDepositBox(self.getId())
        jalon_bdd.deleteEvaluationsAverageByDepositBox(self.getId())
        criteria_average_list = jalon_bdd.generatePeersAverage(self.getId()).all()
        for average in criteria_average_list:
            # LOG.info("***** average : %s" % str(average))
            criteria_code = 1
            criteria_value = None
            criteria_data = criteria_dict[average[1]]
            if not average[0] in is_verification_evaluation:
                is_verification_evaluation[average[0]] = False
            if average[3] < correction_number:
                criteria_code = 2
                criteria_value = average[3]
                is_verification_evaluation[average[0]] = True
            elif average[-1] - average[-2] >= int(criteria_data["gap"]):
                criteria_code = 3
                criteria_value = "%s;%s" % (average[-1], average[-2])
                is_verification_evaluation[average[0]] = True
            # LOG.info("***** criteria_code : %s" % str(criteria_code))
            # LOG.info("***** criteria_value : %s" % str(criteria_value))
            jalon_bdd.setAveragePeer(self.getId(), average[0], average[1], criteria_code, criteria_value, "%.2f" % float(average[2]), 0, "")

        # LOG.info("***** is_verification_evaluation : %s" % is_verification_evaluation)
        evaluation_average_list = jalon_bdd.generateEvaluationsAverage(self.getId()).all()
        for average in evaluation_average_list:
            # LOG.info("***** average : %s" % str(average))
            jalon_bdd.setEvaluationAverage(self.getId(), average[0], "%.2f" % float(average[1]), is_verification_evaluation[average[0]])

    def regenerateAverage(self):
        # LOG.info("----- regenerateAverage -----")
        deposit_id = self.getId()
        jalon_bdd = self.portal_jalon_bdd
        criteria_dict = self.getCriteriaDict()
        for student in self.getPeersOrder():
            evaluation_note = 0
            evaluation_coeff = 0
            evaluation_verification = False
            for criteria_id in self.getCriteriaOrder():
                criteria_coefficient = int(criteria_dict[criteria_id]["coefficient"])
                note = jalon_bdd.getCriteriaAverage(deposit_id, student["id"], criteria_id).first()
                if note:
                    evaluation_note = evaluation_note + (((note[0] * 10) / int(criteria_dict[criteria_id]["notation"])) * criteria_coefficient)
                    evaluation_coeff = evaluation_coeff + criteria_coefficient
                    if note[1] != 1:
                        evaluation_verification = True

            evaluation_note_20 = "%.2f" % ((float(evaluation_note) / float(evaluation_coeff)) * 2.0)
            jalon_bdd.updateEvaluationAverage(deposit_id, student["id"], evaluation_note_20, evaluation_verification)

        #jalon_bdd.deleteEvaluationsAverageByDepositBox(self.getId())
        #self.setAveragePeer()

    def getAveragePeer(self):
        # LOG.info("----- getAveragePeer -----")
        average_dict = {}
        jalon_bdd = self.portal_jalon_bdd
        average_list = jalon_bdd.getPeersAverage(self.getId())
        for ligne in average_list.all():
            # LOG.info("***** ligne : %s" % str(ligne))
            criteria_note = ligne[3] if ligne[2] else ligne[4]
            try:
                average_dict[ligne[0]][ligne[1]] = criteria_note
            except:
                average_dict[ligne[0]] = {ligne[1]: criteria_note}
        return average_dict

    def isEvaluable(self):
        # LOG.info("----- isEvaluable -----")
        now = DateTime(DateTime()).strftime("%Y/%m/%d %H:%M")
        date_depot = DateTime(self.getDateDepot()).strftime("%Y/%m/%d %H:%M")

        # LOG.info("***** now : %s" % now)
        # LOG.info("***** date_depot : %s" % date_depot)
        date_correction = DateTime(self.getDateCorrection()).strftime("%Y/%m/%d %H:%M")
        # LOG.info("***** date_correction : %s" % date_correction)

        # En profil évaluation par les pairs la date de correction est obligatoire
        return False if date_correction <= now else True

    def downloadPeersResults(self, HTTP_USER_AGENT):
        # LOG.info("----- downloadPeersResults -----")
        import tempfile
        from xlwt import Workbook, XFStyle, Style, Pattern

        #translation_service = getToolByName(self, 'translation_service')
        portal_membership = getToolByName(self, "portal_membership")
        authMember = portal_membership.getAuthenticatedMember()

        fd, path = tempfile.mkstemp('.%s-xlfiletransport' % authMember.getId())
        close(fd)

        # création
        listing = Workbook(encoding="utf-8")

        # création de la feuille 1
        feuil1 = listing.add_sheet('feuille 1')

        line = 1
        column = 4
        criteria_dict = self.getCriteriaDict()
        criteria_order = self.getCriteriaOrder()
        criteria_number = len(criteria_order)

        styleEnTete = XFStyle()
        patternEnTete = Pattern()
        patternEnTete.pattern = Pattern.SOLID_PATTERN
        patternEnTete.pattern_fore_colour = Style.colour_map["black"]
        styleEnTete.pattern = patternEnTete
        styleEnTete.font.colour_index = Style.colour_map["white"]

        # ajout en-têtes tableau
        feuil1.write(0, 0, "Critère", styleEnTete)
        feuil1.write(0, 1, "Titre", styleEnTete)
        feuil1.write(0, 2, "Description", styleEnTete)

        feuil1.write(criteria_number + 2, 0, "Nom", styleEnTete)
        feuil1.write(criteria_number + 2, 1, "Prénom", styleEnTete)
        feuil1.write(criteria_number + 2, 2, "Numéro etudiant", styleEnTete)
        feuil1.write(criteria_number + 2, 3, "Identifiant", styleEnTete)

        feuil1.col(0).width = 14 * 256
        feuil1.col(1).width = 14 * 256
        feuil1.col(2).width = 14 * 256
        feuil1.col(3).width = 14 * 256

        # ajout des critères
        for criteria_id in criteria_order:
            feuil1.write(line, 0, "Critère %s" % criteria_id)
            feuil1.write(line, 1, criteria_dict[criteria_id]["title"])
            feuil1.write(line, 2, criteria_dict[criteria_id]["description"])
            # ajout en-têtes tableau
            feuil1.write(criteria_number + 2, column, "Critère %s (%s pts, coeff %s)" % (criteria_id, criteria_dict[criteria_id]["notation"], criteria_dict[criteria_id]["coefficient"]), styleEnTete)
            feuil1.col(column).width = 20 * 256
            line = line + 1
            column = column + 1

        feuil1.write(criteria_number + 2, column, "Note sur 20", styleEnTete)

        peers_list = []
        peers_id_list = []
        peers_average_dict = {}
        infos_peers = self.getInfosPeersDict()

        deposit_box_id = self.getId()
        jalon_bdd = self.portal_jalon_bdd
        for evaluation_note in jalon_bdd.getInfoEvaluationNoteByDepositStu(deposit_box_id, None).all():
            peers_average_dict[evaluation_note[0]] = {"evaluation_note":  evaluation_note[1],
                                                      "evaluation_error": evaluation_note[2]}
            peers_list.append({"id":  evaluation_note[0],
                               "nom": infos_peers[evaluation_note[0]]})
            peers_id_list.append(evaluation_note[0])

        for criteria_note in jalon_bdd.getInfoCriteriaNoteByDepositStu(deposit_box_id).all():
            if criteria_note[0] in peers_average_dict:
                peers_average_dict[criteria_note[0]][criteria_note[1]] = {"criteria_note":  criteria_note[2],
                                                                          "criteria_error": True if criteria_note[3] in [2, 3] else False}

        peers_list.sort(lambda x, y: cmp(x["nom"], y["nom"]))
        peers_infos_dict = jalon_utils.getIndividus(peers_id_list, type="dict")

        line = criteria_number + 3
        for peer in peers_list:
            column = 4
            criteria_stu = peers_average_dict[peer['id']]
            try:
                lastname = peers_infos_dict[peer['id']]["nom"]
                firstname = peers_infos_dict[peer['id']]["prenom"]
                number = peers_infos_dict[peer['id']]["num_etu"]
            except:
                lastname = peer["nom"]
                firstname = number = "Non renseigné"
            feuil1.write(line, 0, lastname)
            feuil1.write(line, 1, firstname)
            feuil1.write(line, 2, number)
            feuil1.write(line, 3, peer['id'])
            for criteria_id in criteria_order:
                criteria_note = criteria_stu[criteria_id]
                feuil1.write(line, column, criteria_note["criteria_note"])
                column = column + 1
            feuil1.write(line, column, criteria_stu["evaluation_note"])
            line = line + 1

        listing.save(path)

        fp = open(path, 'rb')
        data = fp.read()
        fp.close()
        return {"length": str(os.stat(path)[6]), "data": data}

    # #-----------------------------# #
    #  Fonctions appel à jalon_utils  #
    # #-----------------------------# #
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

    #def getInfosMembre(self, etudiant_id):
    #    return jalon_utils.getInfosMembre(etudiant_id)

    def getIndividu(self, sesame, data_type=None, portal=None):
        return jalon_utils.getIndividu(sesame, data_type, portal)

registerATCT(JalonBoiteDepot, PROJECTNAME)
