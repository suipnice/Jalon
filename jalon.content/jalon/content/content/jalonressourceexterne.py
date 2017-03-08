# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.utils import getToolByName

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonRessourceExterne

import jalon_utils
import copy

ressourceType = [u"Lien web".encode("utf-8"), u"Lecteur exportable".encode("utf-8")]

JalonRessourceExterneSchema = ATDocumentSchema.copy() + atpublic.Schema((
    atpublic.StringField("sousTitre",
                         required=False,
                         accessor="getSousTitre",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Sous titre"),)
                         ),
    atpublic.StringField("typeRessourceExterne",
                         required=True,
                         accessor="getTypeRessourceExterne",
                         searchable=False,
                         default="",
                         vocabulary=ressourceType,
                         widget=atpublic.SelectionWidget(label=_(u"Type de la Ressource Externe"),
                                                         format="select",)
                         ),
    atpublic.TextField("auteurs",
                       required=True,
                       accessor="getAuteurs",
                       searchable=False,
                       widget=atpublic.TextAreaWidget(label=_(u"Auteurs"),)
                       ),
    atpublic.StringField("volume",
                         required=False,
                         accessor="getVolume",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Volume"),)
                         ),
    atpublic.StringField("lieu",
                         required=False,
                         accessor="getLieu",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Lieu"),)
                         ),
    atpublic.StringField("editeur",
                         required=False,
                         accessor="getEditeur",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Editeur"),)
                         ),
    atpublic.IntegerField("annee",
                          required=False,
                          accessor="getAnnee",
                          searchable=False,
                          widget=atpublic.IntegerWidget(label=_(u"Année"),)
                          ),
    atpublic.StringField("pagination",
                         required=False,
                         accessor="getPagination",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Pagination"),)
                         ),
    atpublic.StringField("collection",
                         required=False,
                         accessor="getCollection",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Collection"),)
                         ),
    atpublic.StringField("isbn",
                         required=False,
                         accessor="getISBN",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"ISBN"),)
                         ),
    atpublic.StringField("urlbiblio",
                         required=True,
                         accessor="getURLWEB",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"URL"),)
                         ),
    atpublic.TextField("lecteur",
                       required=True,
                       accessor="getLecteur",
                       searchable=False,
                       default_content_type='text/plain',
                       allowable_content_types=('text/plain',),
                       widget=atpublic.TextAreaWidget(label=_(u"Lecteur exportable"),)
                       ),
    atpublic.StringField("videourl",
                         required=False,
                         accessor="getVideourl",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Slug de la vidéo sur le serveur de vidéo"),)
                         ),
    atpublic.StringField("videoauteur",
                         required=False,
                         accessor="getVideoauteur",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Auteur de la vidéo"),)
                         ),
    atpublic.StringField("videoauteurname",
                         required=False,
                         accessor="getVideoauteurname",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Nom de l'auteur de la vidéo"),)
                         ),
    atpublic.StringField("videothumbnail",
                         required=False,
                         accessor="getVideothumbnail",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Vignette de la vidéo"),)
                         ),
))


class JalonRessourceExterne(ATDocumentBase):
    """ Une ressource externe pour Jalon
    """

    implements(IJalonRessourceExterne)
    meta_type = 'JalonRessourceExterne'
    schema = JalonRessourceExterneSchema
    schema['description'].required = True
    schema['description'].widget.label = "Description"
    schema['description'].widget.description = ""
    schema['text'].required = False
    schema['text'].mode = "r"

    def ajouterTag(self, tag):
        return jalon_utils.setTag(self, tag)

    def getAttributsType(self):
        dico = {"Lien web":                   ["title", "description", "urlbiblio"],
                "Lecteur exportable":         ["title", "description", "lecteur"],
                "Ressource bibliographique":  ["title", "sousTitre", "description", "auteurs", "volume", "lieu", "editeur", "annee",  "pagination", "collection", "isbn", "urlbiblio"],
                "Catalogue BU":               ["description"],
                "Video":                      ["title", "description"]}
        return dico[self.getTypeRessourceExterne()]

    def getAttributsTypeMod(self):
        dico = {"Lien web":                   {"title":       "Title",
                                               "description": "Description",
                                               "urlbiblio":   "Urlbiblio"},
                "Lecteur exportable":         {"title":       "Title",
                                               "description": "Description",
                                               "lecteur":     "Lecteur"},
                "Ressource bibliographique":  {"title":       "Title",
                                               "sousTitre":   "SousTitre",
                                               "description": "Description",
                                               "auteurs":     "Auteurs",
                                               "volume":      "Volume",
                                               "lieu":        "Lieu",
                                               "editeur":     "Editeur",
                                               "annee":       "Annee",
                                               "pagination":  "Pagination",
                                               "collection":  "Collection",
                                               "isbn":        "Isbn",
                                               "urlbiblio":   "Urlbiblio"},
                "Catalogue BU":               {"description": "Description"},
                "Video":                      {"title":       "Title",
                                               "description": "Description"},
                "VOD":                        {"title":       "Title",
                                               "description": "Description"}}
        return dico[self.getTypeRessourceExterne()]

    def getLecteurExportable(self):
        return self.lecteur

    def getMacroType(self):
        dico = {"Lien web":                   "lien",
                "Lecteur exportable":         "lecteur",
                "Ressource bibliographique":  "reference",
                "Catalogue BU":               "cataloguebu",
                "Video":                      "video",
                "VOD":                        "vod"}
        return dico[self.getTypeRessourceExterne()]

    def getRessourceCatalogueBU(self):
        portal_primo = getToolByName(self, "portal_primo")
        resultat = portal_primo.rechercherRecordById(str(self.getISBN()))
        if resultat:
            resultat["description"] = self.Description()
        else:
            resultat = {"title": self.Title(),
                        "description":  self.Description(),
                        "creator":      self.getAuteurs(),
                        "publisher":    self.getEditeur(),
                        "creationdate": self.getCollection(),
                        "image":        self.getLecteur().split("\n"),
                        "urlcatalogue":  ""}
        return resultat

    def getRessourceType(self):
        return ressourceType

    def getURLLien(self):
        lien = self.getURLWEB()
        lien = lien.replace("http//", "http://")
        lien = lien.replace("https//", "https://")
        lien = lien.replace("ftp//", "ftp://")
        if lien and not(lien.startswith("http://") or lien.startswith("ftp://")):
            lien = "http://%s" % lien
        return lien

    def setProperties(self, dico):
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        self.reindexObject()
        self.aq_parent.majFichier(self)
        """
        items = self.getRelatedItems()
        for item in items:
            if item.portal_type in ["JalonCours"]:
                #modification du titre dans le cours
                element_cours = copy.deepcopy(item.getCourseItemProperties())
                if self.getId() in element_cours:
                    element_cours[self.getId()]["titreElement"] = self.Title()
                    item.setCourseItemsProperties(element_cours)
            if item.portal_type in ["JalonBoiteDepot", "JalonCoursWims"]:
                #modification du titre dans les boite de depots
                dico = copy.deepcopy(item.getDocumentsProperties())
                if self.getId() in dico:
                    dico[self.getId()]["titreElement"] = self.Title()
                    #item.setInfos_element(dico)
                    item.setDocumentsProperties(dico)
        """

    def editFromBUCatalogBU(self, recordid):
        portal_primo = getToolByName(self, "portal_primo")
        resultat = portal_primo.rechercherRecordById(recordid)
        dico = {"Title":                 resultat["title"],
                "TypeRessourceExterne":  "Catalogue BU",
                "SousTitre":             "",
                "Description":           "",
                "Auteurs":               (resultat["creator"]),
                "Volume":                resultat["format"],
                "Lieu":                  "Lieu",
                "Editeur":               resultat["publisher"],
                "Annee":                 0,
                "Pagination":            "Pagination",
                "Collection":            resultat["creationdate"],
                "Isbn":                  recordid,
                "Urlbiblio":             "Urlbiblio",
                "Lecteur":               ""}
        try:
            dico["Lecteur"] = "\n".join(resultat["image"])
        except:
            pass
        self.setProperties(dico)

registerATCT(JalonRessourceExterne, PROJECTNAME)
