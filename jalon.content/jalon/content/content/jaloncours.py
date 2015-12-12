# -*- coding: utf-8 -*-
""" L'objet "Cours" de Jalon."""
from zope.interface import implements

from Products.Archetypes.public import *

from Products.ATContentTypes.content.folder import ATFolder, ATFolderSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.utils import getToolByName
from Products.Ploneboard.browser.utils import toPloneboardTime

from persistent.dict import PersistentDict

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonCours

from DateTime import DateTime
from os import close
from zipfile import ZipFile, ZIP_DEFLATED

import json
import urllib
import urllib2
import string
import jalon_utils
import random
import os

from logging import getLogger
LOG = getLogger('[JalonCours]')

JalonCoursSchema = ATFolderSchema.copy() + Schema((
    StringField("auteurPrincipal",
                required=False,
                accessor="getAuteurPrincipal",
                default="",
                searchable=False,
                widget=StringWidget(label=_(u"Auteur Principal"),
                                    description=_(u"L'auteur principal du cours a accès à celui-ci en modification, son nom est affiché aux étudiants comme étant l'auteur du cours."),)),
    LinesField("coAuteurs",
               required=False,
               accessor="getCoAuteurs",
               default=[],
               searchable=False,
               widget=MultiSelectionWidget(label=_(u"Co-auteurs"),
                                           description=_(u"Un co-auteur du cours a accès à celui-ci en modification, comme s'il en était l'auteur."),
                                           format="checkbox",)),
    LinesField("coLecteurs",
               required=False,
               accessor="getCoLecteurs",
               default=[],
               searchable=False,
               widget=MultiSelectionWidget(label=_(u"Co-lecteurs"),
                                           description=_(u"Un lecteur du cours a accès à celui-ci en lecture, comme s'il était étudiant."),
                                           format="checkbox",)),
    StringField("acces",
                required=True,
                accessor="getAcces",
                searchable=False,
                default=u"Privé".encode("utf-8"),
                vocabulary=[u"Privé".encode("utf-8"), u"Aux étudiants".encode("utf-8"), u"Public".encode("utf-8")],
                widget=SelectionWidget(label=_(u"Diffusion du cours:"),
                                       format="select",)),
    LinesField("listeAcces",
               required=False,
               accessor="getListeAcces",
               searchable=False,
               widget=LinesWidget(label=_(u"liste des diplômes, ue, uel, groupe d'Apogée"),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("groupe",
               required=False,
               accessor="getGroupe",
               searchable=False,
               widget=LinesWidget(label=_(u"groupe d'étudiants personnalisé du cours"),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("invitations",
               required=False,
               accessor="getInvitations",
               searchable=False,
               widget=LinesWidget(label=_(u"liste des courriels d'invités au cours"),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    StringField("lienCourt",
                required=False,
                accessor="getLienCourt",
                default="",
                searchable=False,
                widget=StringWidget(label=_(u"Le lien court d'un cours"),
                                    description=_(u"Le lien cours n'existe que pour le cours public"),)),
    BooleanField("libre",
                 required=True,
                 accessor="getLibre",
                 searchable=False,
                 default=False,
                 widget=BooleanWidget(label=_(u"Inscriptions libres"))),
    LinesField("inscriptionsLibres",
               required=False,
               accessor="getInscriptionsLibres",
               searchable=False,
               widget=LinesWidget(label=_(u"liste des inscriptions libres"),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    StringField("lienMooc",
                required=False,
                accessor="getLienMooc",
                default="",
                searchable=False,
                widget=StringWidget(label=_(u"Le lien court mooc d'un cours"),
                                    description=_(u"Le lien court mooc n'existe que pour le cours en accès libre"),)),
    LinesField("plan",
               required=False,
               accessor="getPlan",
               searchable=False,
               widget=LinesWidget(label=_(u"Plan intéractif"),
                                  description=_(u"Le plan intéractif."),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("elements_glossaire",
               required=False,
               accessor="getGlossaire",
               searchable=False,
               widget=LinesWidget(label=_(u"Liste des éléments du glossaire"),
                                  description=_(u"La liste des éléments du glossaire."),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("elements_bibliographie",
               required=False,
               accessor="getBibliographie",
               searchable=False,
               widget=LinesWidget(label=_(u"Liste des éléments de la bibliographie"),
                                  description=_(u"La liste des éléments de la bibliographie."),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("listeclasses",
               required=False,
               accessor="getListeClasses",
               searchable=False,
               widget=LinesWidget(label=_(u"liste des classes du cours"),
                                  description=_(u"Les classes du cours."),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("webconferences",
               required=False,
               accessor="getWebconferences",
               searchable=False,
               widget=LinesWidget(label=_(u"liste des webconferences du cours"),
                                  description=_(u"Les webconferences du cours."),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("actualites",
               required=False,
               accessor="getActualites",
               searchable=False,
               widget=LinesWidget(label=_(u"liste des actualités du cours"),
                                  description=_(u"Les actualités du cours."),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("avancementPlan",
               required=False,
               accessor="getAvancementPlan",
               searchable=False,
               widget=LinesWidget(label=_(u"Avancement de l'enseignant et des étudiants dans le plan du cours."),
                                  description=_(u"Avancement de l'enseignant et des étudiants dans le plan du cours."),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    LinesField("categorie",
               required=False,
               accessor="getCategorieCours",
               searchable=False,
               default=["1"],
               widget=LinesWidget(label=_(u"Catégorie(s) du cours."),
                                  description=_(u"Catégorie(s) du cours."),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
    BooleanField("commentaires_sociaux",
                 required=True,
                 accessor="getCommentaires_sociaux",
                 searchable=False,
                 default=False,
                 widget=BooleanWidget(label=_(u"Commentaires sur les réseaux sociaux"))),
    BooleanField("jaime_sociaux",
                 required=True,
                 accessor="getJaime_sociaux",
                 searchable=False,
                 default=False,
                 widget=BooleanWidget(label=_(u"J'aime sur Facebook"))),
    BooleanField("activer_email_forum",
                 required=False,
                 accessor="getActiverEmailForum",
                 searchable=False,
                 widget=StringWidget(label=_(u"Envoie de courriels"),
                                     description=_(u"Envoyer un courriel à tous les utilisateurs du cours à chaque message posté dans un forum."),)),
    StringField("dateDerniereModif",
                required=False,
                accessor="getDateDerniereModif",
                searchable=False,
                widget=StringWidget(label=_(u"Date de dernière modification"),
                                    description=_(u"Date de dernière modification"),)),
    BooleanField("activer_dll_fichier",
                 required=True,
                 accessor="getActiver_dll_fichier",
                 searchable=False,
                 default=False,
                 widget=BooleanWidget(label=_(u"Telechargement de fichiers"),
                                      description=_(u"Autorise le telechargement d'une archive de tous les fichiers d'un cours"),)),
    StringField("catiTunesU",
                required=False,
                accessor="getCatiTunesU",
                searchable=False,
                widget=StringWidget(label=_(u"Catégorie iTunesU du cours"),
                                    description=_(u"Catégorie iTunesU du cours"),)),
    BooleanField("diffusioniTunesU",
                 required=True,
                 accessor="isDiffuseriTunesU",
                 searchable=False,
                 default=False,
                 widget=BooleanWidget(label=_(u"État de la diffusion sur iTunesU"),
                                      description=_(u"État de la diffusion sur iTunesU"),)),
    StringField("dateDerniereActu",
                required=False,
                accessor="getLastDateActu",
                searchable=False,
                widget=StringWidget(label=_(u"Date de la dernière Actu du cours"),
                                    description=_(u"Date de la dernière Actu du cours"),)),
))


class JalonCours(ATFolder):

    """ Un cours Jalon."""

    implements(IJalonCours)
    meta_type = 'JalonCours'
    schema = JalonCoursSchema

    _elements_cours = {}
    _twitter_cours = {}

    def __init__(self, *args, **kwargs):
        super(JalonCours, self).__init__(*args, **kwargs)

    def toPloneboardTime(self, context, request, time_=None):
        """Return time formatted for Ploneboard."""
        return toPloneboardTime(context, request, time_)

    def getElementCours(self, key=None):
        #self.plone_log("getElementCours")
        if key:
            return self._elements_cours.get(key, None)
        return self._elements_cours

    def getKeyElementCours(self):
        #self.plone_log("getKeyElementCours")
        return self._elements_cours.keys()

    def setElementsCours(self, elements_cours):
        #self.plone_log("setElementsCours")
        if type(self._elements_cours).__name__ != "PersistentMapping":
            self._elements_cours = PersistentDict(elements_cours)
        else:
            self._elements_cours = elements_cours

    def getProprietesVideo(self, id_video):
        infos_element = self.getElementCours(id_video)
        video_title = infos_element["titreElement"]
        video_title_my_space = video_title
        if "titreElementMonEspace" in infos_element:
            video_title_my_space = infos_element["titreElementMonEspace"]
        return {"video_title":          video_title,
                "video_title_my_space": video_title_my_space,
                "is_display_in_map":    "checked" if infos_element["complementElement"]["value"] else ""}

    def setProprietesElement(self, infos_element):
        dico = self.getElementCours(infos_element["idElement"])
        if not "titreElementMonEspace" in dico:
            dico["titreElementMonEspace"] = dico["titreElement"][:]
        if infos_element["element_title_in_map"] == "":
            dico["titreElement"] = dico["titreElementMonEspace"][:]
        else:
            dico["titreElement"] = infos_element["element_title_in_map"]
        if not "display_in_plan" in infos_element:
            dico["complementElement"]["value"] = False
        else:
            dico["complementElement"]["value"] = True
        self._elements_cours[infos_element["idElement"]] = dico
        self.setElementsCours(self._elements_cours)

    def getTwitterCours(self, key=None):
        #self.plone_log("getTwitterCours")
        if not "dateMAJ" in self._twitter_cours:
            jalon_properties = getToolByName(self, "portal_jalon_properties")
            twitter_cours = jalon_properties.getTwitterCours("#JalonHTA912")
            if twitter_cours:
                self.setTwitterCours({"dateMAJ": DateTime(),
                                      "tweets":  twitter_cours})
                return twitter_cours
            return []
        if key:
            return self._twitter_cours.get(key, None)
        return self._twitter_cours["tweets"]

    def getKeyTwitterCours(self):
        #self.plone_log("getKeyTwitterCours")
        return self._twitter_cours.keys()

    def setTwitterCours(self, _twitter_cours):
        #self.plone_log("setTwitterCours")
        if type(self._twitter_cours).__name__ != "PersistentMapping":
            self._twitter_cours = PersistentDict(_twitter_cours)
        else:
            self._twitter_cours = _twitter_cours

    def getActualitesCours(self, toutes=None):
        #self.plone_log("getActualitesCours")
        actualites = []
        descriptionActu = {"chapdispo": _(u"et son contenu sont maintenant disponibles."),
                           "chapnondispo": _(u"et son contenu ne sont plus disponibles."),
                           "dispo": _(u"est disponible."),
                           "nondispo": _(u"n'est plus disponible."),
                           "message": _(u"Nouveau message dans le sujet de discussion."),
                           "datedepot": _(u"Nouvelle date limite de dépôt : "),
                           "datedepotfin": _(u"Le dépôt n'est plus permis"),
                           "correctiondispo": _(u"La correction est disponible."),
                           "correctionnondispo": _(u"La correction n'est plus disponible"),
                           "sujetdispo": _(u"Le sujet est disponible."),
                           "sujetnondispo": _(u"Le sujet n'est plus disponible."),
                           "nouveauxdepots": _(u"nouveau(x) dépôt(s) disponible(s)"),
                           "nouveauxmessages": _(u"nouveau(x) message(s) disponible(s)")}
        listeActualites = list(self.getActualites())
        listeActualites.sort(lambda x, y: cmp(y["dateActivation"], x["dateActivation"]))
        if not listeActualites:
            return {"nbActu":    0,
                    "listeActu": []}

        infos_elements = self.getElementCours()

        for actualite in listeActualites:
            if DateTime() > actualite["dateActivation"]:
                infos_element = infos_elements.get(actualite["reference"], '')
                if infos_element:
                    description = descriptionActu[actualite["code"]]
                    if actualite["code"] == "datedepot":
                        description = "%s %s" % (description, DateTime(actualite["dateDepot"], datefmt='international').strftime("%d/%m/%Y %H:%M"))
                    if actualite["code"] == "nouveauxdepots":
                        description = "%s %s" % (str(actualite["nb"]), description)
                    actualites.append({"type":        infos_element["typeElement"],
                                       "titre":       infos_element["titreElement"],
                                       "description": description,
                                       "date":        actualite["dateActivation"]})
        if not toutes:
            return {"nbActu":    len(actualites),
                    "listeActu": actualites[:3]}
        else:
            return {"nbActu":    len(actualites),
                    "listeActu": actualites}

    def getAffichageAcces(self, toutes=None):
        #self.plone_log("getAffichageAcces")
        dico = {"Aux étudiants": {"titre": _(u"Réservé à vos étudiants inscrits à l'Université ou invités par courriel"),
                                   "description": _(u"Accès réservé à : <ul><li>l'offre de formations universitaires Apogée (Diplôme / UE / Groupe)</li><li>mon groupe personalisé d'étudiants inscrits à l'Université</li><li>personnes extérieures à l'université (invitations par courriel)</li></ul>")},
                "Public":        {"titre": _(u"Public"),
                                  "description": _(u"Accès à tous les utilisateurs disposant du lien du cours, seuls les étudiants authentifiés auront accès aux activités.")}
                }
        if toutes:
            return dico
        else:
            return dico[self.getAcces()]

    def getAffElement(self, idElement, attribut):
        #self.plone_log("getAffElement")
        #infos_element = self.getInfosElementCours(idElement)
        infos_element = self.getElementCours(idElement)
        if infos_element:
            if infos_element[attribut] != "":
                return infos_element[attribut].strftime("%Y/%m/%d %H:%M")
        return DateTime().strftime("%Y/%m/%d %H:%M")

    def getAnnonces(self, authMember, request, personnel, all=None):
        #self.plone_log("getAnnonces")
        annonces = []
        listeAnnonces = list(self.annonce.objectValues())
        listeAnnonces.sort(lambda x, y: cmp(y.modified(), x.modified()))
        if listeAnnonces and personnel and all:
            return {"listeAnnonces": listeAnnonces, "nbAnnonces": len(listeAnnonces)}
        elif listeAnnonces and personnel:
            return {"listeAnnonces": [listeAnnonces[0]], "nbAnnonces": len(listeAnnonces)}

        #self.plone_log("not personnel")
        groupes = []
        diplomes = []
        portal = self.portal_url.getPortalObject()
        portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")
        try:
            idMember = authMember.getId()
        except:
            idMember = authMember
        if idMember and not "@" in idMember:
            #membership = getToolByName(portal, "portal_membership")
            #member = membership.getMemberById(idMember)
            #diplomes = authMember.getProperty("unsdiplomes", [])
            #if diplomes is None:
            #    diplomes = []

            if portal_jalon_bdd.getTypeBDD() == "apogee":
                COD_ETU = member.getProperty("supannEtuId", member.getProperty("supannAliasLogin"))
            if portal_jalon_bdd.getTypeBDD() == "sqlite":
                COD_ETU = idMember

            for diplome in portal_jalon_bdd.getInscriptionIND(COD_ETU, "etape"):
                diplomes.append(diplome["COD_ELP"])

            groupes = portal_jalon_bdd.getGroupesEtudiant(COD_ETU)

        for annonce in listeAnnonces:
            suite = 1
            publics = annonce.getPublics()
            ##self.plone_log(publics)
            if not publics:
                #pas besoin de la ligne suivante, si tout est decoche c'est une annonce juste pour l'auteur lui meme
                #annonces.append(annonce)
                suite = 0
            if suite and ("colecteurs*-*colecteurs" in publics) and (idMember in self.getCoLecteurs()):
                annonces.append(annonce)
                suite = 0
            if suite and ("groupeperso*-*perso" in publics) and (idMember in self.getGroupe()):
                annonces.append(annonce)
                suite = 0
            if suite and ("invitationsemail*-*email" in publics) and (idMember in self.getInvitations()):
                annonces.append(annonce)
                suite = 0
            if suite:
                for diplome in diplomes:
                    if "etape*-*%s" % diplome in publics:
                        annonces.append(annonce)
                        suite = 0
                        break

                    #COD_ETP, COD_VRS_VET = diplome.rsplit("-", 1)
                    inscription_pedago = portal_jalon_bdd.getInscriptionPedago(COD_ETU, diplome)
                    if not inscription_pedago:
                        inscription_pedago = portal_jalon_bdd.getUeEtape(diplome)
                    for ue in inscription_pedago:
                        if "ue*-*%s" % ue["COD_ELP"] in publics:
                            annonces.append(annonce)
                            suite = 0
                            break
                    if not suite:
                        break
                if suite:
                    for groupe in groupes:
                        if "groupe*-*%s" % groupe[0] in publics:
                            annonces.append(annonce)
                            break

        annonces.sort(lambda x, y: cmp(y.modified(), x.modified()))
        if annonces and all:
            return {"listeAnnonces": annonces, "nbAnnonces": len(listeAnnonces)}
        elif annonces:
            return {"listeAnnonces": [annonces[0]], "nbAnnonces": len(listeAnnonces)}
        else:
            return {"listeAnnonces": [], "nbAnnonces": 0}

    def getDicoForums(self, all=None):
        #self.plone_log("getDicoForums")
        listeForums = list(self.forum.objectValues())
        listeForums.sort(lambda x, y: cmp(y.modified(), x.modified()))
        if len(listeForums) > 5:
            return {"nbForums":    len(listeForums),
                    "listeForums": listeForums[:5]}
        else:
            return {"nbForums":    len(listeForums),
                    "listeForums": listeForums}

    def getGraphFacebook(self):
        #self.plone_log("getDicoForums")
        if self.getCommentaires_sociaux() or self.getJaime_sociaux():
            url = self.absolute_url()
            req = urllib2.Request('http://graph.facebook.com/?ids=%s' % url)
            try:
                data = json.load(urllib2.urlopen(req))
                ##self.plone_log(data)
                if url in data and "comments" in data[url]:
                    return data[url]
            except:
                ##self.plone_log(e.reason)
                pass
        return None

    def getAuteur(self):
        #self.plone_log("getAuteur")
        username = self.getAuteurPrincipal()
        if username:
            return self.getInfosMembre(username)
        return self.getInfosMembre(self.Creator())

    def getAuteurs(self):
        #self.plone_log("getAuteurs")
        return {"principal": self.getAuteur(), "coAuteurs": self.getCoAuteursCours()}

    def getAffCategorieCours(self):
        #self.plone_log("getAffCategorieCours")
        categories = self.getJalonCategories()
        return categories[int(self.getCategorieCours())]["title"]

    def getCategorieCours(self):
        #self.plone_log("getCategorieCours")
        try:
            return self.categorie[0]
        except:
            return 1

    def getAidePlan(self):
        #self.plone_log("getAidePlan")
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return {"activer_aide_plan": jalon_properties.getJalonProperty("activer_aide_plan"),
                "lien_aide_plan":    jalon_properties.getJalonProperty("lien_aide_plan")}

    def getEtablissement(self):
        #self.plone_log("getEtablissement")
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return {"activer_etablissement": jalon_properties.getJalonProperty("activer_etablissement"),
                "etablissement":         jalon_properties.getJalonProperty("etablissement")}

    def getJalonCategories(self):
        #self.plone_log("getJalonCategories")
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return dict(jalon_properties.getCategorie())

    def getPropertiesCatiTunesU(self):
        #self.plone_log("getPropertiesCatiTunesU")
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return dict(jalon_properties.getPropertiesCatiTunesU())

    def getAffCatiTunesUCours(self):
        #self.plone_log("getAffCatiTunesUCours")
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return jalon_properties.getAffCatiTunesUCours(self.getCatiTunesU())

    def getClefsDico(self, dico):
        #self.plone_log("getClefsDico")
        return jalon_utils.getClefsDico(dico)

    def getCoAuteursCours(self):
        #self.plone_log("getCoAuteursCours")
        retour = []
        for username in self.getCoAuteurs():
            if username:
                retour.append(self.getInfosMembre(username))
        return retour

    def getCoLecteursCours(self):
        #self.plone_log("getCoLecteursCours")
        retour = []
        for username in self.getCoLecteurs():
            retour.append(self.getInfosMembre(username))
        return retour

    def getCommentaireEpingler(self, idTester=None):
        #self.plone_log("getCommentaireEpingler")
        if len(self.getAvancementPlan()) <= 1:
            return ""

        if not idTester:
            return self.getAvancementPlan()[1]
        elif idTester == self.getAvancementPlan()[0]:
            return self.getAvancementPlan()[1]

        return ""

    def getContents(self, subject, typeR, authMember, repertoire=None, categorie=None):
        #self.plone_log("getContents")
        portal = self.portal_url.getPortalObject()
        dicoType = {"Fichiers":              "Fichiers",
                    "JalonRessourceExterne": "Externes",
                    "JalonTermeGlossaire":   "Glossaire",
                    "JalonExerciceWims":     "Wims"}
        if repertoire:
            home = getattr(getattr(portal.Members, authMember), repertoire)
        else:
            home = getattr(getattr(portal.Members, authMember), dicoType[typeR])
        return home.getContents(subject, typeR, authMember, "")

    def getElementView(self, idElement, createurElement, typeElement, indexElement, mode_etudiant):
        #self.plone_log("getElementView")
        return jalon_utils.getElementView(self, "Cours", idElement, createurElement, typeElement, indexElement, mode_etudiant)

    def getCreateur(self):
        #self.plone_log("getCreateur")
        return self.getInfosMembre(self.Creator())

    def getElementsCours(self, tag):
        #self.plone_log("getElementsCours")
        return self.__getattribute__("get%s" % tag)()

    def getDepots(self, idboite, authMember, personnel, request):
        #self.plone_log("getDepots")
        if "*-*"in idboite:
            idboite = idboite.split("*-*")[-1]
        return getattr(self, idboite).getDepots(authMember, personnel, request)

    def getForums(self):
        #self.plone_log("getForums")
        return None

    def getGloBib(self, glo_bib):
        #self.plone_log("getGloBib")
        dicoLettres = {}
        if glo_bib == "glossaire":
            elements = self.getGlossaire()
        else:
            elements = self.getBibliographie()
        if elements:
            infos_element = self.getElementCours()
        for idElement in elements:
            info_element = infos_element.get(idElement)
            if info_element:
                info_element["idElement"] = idElement
                lettre = info_element["titreElement"][0].upper()
                if not lettre in dicoLettres:
                    dicoLettres[lettre] = [info_element]
                else:
                    dicoLettres[lettre].append(info_element)
        return dicoLettres

    def getInfosGroupe(self):
        #self.plone_log("getInfosGroupe")
        groupe = self.getGroupe()
        return jalon_utils.getIndividus(list(groupe), "listdict")

    def getInfosLibre(self):
        #self.plone_log("getInfosLibre")
        libre = self.getInscriptionsLibres()
        return jalon_utils.getIndividus(list(libre), "listdict")

    def getInfosInvitations(self):
        #self.plone_log("getInfosInvitations")
        invitations = self.getInvitations()
        if not invitations:
            return []
        etudiants = []
        portal_membership = getToolByName(self, "portal_membership")
        for sesame in invitations:
            nom = sesame
            member = portal_membership.getMemberById(sesame)
            if member:
                nom = member.getProperty("fullname", sesame)
            etudiants.append({"nom": nom, "email": sesame})
        return etudiants

    def getPublicsAnnonce(self):
        #self.plone_log("getPublicsAnnonce")
        res = self.getInfosListeAcces()
        if self.getCoAuteurs():
            res.append(["Tous les co-auteurs", "coauteurs", len(self.getCoAuteurs()), "coauteurs"])
        if self.getCoLecteurs():
            res.append(["Tous les co-lecteurs", "colecteurs", len(self.getCoLecteurs()), "colecteurs"])
        return res

    def getDescriptionCourte(self):
        description = self.Description()
        if not description:
            return {"link": False, "desc": "ce cours n'a pas encore de description."}
        if len(description) > 100:
            return {"link": True, "desc": self.getShortText(description, 100)}
        return {"link": False, "desc": description}

    def getAffichageFormation(self):
        listeFormations = self.getAffichageFormations()
        nbEtuFormations = self.getNbEtuFormation(listeFormations)
        return {"nbFormations": len(listeFormations),
                "nbEtuFormations": nbEtuFormations}

    def getAffichageFormations(self):
        #self.plone_log("getAffichageFormation")
        res = []
        listeAcces = self.getListeAcces()
        portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
        for acces in listeAcces:
            type, code = acces.split("*-*")
            if type == "etape":
                #suite au probleme de DAEU-B ce conditionnement à été créé pour cette fonction
                #ainsi que pour getInfosListeAcces et dans jalonfoler getInfosApogee et getListeCours
                #retour = apogee.getInfosEtape(*code.rsplit("-", 1))
                retour = portal_jalon_bdd.getInfosEtape(code)
                if not retour:
                    elem = ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
                else:
                    elem = list(self.encodeUTF8(retour))
            if type in ["ue", "uel"]:
                retour = portal_jalon_bdd.getInfosELP2(code)
                if not retour:
                    elem = ["Le code %s n'est plus valide pour cette UE / UEL." % code, code, "0"]
                else:
                    elem = list(self.encodeUTF8(retour))
            if type == "groupe":
                retour = portal_jalon_bdd.getInfosGPE(code)
                if not retour:
                    elem = ["Le code %s n'est plus valide pour ce groupe." % code, code, "0"]
                else:
                    elem = list(self.encodeUTF8(retour))
            elem.append(type)
            res.append(elem)
        res.sort()
        return res

    def getNbEtuFormation(self, listeFormations):
        #self.plone_log("getNbEtuFormation")
        nbEtuFormations = 0
        for formation in listeFormations:
            nbEtuFormations = nbEtuFormations + int(formation[2])
        return nbEtuFormations

    def getAffichageInscriptionIndividuelle(self, typeAff):
        #self.plone_log("getAffichageInscriptionIndividuelle")
        res = []
        if typeAff == "groupe":
            groupe = self.getGroupe()
            nbgroupe = 0
            if groupe:
                nbgroupe = len(groupe)
            if nbgroupe > 0:
                res.append([_(u"Étudiant(s) de l'université"), "perso", nbgroupe, "groupeperso"])
        else:
            invitations = self.getInvitations()
            nbinvitations = 0
            if invitations:
                nbinvitations = len(invitations)
            if nbinvitations > 0:
                res.append([_(u"Étudiant(s) extérieur(s)"), "email", nbinvitations, "invitationsemail"])
        return res

    def getInfosListeAcces(self):
        #self.plone_log("getInfosListeAcces")
        res = []
        listeAcces = self.getListeAcces()
        portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
        for acces in listeAcces:
            type, code = acces.split("*-*")
            if type == "etape":
                #suite au probleme de DAEU-B ce conditionnement à été créé pour cette fonction
                #ainsi que pour getInfosListeAcces et dans jalonfoler getInfosApogee et getListeCours
                #retour = apogee.getInfosEtape(*code.rsplit("-", 1))
                retour = portal_jalon_bdd.getInfosEtape(code)
                if not retour:
                    elem = ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
                else:
                    elem = list(self.encodeUTF8(retour))
            if type in ["ue", "uel"]:
                retour = portal_jalon_bdd.getInfosELP2(code)
                if not retour:
                    elem = ["Le code %s n'est plus valide pour cette UE / UEL." % code, code, "0"]
                else:
                    elem = list(self.encodeUTF8(retour))
            if type == "groupe":
                retour = portal_jalon_bdd.getInfosGPE(code)
                if not retour:
                    elem = ["Le code %s n'est plus valide pour ce groupe." % code, code, "0"]
                else:
                    elem = list(self.encodeUTF8(retour))
            elem.append(type)
            res.append(elem)
        groupe = self.getGroupe()
        if groupe:
            res.append(["Invitations individuelles : étudiant(s) de l'université", "perso", len(groupe), "groupeperso"])
        invitations = self.getInvitations()
        if invitations:
            res.append(["Invitations individuelles : étudiant(s) hors université", "email", len(invitations), "invitationsemail"])
        return res

    # getInfosMembre recupere les infos sur les personnes.
    def getInfosMembre(self, username):
        #self.plone_log("getInfosMembre")
        return jalon_utils.getInfosMembre(username)

    def getKeyElementsCours(self, tag=None, idboite=None, menu=None):
        #self.plone_log("getKeyElementsCours")
        liste = []
        if tag == "Glossaire":
            glossaire = self.getGlossaireCours()
            for lettre in glossaire:
                liste.extend(glossaire[lettre])
            liste.sort()
            return liste
        if tag in ["AutoEvaluation", "BoiteDepot", "Examen"]:
            idBoite = idboite.split("*-*")[-1]
            boite = getattr(self, idBoite)
            liste = []
            for element in boite.getListeAttribut(menu):
                liste.append("%s*-*%s" % (tag, element.split("*-*")[-1]))
            return liste
        return self.getElementsCours(tag)

    def getLastLogin(self):
        #self.plone_log("getLastLogin")
        member = self.portal_membership.getAuthenticatedMember()
        last_login = member.getProperty('last_login_time', None)
        if isinstance(last_login, basestring):
            last_login = DateTime(last_login)
        return last_login

    def getLocaleDate(self, date, format="%d/%m/%Y"):
        #self.plone_log("getLocaleDate : %s" % date)
        return jalon_utils.getLocaleDate(date, format)

    def getMotsClefs(self, search, objet):
        #self.plone_log("getMotsClefs")
        mots = []
        catalog = getToolByName(self, 'portal_catalog')
        keywords = list(catalog.uniqueValuesFor("Subject"))
        for mot in keywords:
            if search in mot:
                mots.append(mot)
        mots.sort()
        return json.dumps(dict(keywords=mots))

    def getPlanPlat(self, liste=None):
        #self.plone_log("getPlanPlat")
        plat = []
        if liste is None:
            liste = list(self.plan)
            if not liste:
                return []
        for titre in liste:
            plat.append(titre["idElement"])
            if "listeElement" in titre:
                plat.extend(self.getPlanPlat(titre["listeElement"]))
        return plat

    def getPlanCours(self, personnel=False, authMember=None, listeActualites=None):
        #self.plone_log("----- getPlanCours (Start) -----")
        #self.plone_log("***** listeActualites : %s" % str(listeActualites))
        html = []
        i = 0
        if listeActualites is None:
            #self.plone_log("***** Not listeActualites")
            listeActualites = self.getActualitesCours(True)["listeActu"]
        for chapitre in self.plan:
            element = self.getPlanChapitre(chapitre, i, personnel, authMember, listeActualites)
            if element:
                html.append(element)
            i = i + 1
        #self.plone_log("----- getPlanCours (End) -----")
        return "\n".join(html)

    def getPlanChapitre(self, element, index, personnel, authMember, listeActualites):
        #self.plone_log("getPlanChapitre")
        idEpingler = commentaireEpingler = ""
        if len(self.getAvancementPlan()):
            idEpingler = self.getAvancementPlan()[0]
            try:
                commentaireEpingler = self.getAvancementPlan()[1]
            except:
                commentaireEpingler = "Élément signalé par l&rsquo;enseignant"

        infos_element = self.getElementCours(element["idElement"])
        if infos_element:
            nouveau = ""
            #si la ressource est nouvelle dans le cours
            if authMember and self.isNouveau(infos_element, listeActualites):
                nouveau = "<i class='fa fa-bell-o fa-fw fa-lg no-pad right'></i>"
            isTitre = self.isTitre(infos_element["typeElement"])
            isAffElement = self.isAfficherElement(infos_element["affElement"], infos_element["masquerElement"])

            categorieElement = ""
            if infos_element["typeElement"] in ["Titre", "TexteLibre"]:
                categorieElement = "Classement"
            if infos_element["typeElement"] in ["File", "Image", "Page", "Lien web", "Lecteur exportable", "Ressource bibliographique", "Glossaire", "Presentations sonorisees", "Webconference", "Catalogue BU", "Video"]:
                categorieElement = "Mon_Espace"
            if infos_element["typeElement"] in ["AutoEvaluation", "Examen", "BoiteDepot", "Forum", "Glossaire", "SalleVirtuelle"]:
                categorieElement = "Activite"

            tag = 'span' if isTitre["condition"] else 'a'
            html = []
            html.append("<li id=\"%s-%s\" class=\"sortable %s\">" % (isTitre["class"], element["idElement"], isTitre["class"]))
            if personnel or isAffElement["val"] == 1:

                if authMember and not personnel:
                    # Version lien
                    if infos_element["typeElement"] != "Titre":
                        if "marque" in infos_element and authMember in infos_element["marque"]:
                            html.append("<a class='right' href='%s/marquer_element_script?element=%s&amp;marquer=non'>" % (self.absolute_url(), element["idElement"]))
                            html.append("<i class='fa fa-check-square-o fa-fw fa-lg no-pad'></i>")
                            html.append("</a>")
                        else:
                            html.append("<a class='right' href='%s/marquer_element_script?element=%s&amp;marquer=oui'>" % (self.absolute_url(), element["idElement"]))
                            html.append("<i class='fa fa-square-o fa-fw fa-lg no-pad'></i>")
                            html.append("</a>")

                if personnel:
                    html.append("""
                                <a class="dropdown" data-dropdown="drop-%s" data-options="align:left">
                                    <i class="fa fa-cog fa-fw no-pad"></i>
                                </a>
                                <ul id="drop-%s" class="f-dropdown" data-dropdown-content="data-dropdown-content">
                                """ % (index, index))
                    if isAffElement["val"] == 0:
                        epinglerPos = "non"
                        html.append("""<li>
                                           <a href="%s/folder_form?macro=macro_cours_afficher&amp;formulaire=afficher-element&amp;page=cours_plan_view&amp;section=plan&amp;tag=aucun&amp;idElement=%s"
                                              data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-eye fa-fw"></i>Afficher</a>
                                       </li>""" % (self.absolute_url(), element["idElement"]))
                    else:
                        epinglerPos = "oui"
                        html.append("""<li>
                                           <a href="%s/folder_form?macro=macro_cours_afficher&amp;formulaire=masquer-element&amp;page=cours_plan_view&amp;section=plan&amp;tag=aucun&amp;idElement=%s"
                                              data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-eye-slash fa-fw"></i>Masquer</a>
                                       </li>""" % (self.absolute_url(), element["idElement"]))

                    html.append("""<li>
                                        <a href="%s/folder_form?macro=macro_cours&amp;formulaire=epingler-element&amp;idElement=%s&amp;epinglerPos=%s"
                                           data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-hand-o-left fa-fw"></i>Jalonner</a>
                                   </li>""" % (self.absolute_url(), element["idElement"], epinglerPos))
                    if element["idElement"] == idEpingler:
                        html.append("""<li>
                                            <a href="%s/folder_form?macro=macro_cours&amp;formulaire=desepingler-element&amp;idElement=%s"
                                               data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-hand-o-right fa-fw"></i>Déjalonner</a>
                                       </li>""" % (self.absolute_url(), element["idElement"]))
                    if infos_element["typeElement"] == "BoiteDepot":
                        idboite = element["idElement"].split("*-*")[-1]
                        html.append("""<li>
                                           <a href="%s/%s/folder_form?macro=macro_cours_boite&amp;formulaire=modifier-boite-info&amp;section=boite&amp;page=cours_plan_view&amp;idboite=%s"
                                              data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-cubes fa-fw"></i>Propriétés</a>
                                       </li>""" % (self.absolute_url(), idboite, idboite))
                        html.append("""<li>
                                           <a href="%s/%s/folder_form?macro=macro_cours_boite&amp;formulaire=modifier-boite-date&amp;section=boite&amp;page=cours_plan_view&amp;idboite=%s"
                                              data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-calendar-o fa-fw"></i>Dates</a>
                                       </li>""" % (self.absolute_url(), idboite, idboite))
                        html.append("""<li>
                                           <a href="%s/folder_form?macro=macro_form&amp;formulaire=detacher-cours&amp;idElement=%s&amp;repertoire=%s"
                                              data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-trash-o fa-fw"></i>Supprimer</a>
                                       </li>""" % (self.absolute_url(), element["idElement"], self.verifType(infos_element["typeElement"])))
                    if infos_element["typeElement"] in ["Video"]:
                        html.append("""<li>
                                           <a href="%s/folder_form?macro=macro_cours_video&amp;formulaire=modifier-video_infos&amp;idElement=%s"
                                              data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-cubes fa-fw"></i>Propriétés</a>
                                       </li>""" % (self.absolute_url(), element["idElement"]))
                    if infos_element["typeElement"] in ["Titre", "TexteLibre"]:
                        html.append("""<li>
                                           <a href="%s/folder_form?macro=macro_cours_plan&amp;formulaire=modifier-plan&amp;idElement=%s&amp;typeElement=%s"
                                              data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-pencil fa-fw"></i>Modifier</a>
                                       </li>""" % (self.absolute_url(), element["idElement"], infos_element["typeElement"]))

                    if infos_element["typeElement"] in ["AutoEvaluation", "Examen"]:
                        idActivite = element["idElement"].split("*-*")[-1]
                        html.append("""<li>
                                           <a href="%s/%s/folder_form?macro=macro_form&amp;formulaire=modifier-activite&amp;page=../&amp;idActivite=%s"
                                              data-reveal-id="reveal-main-large" data-reveal-ajax="true"><i class="fa fa-pencil fa-fw"></i>Modifier</a>
                                       </li>""" % (self.absolute_url(), idActivite, idActivite))

                    if infos_element["typeElement"] in ["Titre", "TexteLibre"]:
                        html.append("""<li>
                                           <a href="%s/cours_retirer_view?idElement=%s"
                                              data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-trash-o fa-fw"></i>Supprimer</a>
                                       </li>""" % (self.absolute_url(), element["idElement"]))
                    elif infos_element["typeElement"] not in ["AutoEvaluation", "Examen", "Glossaire", "BoiteDepot"]:
                        html.append("""<li>
                                           <a href="%s/folder_form?macro=macro_form&amp;formulaire=detacher-cours&amp;idElement=%s&amp;repertoire=%s"
                                              data-reveal-id="reveal-main" data-reveal-ajax="true"><i class="fa fa-chain-broken fa-fw"></i>Détacher</a>
                                       </li>""" % (self.absolute_url(), element["idElement"], self.verifType(infos_element["typeElement"])))
                    html.append("</ul>")
                    if isAffElement["icon2"]:
                        html.append("<i class='fa %s fa-fw fa-lg no-pad right' data-tooltip title='%s'></i>" % (isAffElement["icon2"], isAffElement["legende"]))
                    if isAffElement["icon"]:
                        html.append("<i class='fa %s fa-fw fa-lg no-pad right' data-tooltip title='masqué'></i>" % (isAffElement["icon"]))

                if nouveau:
                    html.append(nouveau)
                if element["idElement"] == idEpingler:
                    if commentaireEpingler:
                        commentaireEpingler = " data-tooltip title='%s'" % commentaireEpingler.replace("'", "’")
                    html.append("<i class='fa fa-hand-o-left fa-lg fa-fw no-pad jalonner'%s></i>" % commentaireEpingler)

                html.append("<span class='typeElement type_%s type_%s'>" % (infos_element["typeElement"].replace(" ", ""), categorieElement))

                if tag == "a":
                    html_etudiant = ""
                    if not personnel:
                        html_etudiant = "&amp;mode_etudiant=true"
                    html.append("""<a href="%s/cours_element_view?idElement=%s&amp;createurElement=%s&amp;typeElement=%s&amp;indexElement=%s%s"
                                       title="Voir cet élément du plan"
                                       data-reveal-id="reveal-main" data-reveal-ajax="true"
                                       class="typeElementTitre">%s""" % (self.absolute_url(), element["idElement"], infos_element["createurElement"], self.verifType(infos_element["typeElement"]), index, html_etudiant, infos_element["titreElement"]))
                    if "complementElement" in infos_element and infos_element["complementElement"]["value"]:
                        html.append("<div class=\"pod_thumb\"><img src=\"%s\" /></div>" % infos_element["complementElement"]["image"])

                    html.append("</a>")
                    # TODO : troncature coté serveur -> refonte du JS associé
                    #html.append("   <%s href='./cours_element_view?idElement=%s&createurElement=%s&typeElement=%s&indexElement=%s&requete_ajax=0' class='typeElementTitre'>%s</%s>" % (tag, element["idElement"], infos_element["createurElement"], self.verifType(infos_element["typeElement"]), index, self.getShortText( infos_element["titreElement"] ), tag))
                else:
                    html.append("<%s class='typeElementTitre'>%s" % (tag, infos_element["titreElement"]))
                    if infos_element["typeElement"] == "Titre" and personnel and len(element["listeElement"]) == 0:
                        html.append('<span class="title-legend"><i class="fa fa-info-circle fa-fw"></i>Faites glisser des éléments du plan dans le titre…</span>')
                    html.append("</%s>" % tag)

                html.append("</span>")
                if isTitre["class"] == "chapitre":
                    html.append("<ol>")
                    i = 0
                    for elem in element["listeElement"]:
                        index = "%s_%s" % (index, i)
                        i = i + 1
                        sous_elem = self.getPlanChapitre(elem, index, personnel, authMember, listeActualites)
                        if sous_elem:
                            html.append(sous_elem)
                    html.append("</ol>")
                html.append("</li>")
                return "\n".join(html)
            return None
        else:
            return None

    def getPlanRSS(self, personnel=False):
        #self.plone_log("getPlanRSS")
        rss = []
        idElements = self.getPlanPlat()
        for idElement in idElements:
            infos_element = self.getElementCours(idElement)
            if infos_element:
                isAffElement = self.isAfficherElement(infos_element["affElement"], infos_element["masquerElement"])
                if personnel or not isAffElement["val"] == 0:
                    if infos_element["typeElement"] in ["File"]:
                        element = self.getCoursElementRSS(idElement, infos_element["createurElement"])
                        if element:
                            #infos = dict(infos_element.items() + element.items())
                            element["affElement"] = infos_element["affElement"]
                            rss.append(element)
        return rss

    def getCoursElementRSS(self, idElement, createurElement):
        #self.plone_log("getCoursElementRSS")
        portal = self.portal_url.getPortalObject()
        if "*-*" in idElement:
            idElement = idElement.replace("*-*", ".")
        home = getattr(getattr(portal.Members, createurElement), "Fichiers", None)
        if home:
            element = getattr(home, idElement, None)
            if element:
                mime = element.getContentType()
                if mime in ['audio/mpeg', 'audio/x-m4a', 'video/mp4', 'video/x-m4v', 'video/quicktime', 'application/pdf', 'document/x-epub']:
                    return {
                        "idElement": idElement,
                        "titreElement": element.Title(),
                        "descriptionElement": element.Description(),
                        "urlElement": element.absolute_url(),
                        "mimeElement": mime,
                        "poidsElement": element.get_size(),
                    }
        return None

    def getCategorieiTunesU(self):
        #self.plone_log("getCategorieiTunesU")
        icon = 'jalon'

        jalon_properties = getToolByName(self, 'portal_jalon_properties')
        dicoLibCatITunesU = jalon_properties.getJalonProperty("dicoLibCatITunesU")
        idCatiTunesU = self.getCatiTunesU()
        try:
            main_category = dicoLibCatITunesU[idCatiTunesU[:3]]
            sub_category = dicoLibCatITunesU[idCatiTunesU]

            return {'main_category': main_category,
                    'sub_category':  sub_category,
                    'icon':          'http://itunesu.unice.fr/icones/%s.png' % icon}
        except:
            return None

    def getRechercheAcces(self):
        #self.plone_log("getRechercheAcces")
        acces = list(self.getListeAcces())
        groupe = self.getGroupe()
        if groupe:
            acces.extend(list(groupe))
        invitations = self.getInvitations()
        if invitations:
            acces.extend(list(invitations))
        inscriptionsLibres = self.getInscriptionsLibres()
        if inscriptionsLibres:
            acces.extend(list(inscriptionsLibres))
        return tuple(acces)

    def getRole(self):
        #self.plone_log("getRole")
        roles = {"createur":  False,
                 "auteur":    False,
                 "coauteur":  False,
                 "colecteur": False}
        authMember = self.portal_membership.getAuthenticatedMember().getId()
        if authMember == self.Creator():
            roles["auteur"] = True
        if authMember == self.getAuteurPrincipal():
            roles["auteur"] = True
        if authMember in self.getCoAuteurs():
            roles["coauteur"] = True
        if authMember in self.getCoLecteurs():
            roles["colecteur"] = True
        return roles

    def getRoleCat(self):
        #self.plone_log("getRoleCat")
        return {"auteur":    [self.Creator(), self.getAuteurPrincipal()],
                "coauteur":  self.getCoAuteurs(),
                "colecteur": self.getCoLecteurs()
                }

    def getMenuCours(self):
        #self.plone_log("getMenuCours")
        portal = self.portal_url.getPortalObject()
        portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
        mon_espace = portal_jalon_properties.getPropertiesMonEspace()

        retour = {"titre":     [],
                  "espace":    [],
                  "activites": [],
                  "rapide":    []}

        # Menu Mon Espace
        if mon_espace["activer_fichiers"]:
            retour["espace"].append({"rubrique": "Fichiers", "titre": "Fichiers", "icone": "fa fa-files-o fa-fw"})
        if mon_espace["activer_presentations_sonorisees"]:
            retour["espace"].append({"rubrique": urllib.quote("Presentations sonorisees"), "titre": "Présentations sonorisées", "icone": "fa fa-microphone fa-fw"})
        if mon_espace["activer_liens"]:
            retour["espace"].append({"rubrique": urllib.quote("Ressources Externes"), "titre": "Ressources externes", "icone": "fa fa-external-link fa-fw"})
        if mon_espace["activer_webconferences"]:
            retour["espace"].append({"rubrique": "Webconference", "titre": "Webconférence", "icone": "fa fa-headphones fa-fw"})

        # à retirer quand partie administration OK
        mon_espace["activer_videos"] = True
        if mon_espace["activer_videos"]:
            retour["espace"].append({"rubrique": "Video", "titre": "Vidéos", "icone": "fa fa-youtube-play fa-fw"})

        # Menu Activités
        retour["activites"].append({"rubrique": urllib.quote("Boite de depots"), "titre": "Boite de dépôts", "icone": "fa fa-fw fa-inbox"})
        if mon_espace["activer_exercices_wims"]:
            retour["activites"].append({"rubrique": urllib.quote("Auto evaluation"), "titre": "Auto évaluation WIMS", "icone": "fa fa-fw fa-gamepad"})
            retour["activites"].append({"rubrique": "Examen", "titre": "Examen WIMS", "icone": "fa fa-fw fa-graduation-cap"})
        if mon_espace["activer_webconferences"]:
            retour["activites"].append({"rubrique": urllib.quote("Salle virtuelle"), "titre": "Salle virtuelle", "icone": "fa fa-fw fa-globe"})

        # Menu Ajout rapide
        if mon_espace["activer_fichiers"]:
            retour["rapide"].append({"rubrique": "Fichiers", "titre": "Fichiers", "icone": "fa fa-files-o fa-fw"})
        if mon_espace["activer_liens"]:
            retour["rapide"].append({"rubrique": urllib.quote("Ressources Externes"), "titre": "Ressources externes", "icone": "fa fa-external-link fa-fw"})

        return retour

    def getRubriqueEspace(self, ajout=None):
        #self.plone_log("getRubriqueEspace")
        portal = self.portal_url.getPortalObject()
        portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
        mon_espace = portal_jalon_properties.getPropertiesMonEspace()
        liste = []
        if ajout in ["Supports", "BoiteDepot", "AutoEvaluation-sujets", "Examen-sujets"]:
            if mon_espace["activer_fichiers"]:
                liste.append({"rubrique": "Fichiers", "titre": "Fichiers"})
            if mon_espace["activer_presentations_sonorisees"]:
                liste.append({"rubrique": urllib.quote("Presentations sonorisees"), "titre": "Présentations sonorisées"})
            if mon_espace["activer_liens"]:
                liste.append({"rubrique": urllib.quote("Ressources Externes"), "titre": "Liens"})
            if mon_espace["activer_webconferences"]:
                liste.append({"rubrique": "Webconference", "titre": "Webconférence"})
        if ajout == "Rapide":
            if mon_espace["activer_fichiers"]:
                liste.append({"rubrique": "Fichiers", "titre": "Fichiers"})
            if mon_espace["activer_liens"]:
                liste.append({"rubrique": urllib.quote("Ressources Externes"), "titre": "Liens"})
        if ajout in ["AutoEvaluation-exercices", "Examen-exercices"]:
            if mon_espace["activer_exercices_wims"]:
                liste.append({"rubrique": urllib.quote("Exercices Wims"), "titre": "Exercices Wims"})
        if ajout == "Activites":
            liste.append({"rubrique": urllib.quote("Boite de depots"), "titre": "Boite de dépôts"})
            if mon_espace["activer_exercices_wims"]:
                liste.append({"rubrique": urllib.quote("Auto evaluation"), "titre": "Auto évaluation WIMS"})
                liste.append({"rubrique": "Examen", "titre": "Examen WIMS"})
            if mon_espace["activer_webconferences"]:
                liste.append({"rubrique": urllib.quote("Salle virtuelle"), "titre": "Salle virtuelle"})
        return liste

    #getSousObjet renvoie le sous-objet idElement
    def getSousObjet(self, idElement):
        #self.plone_log("getSousObjet")
        if "*-*" in idElement:
            idElement = idElement.split("*-*")[-1]
        return getattr(self, idElement)

    #getTypeSousObjet renvoie le type du sous-objet idElement
    def getTypeSousObjet(self, idElement):
        #self.plone_log("getTypeSousObjet")
        if "*-*" in idElement:
            typeSousObjet = idElement.split("*-*")[0]
        else:
            typeSousObjet = idElement.split("-")[0]
        return typeSousObjet

    #getTagDefautObj
    def getTagDefautObj(self, ref, espace, authMember):
        #self.plone_log("getTagDefautObj")
        return None
        portal = self.portal_url.getPortalObject()
        if espace == "Exercices Wims":
            espace = "Wims"
        if espace == "Ressources Externes":
            espace = "Externes"
        if espace == "Presentations sonorisees":
            espace = "Sonorisation"
        home = getattr(getattr(portal.Members, authMember), espace, None)
        defaut = home.getTagDefaut()
        for tag in ref["Subject"]:
            if tag in defaut:
                return tag
        return None

    # getTag : ancien getTagType() Donne la liste des tags associés au type "espace"
    def getTag(self, authMember, espace):
        #self.plone_log("getTag")
        retour = []
        portal = self.portal_url.getPortalObject()
        if espace == "Exercices Wims":
            espace = "Wims"
        if espace in ["Ressources Externes", "Bibliographie"]:
            espace = "Externes"
        if espace == "Presentations sonorisees":
            espace = "Sonorisation"
        home = getattr(getattr(portal.Members, authMember), espace, None)
        if home:
            return home.getTag()
        return retour

    def getPageMacro(self, espace):
        #self.plone_log("getPageMacro")
        dicoMacro = {"Fichiers":                 {"page": "macro_cours_fichiers", "macro": "fichiers_liste"},
                     "Ressources Externes":      {"page": "macro_cours_externes", "macro": "externes_liste"},
                     "Presentations sonorisees": {"page": "macro_cours_webconference", "macro": "webconferences_liste"},
                     "Webconference":            {"page": "macro_cours_webconference", "macro": "webconferences_liste"},
                     "Video":                    {"page": "macro_cours_video", "macro": "video_liste"},
                     "Glossaire":                {"page": "macro_cours_glossaire", "macro": "termes_glossaire_liste"},
                     "Bibliographie":            {"page": "macro_cours_bibliographie", "macro": "bibliographie_liste"},
                     "Exercices Wims":           {"page": "macro_cours_activites", "macro": "exercices_wims_liste"}}
        return dicoMacro[espace]

    def getUrlWebconference(self, url):
        #self.plone_log("getUrlWebconference")
        url_base = self.connect("getAttribut", {"attribut": "url_connexion"}).split("/api")[0]
        id_reunion = url.split("/")[-2]
        authMember = self.portal_membership.getAuthenticatedMember()
        idMember = authMember.getId()
        fullname = authMember.getProperty("fullname", idMember)
        if id_reunion != idMember:
            return "%s/system/login-guest?account-id=7&next=/%s&path=/%s&set-lang=fr&chooser=1&guestName=%s" % (url_base, id_reunion, id_reunion, fullname)
        else:
            portal = self.portal_url.getPortalObject()
            home = getattr(getattr(getattr(portal, "Members"), idMember), "Webconference")
            session = home.getSessionConnect(idMember)
            return "%s/%s?session=%s" % (url_base, idMember, session)

    def getValAcces(self):
        #self.plone_log("getValAcces")
        acces = self.getAcces()
        if acces == u"Privé".encode("utf-8"):
            return 0
        if acces == u"Aux étudiants".encode("utf-8"):
            return 1
        if acces == u"Public".encode("utf-8"):
            return 2
        return 0

    def getWebconferencesAuteurs(self, personnel):
        #self.plone_log("getWebconferencesAuteurs")
        reunions = []
        creators = [self.Creator()]
        creators.extend(self.getCoAuteurs())
        dossiers = self.connect("getAttribut", {"attribut": "dossiers"})
        if dossiers:
            modele = ""
            for ligne in dossiers.split("\n"):
                if "Webconference" in ligne:
                    modele = ligne.split(":")[-1]
                    break
            if modele == "":
                return []
        if modele:
            actives = self.getWebconferences()
            for creator in creators:
                reunionsCreator = self.connect("rechercherReunions", {"login": creator, "modele": modele})
                if reunionsCreator:
                    for webconference in reunionsCreator:
                        webconference["active"] = self.test(webconference['id'] in actives, 1, 0)
                        webconference["urlSession"] = self.getUrlWebconference(webconference['url'])
                        if personnel or webconference["active"]:
                            reunions.append(webconference)
        return reunions

    def getWebconferencesUser(self, personnel, authMember):
        #self.plone_log("getWebconferencesUser")
        reunions = []
        dossiers = self.connect("getAttribut", {"attribut": "dossiers"})
        if dossiers:
            modele = ""
            for ligne in dossiers.split("\n"):
                if "Webconference" in ligne:
                    modele = ligne.split(":")[-1]
                    break
            if modele == "":
                return []
        if modele:
            actives = self.getWebconferences()
            reunionsCreator = self.connect("rechercherReunions", {"login": authMember, "modele": modele})
            if reunionsCreator:
                for webconference in reunionsCreator:
                    webconference["active"] = self.test(webconference['id'] in actives, 1, 0)
                    webconference["urlSession"] = self.getUrlWebconference(webconference['url'])
                    if personnel or webconference["active"]:
                        reunions.append(webconference)
        return reunions

    def getWebconferenceUrlById(self, authMember, webid):
        #self.plone_log("getWebconferenceUrlById")
        for reunion in self.getWebconferencesUser(True, authMember):
            if reunion["id"] == webid:
                return self.getUrlWebconference(reunion['url'])
        return ""

    def getFilAriane(self, portal, folder, authMemberId):
        #self.plone_log("getFilAriane")
        return jalon_utils.getFilAriane(portal, folder, authMemberId)

    def setAccesApogee(self, elements):
        #self.plone_log("setAccesApogee")
        self.listeAcces = tuple(set(elements))
        self.setProperties({"DateDerniereModif": DateTime()})

    def setAuteur(self, form):
        ancienPrincipal = self.getAuteurPrincipal()
        if not ancienPrincipal:
            ancienPrincipal = self.Creator()
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été ajouté comme auteur du cours "%s" ayant eu pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace Mes cours.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), portal.absolute_url(), portal.Title())
        self.auteurPrincipal = form["username"]
        infosMembre = self.getInfosMembre(form["username"])
        #self.tagBU(ancienPrincipal)
        self.envoyerMail({"a":       infosMembre["email"],
                          "objet":   "Vous avez été ajouté à un cours",
                          "message": message})
        infosMembre = self.getInfosMembre(ancienPrincipal)
        message = 'Bonjour\n\nVous avez été retiré du cours "%s" ou vous êtiez auteur.\n\nCordialement,\n%s.' % (self.Title(), portal.Title())
        self.envoyerMail({"a":       infosMembre["email"],
                          "objet":   "Vous avez été retiré d'un cours",
                          "message": message})
        self.manage_setLocalRoles(form["username"], ["Owner"])
        self.setProperties({"DateDerniereModif": DateTime()})

    def addOffreFormations(self, elements):
        listeOffreFormations = list(self.getListeAcces())
        for formation in elements:
            if not formation in listeOffreFormations:
                listeOffreFormations.append(formation)
        self.listeAcces = tuple(listeOffreFormations)
        self.setProperties({"DateDerniereModif": DateTime()})

    def deleteOffreFormations(self, elements):
        self.listeAcces = tuple(elements)
        self.setProperties({"DateDerniereModif": DateTime()})

    def addCoAuteurs(self, form):
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été ajouté comme co-auteur du cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), portal.absolute_url(), portal.Title())
        coAuteurs = list(self.getCoAuteurs())
        usernames = form["username"].split(",")
        if usernames != ['']:
            for username in usernames:
                if not username in coAuteurs:
                    coAuteurs.append(username)
                    self.manage_setLocalRoles(username, ["Owner"])
                    infosMembre = self.getInfosMembre(username)
                    self.envoyerMail({"a":       infosMembre["email"],
                                      "objet":   "Vous avez été ajouté à un cours",
                                      "message": message})
            self.coAuteurs = tuple(coAuteurs)
        self.setProperties({"DateDerniereModif": DateTime()})

    def deleteCoAuteurs(self, form):
        auteurs = []
        if "auteur-actu" in form:
            auteurs = form["auteur-actu"]
        ancienAuteurs = set(self.getCoAuteurs())
        supprAuteurs = ancienAuteurs.difference(set(auteurs))

        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été retiré du cours "%s" ayant pour auteur %s ou vous êtiez co-auteur.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())

        for idMember in supprAuteurs:
            infosMembre = self.getInfosMembre(idMember)
            self.envoyerMail({"a":      infosMembre["email"],
                              "objet":  "Vous avez été retiré d'un cours",
                              "message": message})
        self.coAuteurs = tuple(auteurs)
        self.setProperties({"DateDerniereModif": DateTime()})

    def addLecteurs(self, form):
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été ajouté comme lecteur du cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), portal.absolute_url(), portal.Title())
        lecteurs = list(self.getCoLecteurs())
        usernames = form["username"].split(",")
        if usernames != ['']:
            for username in usernames:
                if not username in lecteurs:
                    lecteurs.append(username)
                    infosMembre = self.getInfosMembre(username)
                    self.envoyerMail({"a":       infosMembre["email"],
                                      "objet":   "Vous avez été ajouté à un cours",
                                      "message": message})
            self.coLecteurs = tuple(lecteurs)
        self.setProperties({"DateDerniereModif": DateTime()})

    def deleteLecteurs(self, form):
        lecteurs = []
        if "auteur-actu" in form:
            lecteurs = form["auteur-actu"]
        ancienLecteurs = set(self.getCoLecteurs())
        supprLecteurs = ancienLecteurs.difference(set(lecteurs))
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été retiré du cours "%s" ayant pour auteur %s ou vous êtiez lecteur.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())
        for idMember in supprLecteurs:
            infosMembre = self.getInfosMembre(idMember)
            self.envoyerMail({"a":       infosMembre["email"],
                              "objet":   "Vous avez été retiré d'un cours",
                              "message": message})
        self.coLecteurs = tuple(lecteurs)
        self.setProperties({"DateDerniereModif": DateTime()})

    def addInscriptionsNomminatives(self, form):
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été inscrit au cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), portal.absolute_url(), portal.Title())
        nomminatives = list(self.getGroupe())
        usernames = form["username"].split(",")
        if usernames != ['']:
            for username in usernames:
                if not username in nomminatives:
                    nomminatives.append(username)
                    infosMembre = self.getInfosMembre(username)
                    self.envoyerMail({"a":       infosMembre["email"],
                                      "objet":   "Vous avez été inscrit à un cours",
                                      "message": message})
        self.setGroupe(tuple(nomminatives))
        self.setProperties({"DateDerniereModif": DateTime()})

    def deleteInscriptionsNomminatives(self, form):
        nomminatives = []
        if "etu_groupe" in form:
            nomminatives = form["etu_groupe"]
        ancienNomminatives = set(self.getGroupe())
        supprNomminatives = ancienNomminatives.difference(set(nomminatives))
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été désinscrit du cours "%s" ayant pour auteur %s.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())
        for idMember in supprNomminatives:
            infosMembre = self.getInfosMembre(idMember)
            self.envoyerMail({"a":       infosMembre["email"],
                              "objet":   "Vous avez été désincrit d'un cours",
                              "message": message})
        self.setGroupe(tuple(nomminatives))
        self.setProperties({"DateDerniereModif": DateTime()})

    def addInvitationsEmail(self, form):
        invitations = list(self.getInvitations())
        if "invitation" in form and form["invitation"] != "":
            if "," in form["invitation"]:
                listeInvit = form["invitation"].split(",")
            else:
                listeInvit = [form["invitation"]]
            portal = self.portal_url.getPortalObject()
            portal_membership = getToolByName(portal, 'portal_membership')
            for invitation in listeInvit:
                invitation = invitation.strip()
                if "<" in invitation:
                    nameInvit, emailInvit = invitation.rsplit("<", 1)
                    #emailInvit = emailInvit.replace("<", "")
                    emailInvit = emailInvit.replace(">", "")
                else:
                    nameInvit = invitation.replace("@", " ")
                    emailInvit = invitation
                emailInvit = emailInvit.lower()
                if not emailInvit in invitations:
                    if not portal_membership.getMemberById(emailInvit):
                        portal_registration = getToolByName(portal, 'portal_registration')
                        password = portal_registration.generatePassword()
                        portal_membership.addMember(emailInvit, password, ("EtudiantJalon", "Member",), "", {"fullname": nameInvit, "email": emailInvit})
                        portal_registration.registeredNotify(emailInvit)
                    invitations.append(emailInvit)
                    message = 'Bonjour\n\nVous avez été inscrit au cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), portal.absolute_url(), portal.Title())
                    self.envoyerMail({"a":       emailInvit,
                                      "objet":   "Vous avez été inscrit à un cours",
                                      "message": message})
                self.setInvitations(tuple(invitations))
        self.setProperties({"DateDerniereModif": DateTime()})

    def deleteInvitationsEmail(self, form):
        invitations = []
        if "etu_email" in form:
            invitations = form["etu_email"]
        ancienInvitations = set(self.getInvitations())
        supprInvitations = ancienInvitations.difference(set(invitations))
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été désinscrit du cours "%s" ayant pour auteur %s.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())
        for idMember in supprInvitations:
            infosMembre = self.getInfosMembre(idMember)
            self.envoyerMail({"a":       infosMembre["email"],
                              "objet":   "Vous avez été désincrit d'un cours",
                              "message": message})
        self.setInvitations(tuple(invitations))
        self.setProperties({"DateDerniereModif": DateTime()})

    def setAttributCours(self, form):
        #self.plone_log("setAttributCours")
        for key in form.keys():
            if key == "acces":
                if self.getAcces() != form["acces"]:
                    portal = self.portal_url.getPortalObject()
                    portal_workflow = getToolByName(portal, "portal_workflow")
                    if form["acces"] == "Aux étudiants":
                        workflow_action = "submit"
                        state = "pending"
                    if form["acces"] == "Public":
                        #self.plone_log("[jaloncours/setAttributCours] (ACESS PUBLIC)")
                        workflow_action = "publish"
                        state = "published"
                        court = self.getLienCourt()
                        if not court:
                            dont_stop = 1
                            while dont_stop:
                                part1 = ''.join([random.choice(string.ascii_lowercase) for i in range(3)])
                                part2 = ''.join([random.choice(string.digits[1:]) for i in range(3)])
                                short = part1 + part2
                                objLien = getattr(portal.public, short, None)
                                if not objLien:
                                    dont_stop = 0
                            portal.public.invokeFactory(type_name="Link", id=short)
                            objLien = getattr(portal.public, short)
                            objLien.setTitle(self.title_or_id())
                            objLien.setRemoteUrl(self.absolute_url())
                            portal_workflow.doActionFor(objLien, workflow_action, "jalon_workflow")
                            objLien.reindexObject()
                            self.setLienCourt(short)

                        for objet in self.objectValues():
                            if portal_workflow.getInfoFor(objet, "review_state", wf_id="jalon_workflow") != state:
                                portal_workflow.doActionFor(objet, workflow_action, "jalon_workflow")
                                # On va modifier l'etat de tous les elements contenus dans les activités du cours.
                                # (mais cette étape est pour le moment inutile puisque les activités ne sont pas accessibles dans un cours Public)
                                if objet.meta_type in ["JalonBoiteDepot", "JalonCoursWims"]:
                                    relatedItems = objet.getRelatedItems()
                                    for related in relatedItems:
                                        # On ne rend pas public les exercices WIMS. l'objet lui-même ne reste accessible que par son propriétaire.
                                        if related.meta_type != "JalonExerciceWims" and portal_workflow.getInfoFor(related, "review_state", wf_id="jalon_workflow") != state:
                                            portal_workflow.doActionFor(related, workflow_action, "jalon_workflow")
                        for related in self.getRelatedItems():
                            if portal_workflow.getInfoFor(related, "review_state", wf_id="jalon_workflow") != state:
                                portal_workflow.doActionFor(related, workflow_action, "jalon_workflow")
                    try:
                        portal_workflow.doActionFor(self, workflow_action, "jalon_workflow")
                    except:
                        pass
            if key == "libre":
                if not self.getLienMooc():
                    part1 = ''.join([random.choice(string.ascii_lowercase) for i in range(3)])
                    part2 = ''.join([random.choice(string.digits[1:]) for i in range(3)])
                    part3 = ''.join([random.choice(string.ascii_uppercase) for i in range(3)])
                    short = part1 + part2 + part3
                    self.setLienMooc(short)
                if form[key] == "True":
                    self.setCategorie("2")
                else:
                    self.setCategorie("1")
            method_name = "set%s" % key.capitalize()
            if key == "catiTunesU":
                method_name = "setCatiTunesU"
                self.portal_jalon_properties.setUsersiTunesU(self.Creator())
                self.portal_jalon_properties.setCoursUser(self.Creator(), self.getId())

            if key == "diffusioniTunesU":
                method_name = "setDiffusioniTunesU"
            try:
                self.__getattribute__(method_name)(form[key])
            except AttributeError:
                #self.plone_log("Erreur %s : %s" % (str(method_name), str(form[key])))
                pass

            if key == "catiTunesU":
                portal = self.portal_url.getPortalObject()
                infosMembre = jalon_utils.getInfosMembre(self.Creator())
                jalon_utils.envoyerMail({"objet":   "Demande de publication sur iTunesU",
                                         "message": "Bonjour\n\n%s a fait une demande de publication sur iTunesU pour le cours \"%s\" dans la catégorie : \"%s\".\n\nVous pouvez la valider ou la rejeter depuis l'interface de configuration de %s\n\nCordialement,\nL'équipe %s" % (infosMembre["fullname"], self.Title(), self.getAffCatiTunesUCours(), portal.Title(), portal.Title()), })

        self.setProperties({"DateDerniereModif": DateTime()})

    def setGroupePerso(self, REQUEST):
        #self.plone_log("setGroupePerso")
        form = REQUEST.form
        etudiants = []
        if form["typeGroupe"] == "groupe":
            if "etu_groupe" in form:
                etudiants = form["etu_groupe"]
            if "username" in form:
                usernames = form["username"].split(",")
                if usernames != ['']:
                    for username in usernames:
                        if not username in etudiants:
                            etudiants.append(username)
            self.setGroupe(tuple(etudiants))
        elif form["typeGroupe"] == "libre":
            if "etu_libre" in form:
                etudiants = form["etu_libre"]
            self.setInscriptionsLibres(tuple(etudiants))
        else:
            if "etu_email" in form:
                etudiants = form["etu_email"]
            if "invitation" in form and form["invitation"] != "":
                if "," in form["invitation"]:
                    listeInvit = form["invitation"].split(",")
                else:
                    listeInvit = [form["invitation"]]
                portal = self.portal_url.getPortalObject()
                portal_membership = getToolByName(portal, 'portal_membership')
                for invitation in listeInvit:
                    invitation = invitation.strip()
                    if " " in invitation:
                        nameInvit, emailInvit = invitation.rsplit(" ", 1)
                        emailInvit = emailInvit.replace("<", "")
                        emailInvit = emailInvit.replace(">", "")
                    else:
                        nameInvit = invitation.replace("@", " ")
                        emailInvit = invitation
                    emailInvit = emailInvit.lower()
                    if not emailInvit in etudiants:
                        if not portal_membership.getMemberById(emailInvit):
                            portal_registration = getToolByName(portal, 'portal_registration')
                            password = portal_registration.generatePassword()
                            portal_membership.addMember(emailInvit, password, ("EtudiantJalon", "Member",), "", {"fullname": nameInvit, "email": emailInvit})
                            portal_registration.registeredNotify(emailInvit)
                        etudiants.append(emailInvit)
            self.setInvitations(tuple(etudiants))
        self.setProperties({"DateDerniereModif": DateTime()})
        return None

    def setFavoris(self, authMember):
        #self.plone_log("setFavoris")
        subjects = list(self.Subject())
        if not authMember in subjects:
            subjects.append(authMember)
        else:
            subjects.remove(authMember)
        self.setSubject(tuple(subjects))
        self.setProperties({"DateDerniereModif": DateTime()})

    def setLecture(self, lu, idElement, authMember):
        #self.plone_log("setLecture")
        dico = self.getElementCours(idElement)
        if not self.isAfficherElement(dico["affElement"], dico["masquerElement"])["val"]:
            return None
        if lu == 'true':
            if "lecture" in dico and not authMember in dico["lecture"]:
                dico["lecture"].append(authMember)
            else:
                dico["lecture"] = [authMember]

            if dico["typeElement"] == "Titre":
                for element in self.getEnfantPlanElement(idElement):
                        self.setLecture(lu, element["idElement"], authMember)
        else:
            if authMember in dico["lecture"]:
                dico["lecture"].remove(authMember)
        self._elements_cours[idElement] = dico
        self.setElementsCours(self._elements_cours)

    def marquerElement(self, idElement, marquer=None):
        dico = self.getElementCours(idElement)
        id_auth_member = self.portal_membership.getAuthenticatedMember().getId()
        if "marque" in dico:
            if not id_auth_member in dico["marque"]:
                dico["marque"].append(id_auth_member)
            else:
                dico["marque"].remove(id_auth_member)
        else:
            dico["marque"] = [id_auth_member]
        self._elements_cours[idElement] = dico
        self.setElementsCours(self._elements_cours)

    def setListeClasses(self, valeur):
        #self.plone_log("setListeClasses")
        self.listeclasses = tuple(valeur)

    def setPlanCours(self, plan):
        #self.plone_log("setPlanCours")
        self.plan = tuple(plan)

    def setProperties(self, dico):
        #self.plone_log("setProperties (Start)")
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        if key == "DateDerniereModif":
            #self.plone_log("DateDerniereModif")
            self.reindexObject()
        #self.plone_log("setProperties (End)")

    def setTagDefaut(self):
        #self.plone_log("setTagDefaut")
        return ""

    def delAccesApogee(self, elements):
        #self.plone_log("delAccesApogee")
        liste = list(self.getListeAcces())
        for element in elements:
            if element in liste:
                liste.remove(element)
            if element == "groupeperso*-*perso":
                self.setGroupe(())
            if element == "invitationsemail*-*email":
                self.setInvitations(())
        self.listeAcces = tuple(liste)
        self.setProperties({"DateDerniereModif": DateTime()})

    def isAfficherElement(self, affElement, masquerElement):
        #self.plone_log("isAfficherElement")
        return jalon_utils.isAfficherElement(affElement, masquerElement)

    def isAuteurs(self, username):
        #self.plone_log("jaloncours/isAuteurs = %s" % (self.isAuteur(username) or self.isCoAuteurs(username)))
        return self.isAuteur(username) or self.isCoAuteurs(username)

    def isAuteur(self, username):
        #self.plone_log("isAuteur")
        if username == self.Creator():
            return 1
        if username == self.getAuteurPrincipal():
            return 1
        return 0

    def isChecked(self, idElement, espace, listeElement=None):
        #self.plone_log("isChecked")
        if espace == "Glossaire":
            if idElement in list(self.getGlossaire()):
                return 1
            return 0
        if espace == "Bibliographie":
            if idElement in list(self.getBibliographie()):
                return 1
            return 0
        if espace in ["ajout-supports", "ajout-activite"]:
            return self.isInPlan(idElement, listeElement)

    def isInscriptionsLibre(self):
        #self.plone_log("isInscriptionsLibre")
        if len(self.getInscriptionsLibre()) > 0:
            return True
        else:
            return False

    def isCoAuteurs(self, username):
        u""" Détermine si l'utilisateur 'username' est un auteur ou co-auteur du cours."""
        if self.isAuteur(username):
            #self.plone_log("isCoAuteurs = 1 (isAuteur)")
            return 1
        if username in self.coAuteurs:
            #self.plone_log("isCoAuteurs = 1 (coAuteur)")
            return 1
        # Dans le cas de l'admin, isCoAuteurs renvoi 0 aussi
        #self.plone_log("isCoAuteurs = 0 (ni auteur, ni coAuteur)")
        return 0

    def isCoLecteurs(self, username):
        #self.plone_log("isCoLecteurs")
        if username in self.coLecteur:
            return 1
        return 0

    def isInPlan(self, idElement, listeElement=None):
        #self.plone_log("isInPlan : %s" % idElement)
        if not listeElement:
            listeElement = self.getPlanPlat()
        #listeIdElementPan = self.getPlanPlat()
        if idElement in listeElement:
            return 1
        return 0

    def isPersonnel(self, user, mode_etudiant="false"):
        #self.plone_log("jaloncours/isPersonnel")
        if mode_etudiant == "true":
            #self.plone_log("isPersonnel = False (mode étudiant)")
            return False
        if user.has_role("Manager"):
            #self.plone_log("isPersonnel = True (manager role)")
            return True
        if user.has_role("Personnel") and self.isCoAuteurs(user.getId()):
            #self.plone_log("isPersonnel = True (Personnel & iscoAuteurs)")
            return True
        return False

    def isTitre(self, categorieElement):
        #self.plone_log("isTitre")
        retour = {"condition": False, "class": "element"}
        if categorieElement == "Titre":
            retour = {"condition": True, "class": "chapitre"}
        if categorieElement == "TexteLibre":
            retour = {"condition": True, "class": "element"}
        return retour

    def activerWebconference(self, idwebconference):
        #self.plone_log("activerWebconference")
        webconferences = list(self.webconferences)
        if not idwebconference in webconferences:
            webconferences.append(idwebconference)
        else:
            webconferences.remove(idwebconference)
        self.webconferences = tuple(webconferences)

    def getActuCoursFull(self, date):
        #self.plone_log("getActuCoursFull")
        actualites = []
        descriptionActu = {"chapdispo":          _(u"et son contenu sont maintenant disponibles."),
                           "dispo":              _(u"est disponible."),
                           "datedepot":          _(u"modification de la date de dépôt : "),
                           "datedepotfin":       _(u"le dépôt n'est plus permis"),
                           "correctiondispo":    _(u"la correction est disponible."),
                           "sujetdispo":         _(u"le sujet est disponible."),
                           "nouveauxdepots":     _(u"nouveau(x) dépôt(s) disponible(s)"),
                           "nouveauxmessages":   _(u"nouveau(x) message(s) disponible(s)")}

        listeActualites = list(self.getActualites())
        listeActualites.sort(lambda x, y: cmp(y["dateActivation"], x["dateActivation"]))
        infos_elements = self.getElementCours()

        for actualite in listeActualites:
            if date > DateTime(actualite["dateActivation"]).Date():
                break
            elif date == DateTime(actualite["dateActivation"]).Date():
                infos_element = infos_elements.get(actualite["reference"], '')
                if infos_element:
                    description = descriptionActu[actualite["code"]]
                    if actualite["code"] == "datedepot":
                        description = "%s %s" % (description, DateTime(actualite["dateDepot"], datefmt='international').strftime("%d/%m/%Y %H:%M"))
                    if actualite["code"] == "nouveauxdepots":
                        description = "%s %s" % (str(actualite["nb"]), description)
                    actualites.append({"type":        infos_element["typeElement"],
                                       "titre":       infos_element["titreElement"],
                                       "description": description})
        return actualites

    def setActuCours(self, param):
        #self.plone_log("setActuCours")
        dicoActu = {"reference":      param["reference"],
                    "dateActivation": DateTime(),
                    "code":           param["code"],
                    "nb":             0,
                    "dateDepot":      None,
                    "acces":          ["auteurs", "etudiants"]
                    }
        listeActualites = list(self.getActualites())
        if param["code"] in ["nouveauxdepots", "nouveauxmessages"]:
            for actualite in listeActualites:
                if actualite["reference"] == param["reference"] and param["code"] == actualite["code"] and DateTime(actualite["dateActivation"]).Date() == DateTime().Date():
                    dicoActu = actualite.copy()
                    listeActualites.remove(actualite)
                    break
            dicoActu["nb"] = dicoActu["nb"] + 1
            dicoActu["dateActivation"] = DateTime()
        if param["code"] == "datedepot":
            dicoActu["dateDepot"] = param["dateDepot"]
            dicoActu["dateActivation"] = DateTime()
        if param["code"] not in ["nouveauxdepots", "nouveauxmessages", "datedepot"]:
            dicoActu["dateActivation"] = param["dateActivation"]
        listeActualites.append(dicoActu)
        self.actualites = tuple(listeActualites)
        self.setDateDerniereActu(self.actualites)
        self.setProperties({"DateDerniereModif": DateTime()})

    def delActu(self, idElement):
        #self.plone_log("delActu")
        newActu = []
        listeActualites = list(self.getActualites())
        for actu in listeActualites:
            if idElement != actu["reference"]:
                newActu.append(actu)
        self.actualites = tuple(newActu)
        self.setProperties({"DateDerniereModif": DateTime()})

    def afficherRessource(self, idElement, dateAffichage, attribut, chapitre=None):
        u""" Modifie l'etat de la ressource quand on modifie sa visibilité ("attribut" fournit l'info afficher / masquer)."""
        #self.plone_log("afficherRessource")
        dico = self.getElementCours(idElement)
        if dico:
            rep = {"Image":                     "Fichiers",
                   "File":                      "Fichiers",
                   "Lien web":                  "Externes",
                   "Lecteur exportable":        "Externes",
                   "Reference bibliographique": "Externes",
                   "Glossaire":                 "Glossaire",
                   "Webconference":             "Webconference",
                   "Presentations sonorisees":  "Sonorisation"}
            if dico["typeElement"] in rep.keys():
                portal = self.portal_url.getPortalObject()
                try:
                    objet = getattr(getattr(getattr(getattr(portal, "Members"), dico["createurElement"]), rep[dico["typeElement"]]), idElement.replace("*-*", "."))
                except:
                    return None
                portal_workflow = getToolByName(portal, "portal_workflow")
                cours_state = portal_workflow.getInfoFor(self, "review_state", wf_id="jalon_workflow")
                objet_state = portal_workflow.getInfoFor(objet, "review_state", wf_id="jalon_workflow")
                if attribut == "affElement" and cours_state != objet_state and cours_state == "published":
                    portal_workflow.doActionFor(objet, "publish", "jalon_workflow")

            # Cas des activités
            if dico["typeElement"] in ["AutoEvaluation", "BoiteDepot", "Examen", "Forum"]:
                obj = self.getSousObjet(idElement)
                resultat_affichage = obj.afficherRessource(idElement, dateAffichage, attribut)
                if resultat_affichage:
                    # resultat_affichage["val"] indique "False" si l'affichage n'a pas été fait.
                    if not resultat_affichage["val"]:
                        # resultat_affichage["reason"] peut indiquer la raison pour laquelle l'affichage est refusé.
                        return resultat_affichage

            descriptionElement = ""
            dico[attribut] = dateAffichage
            if attribut == "affElement":
                dico["masquerElement"] = ""
                descriptionElement = "dispo"
            self._elements_cours[idElement] = dico
            self.setElementsCours(self._elements_cours)

            isNotSetActu = True
            if attribut == "masquerElement":
                self.delActu(idElement)
                isNotSetActu = False

            # Quand on affiche un element directement, on l'ajoute aux actus du cours.
            if descriptionElement and not chapitre:
                actualites = list(self.getActualites())
                dicoActu = {"reference":      idElement,
                            "dateActivation": dateAffichage,
                            "code":           descriptionElement,
                            "acces":          ["auteurs", "etudiants"]
                            }
                if (actualites and not dicoActu in actualites) or not actualites:
                    self.setActuCours(dicoActu)
                    isNotSetActu = False
            if isNotSetActu:
                self.setProperties({"DateDerniereModif": DateTime()})

    # Affiche (ou masque) un chapitre du cours, ainsi que tout son contenu
    def afficherRessourceChapitre(self, idElement, dateAffichage, attribut, listeElement=None):
        #self.plone_log("afficherRessourceChapitre")
        descriptionElement = ""
        #attribut = masquerElement ou affElement
        if attribut == "affElement":
            descriptionElement = "chapdispo"

        # lors d'un affichage, on ajoute l'actions aux actus du cours
        if descriptionElement:
            actualites = list(self.getActualites())
            dicoActu = {"reference":      idElement,
                        "dateActivation": dateAffichage,
                        "code":           descriptionElement,
                        "nb":             0,
                        "dateDepot":      None,
                        "acces":          ["auteurs", "etudiants"]
                        }
            if not actualites:
                self.setActuCours(dicoActu)
            elif dicoActu not in actualites:
                self.setActuCours(dicoActu)

        if listeElement is None:
            listeElement = list(self.getPlan())

        for element in listeElement:
            if element["idElement"] == idElement or idElement == "all":
                # On commence par afficher le chapitre lui-même
                self.afficherRessource(element["idElement"], dateAffichage, attribut, "chapitre")
                if "listeElement" in element:
                    for souselem in element["listeElement"]:
                        #Puis on affiche tous les elements du chapitre
                        self.afficherRessource(souselem["idElement"], dateAffichage, attribut, "chapitre")
                        if "listeElement" in souselem:
                            # Si un des éléments est un sous-chapitre, on affiche son contenu recursivement.
                            self.afficherRessourceChapitre("all", dateAffichage, attribut, souselem["listeElement"])
                #Lorsqu'on a trouvé le chapitre qu'on cherchait, plus besoin de continuer à parcourir le plan.
                if element["idElement"] == idElement:
                    break
            elif "listeElement" in element:
                self.afficherRessourceChapitre(idElement, dateAffichage, attribut, element["listeElement"])

    # Affiche un chapitre du cours et ses parents jusqu'à atteindre la racine
    def afficherChapitresParent(self, idElement, dateAffichage):
        #self.plone_log("afficherChapitresParent")
        dicoActu = {"reference":      idElement,
                    "dateActivation": dateAffichage,
                    "code":           "dispo",
                    "nb":             0,
                    "dateDepot":      None,
                    "acces":          ["auteurs", "etudiants"]
                    }
        actualites = list(self.getActualites())
        if not actualites:
            self.setActuCours(dicoActu)
        elif dicoActu not in actualites:
            self.setActuCours(dicoActu)

        dico = self.getElementCours(idElement)
        dico["affElement"] = dateAffichage
        dico["masquerElement"] = ""
        self._elements_cours[idElement] = dico
        self.setElementsCours(self._elements_cours)

        parent = self.getParentPlanElement(idElement, 'racine', '')
        if parent["idElement"] != "racine":
            self.afficherChapitresParent(parent["idElement"], dateAffichage)
        else:
            idElement = "racine"

    def getParentPlanElement(self, idElement, idParent, listeElement):
        #self.plone_log("getParentPlanElement")
        if idParent == "racine":
            listeElement = self.plan
        for element in listeElement:
            if idElement == element["idElement"]:
                if idParent == "racine":
                    return {"idElement": "racine", "affElement": "", "masquerElement": ""}
                else:
                    dico = dict(self.getElementCours(idParent))
                    dico["idElement"] = idParent
                    return dico
            elif "listeElement" in element:
                retour = self.getParentPlanElement(idElement, element["idElement"], element["listeElement"])
                if retour:
                    return retour
        return None

    def getEnfantPlanElement(self, idElement, listeElement=None):
        #self.plone_log("getEnfantPlanElement")
        if listeElement is None:
            listeElement = self.plan
        for element in listeElement:
            if element["idElement"] == idElement and "listeElement" in element:
                return element["listeElement"]
            elif "listeElement" in element:
                retour = self.getEnfantPlanElement(idElement, element["listeElement"])
                if retour:
                    return retour
        return None

    def ajouterElement(self, idElement, typeElement, titreElement, createurElement, affElement="", position=None, display_in_plan=False):
        #self.plone_log("ajouterElement")
        remplacer = False
        if typeElement == "Glossaire":
            glossaire = list(self.getGlossaire())
            glossaire.append(idElement)
            self.setElements_glossaire(glossaire)
            typeElement = "TermeGlossaire"
        elif "*-*" in typeElement:
            bibliographie = list(self.getBibliographie())
            bibliographie.append(idElement)
            self.setElements_bibliographie(bibliographie)
            typeElement = typeElement.split("*-*")[1]
        else:
            if self.isInPlan(idElement.replace(".", "*-*")):
                return None
            self.ajouterElementPlan(idElement, position)
            if "." in idElement:
                remplacer = True

        complement_element = None
        rep = {"Image":                     "Fichiers",
               "File":                      "Fichiers",
               "Page":                      "Fichiers",
               "Lien web":                  "Externes",
               "Lecteur exportable":        "Externes",
               "Reference bibliographique": "Externes",
               "Video":                     "Video",
               "Catalogue BU":              "Externes",
               "TermeGlossaire":            "Glossaire",
               "Webconference":             "Webconference",
               "Presentations sonorisees":  "Sonorisation"}
        if typeElement in rep:
            portal = self.portal_url.getPortalObject()
            objet = getattr(getattr(getattr(getattr(portal, "Members"), createurElement), rep[typeElement]), idElement)
            if remplacer:
                idElement = idElement.replace(".", "*-*")
            if affElement:
                portal_workflow = getToolByName(portal, "portal_workflow")
                cours_state = portal_workflow.getInfoFor(self, "review_state", wf_id="jalon_workflow")
                objet_state = portal_workflow.getInfoFor(objet, "review_state", wf_id="jalon_workflow")
                if cours_state != objet_state and cours_state == "published":
                    portal_workflow.doActionFor(objet, "publish", "jalon_workflow")
                dicoActu = {"reference":      idElement,
                            "code":           "dispo",
                            "dateActivation": DateTime()}
                self.setActuCours(dicoActu)
            relatedItems = objet.getRelatedItems()
            if not self in relatedItems:
                relatedItems.append(self)
                objet.setRelatedItems(relatedItems)
                objet.reindexObject()
            coursRelatedItems = self.getRelatedItems()
            if not objet.getId() in coursRelatedItems:
                coursRelatedItems.append(objet)
                self.setRelatedItems(coursRelatedItems)

            if typeElement == "Video":
                complement_element = {"value":  display_in_plan,
                                      "auteur": objet.getVideoauteurname(),
                                      "image":  objet.getVideothumbnail()}

        self.ajouterInfosElement(idElement, typeElement, titreElement, createurElement, affElement=affElement, complementElement=complement_element)

    def ajouterElementPlan(self, idElement, position=None):
        #self.plone_log("ajouterElementPlan")
        plan = list(self.getPlan())
        if idElement.startswith("Titre"):
            element_add = {"idElement": idElement, "listeElement": []}
        else:
            if "." in idElement and not (idElement.startswith("BoiteDepot") or idElement.startswith("AutoEvaluation") or idElement.startswith("Examen")):
                idElement = idElement.replace(".", "*-*")
            element_add = {"idElement": idElement}
        if not position:
            plan.append(element_add)
        elif position == "debut_racine":
            plan.insert(0, element_add)
        else:
            liste_titres = position.split("*-*")
            self.setPosition(idElement, plan, liste_titres[1:])

        self.plan = tuple(plan)
        #self.setProperties({"DateDerniereModif": DateTime()})

    def setPosition(self, idElement, listeElement, liste_titres):
        #self.plone_log("setPosition")
        if len(liste_titres) > 1:
            for element in listeElement:
                if element["idElement"] == liste_titres[0]:
                    self.setPosition(idElement, element["listeElement"], liste_titres[1:])
        else:
            for element in listeElement:
                if element["idElement"] == liste_titres[0]:
                    if idElement.startswith("Titre"):
                        element_add = {"idElement": idElement, "listeElement": []}
                    else:
                        if "." in idElement:
                            idElement = idElement.replace(".", "*-*")
                        element_add = {"idElement": idElement}
                    element["listeElement"].append(element_add)
                    break

    def ajouterInfosElement(self, idElement, typeElement, titreElement, createurElement, affElement="", complementElement=None):
        #self.plone_log("ajouterInfosElement")
        parent = self.getParentPlanElement(idElement, 'racine', '')
        if parent and parent['idElement'] != 'racine':
            isAfficher = self.isAfficherElement(parent['affElement'], parent['masquerElement'])['val']
            if not isAfficher:
                affElement = ""

        infos_element = self.getElementCours()
        if not idElement in infos_element:
            infos_element[idElement] = {"titreElement":    titreElement,
                                        "typeElement":     typeElement,
                                        "createurElement": createurElement,
                                        "affElement":      affElement,
                                        "masquerElement":  ""}
            if complementElement:
                infos_element[idElement]["complementElement"] = complementElement
            self.setElementsCours(infos_element)
        #self.setProperties({"DateDerniereModif": DateTime()})

    def authUser(self, quser=None, qclass=None, request=None):
        #self.plone_log("authUser")
        return jalon_utils.authUser(self, quser, qclass, request)

    def creerSousObjet(self, typeElement, titreElement, descriptionElement, createurElement, publicsElement, mailAnnonce):
        #self.plone_log("creerSousObjet (Start)")
        dicoType = {"BoiteDepot":     "JalonBoiteDepot",
                    "AutoEvaluation": "JalonCoursWims",
                    "Examen":         "JalonCoursWims",
                    "Forum":          "PloneboardForum",
                    "Annonce":        "JalonAnnonce"}
        rep = self
        if typeElement == "Annonce":
            rep = self.annonce
        elif typeElement == "Actu":
            rep = self.actu
        elif typeElement == "Forum":
            rep = self.forum
        #self.plone_log("invokeFactory %s (Start)" % dicoType[typeElement])
        idElement = rep.invokeFactory(type_name=dicoType[typeElement], id="%s-%s-%s" % (typeElement, createurElement, DateTime().strftime("%Y%m%d%H%M%S%f")))
        #self.plone_log("invokeFactory %s (End)" % dicoType[typeElement])
        element = getattr(rep, idElement)
        if typeElement == "Forum":
            element.setTitle(titreElement)
            element.setDescription(descriptionElement)
            element.setMaxAttachments(0)
            element.reindexObject()
        else:
            element.setProperties({"Title":       titreElement,
                                   "Description": descriptionElement})
        if typeElement == "Annonce":
            element.setProperties({"Publics": publicsElement})
            if mailAnnonce:
                element.envoyerAnnonce()
        #self.setProperties({"DateDerniereModif": DateTime()})
        #self.plone_log("creerSousObjet (End)")
        return idElement

    def connect(self, methode, param):
        #self.plone_log("connect")
        connect = getToolByName(self, jalon_utils.getAttributConf("webconference_connecteur"))
        return connect.__getattribute__(methode)(param)

    def detacherElement(self, ressource, createur, repertoire):
        #self.plone_log("detacherElement")
        dicoRep = {"Image":                    "Fichiers",
                   "File":                     "Fichiers",
                   "Page":                     "Fichiers",
                   "Lienweb":                  "Externes",
                   "Lecteurexportable":        "Externes",
                   "Referencebibliographique": "Externes",
                   "CatalogueBU":              "Externes",
                   "Catalogue BU":             "Externes",
                   "TermeGlossaire":           "Glossaire",
                   "Presentationssonorisees": "Sonorisation"}
        if repertoire in dicoRep:
            repertoire = dicoRep[repertoire]
        if "*-*" in ressource:
            ressource = ressource.replace("*-*", ".")
        try:
            objet = getattr(getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), createur), repertoire), ressource)
            relatedItems = objet.getRelatedItems()
            relatedItems.remove(self)
            objet.setRelatedItems(relatedItems)
            objet.reindexObject()
        except:
            pass
        self.setProperties({"DateDerniereModif": DateTime()})

    def encodeUTF8(self, itemAEncoder):
        #self.plone_log("encodeUTF8")
        return jalon_utils.encodeUTF8(itemAEncoder)

    def envoyerMail(self, form):
        #self.plone_log("envoyerMail")
        jalon_utils.envoyerMail(form)

    def envoyerMailErreur(self, form):
        #self.plone_log("envoyerMailErreur")
        jalon_utils.envoyerMailErreur(form)

    def modifierInfosBoitePlan(self, idElement, param):
        #self.plone_log("modifierInfosBoitePlan")
        dico = self.getElementCours(idElement)
        for attribut in param.keys():
            dico[attribut] = param[attribut]
        self._elements_cours[idElement] = dico
        self.setElementsCours(self._elements_cours)
        self.setProperties({"DateDerniereModif": DateTime()})

    def modifierInfosElementPlan(self, idElement, titreElement):
        #self.plone_log("modifierInfosElementPlan")
        dico = self.getElementCours(idElement)
        dico["titreElement"] = titreElement
        self._elements_cours[idElement] = dico
        self.setElementsCours(self._elements_cours)
        self.setProperties({"DateDerniereModif": DateTime()})

    def ordonnerElementPlan(self, pplan):
        #self.plone_log("ordonnerElementPlan")
        plan = []
        dicoplan = {}
        pre_plan = pplan.split("&")
        for element in pre_plan:
            clef, valeur = element.split("=")
            typeElement, idElement = clef[:-1].split("[")
            dicoplan[idElement] = valeur

        def getParentPlan(idElement):
            parent = dicoplan[idElement]
            if parent == "null":
                return {"idElement": "racine", "listeElement": plan}
            else:
                racine = getParentPlan(parent)
                return {"idElement": racine["listeElement"][-1]["idElement"], "listeElement": racine["listeElement"][-1]["listeElement"]}

        dicoElements = self.getElementCours()
        for element in pre_plan:
            clef, valeur = element.split("=")
            typeElement, idElement = clef[:-1].split("[")
            infosElement = dicoElements[idElement]
            isAfficherElement = self.isAfficherElement(infosElement["affElement"], infosElement["masquerElement"])["val"]
            if typeElement == "chapitre":
                p = getParentPlan(idElement)
                if p["idElement"] != "racine":
                    pInfosElement = self.getElementCours(p["idElement"])
                    isPAfficherElement = self.isAfficherElement(pInfosElement["affElement"], pInfosElement["masquerElement"])["val"]
                    if isAfficherElement and not isPAfficherElement:
                        self.afficherRessourceChapitre(idElement, DateTime(), "masquerElement")
                p["listeElement"].append({"idElement": idElement, "listeElement": []})
            else:
                p = getParentPlan(idElement)
                if p["idElement"] != "racine":
                    pInfosElement = self.getElementCours(p["idElement"])
                    isPAfficherElement = self.isAfficherElement(pInfosElement["affElement"], pInfosElement["masquerElement"])["val"]
                    if isAfficherElement and not isPAfficherElement:
                        self.afficherRessource(idElement, DateTime(), "masquerElement")
                p["listeElement"].append({"idElement": idElement})

        self.plan = tuple(plan)
        self.setProperties({"DateDerniereModif": DateTime()})
        return self.getPlanCours(True)

    def purgerActivitesWims(self):
        u"""Supprime l'ensemble des travaux effectués dans toutes les activités Wims d'un cours."""
        #self.plone_log("purgerActivitesWims")
        dico_classes = self.getListeClasses()
        retour = {}
        if dico_classes:
            dico_classes = dico_classes[0]

            authMember = self.portal_membership.getAuthenticatedMember().getId()
            for user in dico_classes.keys():
                class_id = dico_classes[user]
                dico = {"qclass": class_id, "code": authMember}
                rep = self.wims("cleanClass", dico)
                retour[user] = rep

        return retour

    def supprimerActivitesWims(self, utilisateur="All"):
        u"""Suppression de toutes les activites WIMS du cours, créées par 'utilisateur'."""
        # Retirer toutes les activités du plan

        # Ici on utilise getElementCours() plutot que getPlanPlat,
        # Cela permet de prendre egalement d'éventuels elements mal supprimés qui sont toujours "la", mais plus dans le plan.
        # nb : on pourrait également parcourir "for idElement in self.objectIds()", afin de lister les objets réellement dans le cours.
        #dicoElements = copy.deepcopy(self.getElementCours())

        liste_activitesWIMS = []
        #portal_members = getattr(self.portal_url.getPortalObject(), "Members")
        #for idElement in dicoElements:
        for idElement in self.objectIds():
            #infosElement = dicoElements[idElement]
            #if infosElement and infosElement["typeElement"] in ["AutoEvaluation", "Examen"]:
            if (idElement.startswith("AutoEvaluation") or idElement.startswith("Examen")):
                # self.plone_log("[jaloncours/supprimerActivitesWims] ACTIVITE :'%s'" % element)
                if utilisateur == "All" or infosElement["createurElement"] == utilisateur:
                    #self.plone_log("[jaloncours/supprimerActivitesWims] suppression de '%s'" % element)
                    liste_activitesWIMS.append(idElement)

                    # On parcourt ensuite les exo des activitées retirées, pour que chaque exercice n'y fasse plus référence dans ses "relatedITEMS"
                    activite = getattr(self, idElement)

                    # retire l'activité des relatedItems pour ses exercices et ses documents.
                    activite.retirerTousElements(force_WIMS=True)

                    # Supprime l'activité (du plan du cours et du cours)
                    self.retirerElementPlan(idElement, force_WIMS=True)
                    # Supprime l'activité des actus du cours
                    self.delActu(idElement)

                    ### A utiliser dans un patch correctif :
                    #(on refait ce que fait normalement retirerElementPlan, sauf dans le cas ou l'element n'est plus dans le plan) :
                    self.manage_delObjects(idElement)
                    if idElement in self._elements_cours:
                        del self._elements_cours[idElement]

        # Supprime toutes les classes du serveur WIMS
        listeClasses = list(self.getListeClasses())
        removed_classes = []
        dico = listeClasses[0]
        #self.plone_log("[jaloncours/supprimerActivitesWims] Ancienne liste :'%s'" % listeClasses)
        new_listeClasses = []
        for auteur in dico:
            if utilisateur == "All" or utilisateur == auteur:
                removed_classes.append(dico[auteur])
            else:
                if len(new_listeClasses) == 0:
                    new_listeClasses.append({auteur: dico[auteur]})
                else:
                    new_listeClasses[0][auteur] = dico[auteur]
        if removed_classes is not None:
            self.aq_parent.delClassesWims(removed_classes)

        # Et enfin remettre à zero la liste des classes du cours.
        #self.plone_log("[jaloncours/supprimerActivitesWims] Nouvelle liste :'%s'" % new_listeClasses)
        self.setListeClasses(new_listeClasses)

        # Renvoit le nombre d'activités supprimées.
        return len(liste_activitesWIMS)

    # rechercheApogee
    def rechercheApogee(self, recherche, termeRecherche):
        #self.plone_log("rechercheApogee")
        if not termeRecherche:
            return None
        termeRecherche.strip()
        termeRecherche = "%" + termeRecherche + "%"
        termeRecherche = termeRecherche.replace(" ", "% %")
        listeRecherche = termeRecherche.split(" ")

        #apogee = getToolByName(self, "portal_apogee")
        portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
        if recherche == "etape":
            return portal_jalon_bdd.rechercherEtape(listeRecherche)
        if recherche == "ue":
            return portal_jalon_bdd.rechercherELP(listeRecherche, 0)
        if recherche == "uel":
            return portal_jalon_bdd.rechercherELP(listeRecherche, 1)
        if recherche == "groupe":
            return portal_jalon_bdd.rechercherGPE(listeRecherche)
        return None

    def rechercherUtilisateur(self, username, typeUser, match=False, json=True):
        #self.plone_log("rechercherUtilisateur")
        return jalon_utils.rechercherUtilisateur(username, typeUser, match, json)

    def retirerElement(self, idElement):
        #self.plone_log("retirerElement")
        elements_glossaire = list(self.getGlossaire())
        if idElement in elements_glossaire:
            elements_glossaire.remove(idElement)
            self.elements_glossaire = tuple(elements_glossaire)
            infos_element = self.getElementCours()
            infosElement = infos_element[idElement]
            self.detacherElement(idElement, infosElement["createurElement"], infosElement["typeElement"])
            del infos_element[idElement]
        elements_bibliographie = list(self.getBibliographie())
        if idElement in elements_bibliographie:
            elements_bibliographie.remove(idElement)
            self.elements_bibliographie = tuple(elements_bibliographie)
            if not self.isInPlan(idElement):
                infos_element = self.getElementCours()
                infosElement = infos_element[idElement]
                self.detacherElement(idElement, infosElement["createurElement"], infosElement["typeElement"].replace(" ", ""))
                del infos_element[idElement]
        self.setProperties({"DateDerniereModif": DateTime()})

    def retirerElementPlan(self, idElement, listeElement=None, force_WIMS=False):
        """ Fonction recursive qui supprime l'element idElement du plan, ainsi que tout son contenu si c'est un Titre."""
        #LOG.info("retirerElementPlan")
        start = False
        if listeElement is None:
            listeElement = list(self.getPlan())
            start = True
        for element in listeElement:
            if element["idElement"] == idElement or idElement == "all":
                #Si element contient lui-même une liste d'elements, on appelle a nouveau cette fonction
                #   avec le parametre "all" et la liste des elements a supprimer
                if "listeElement" in element and element["listeElement"] != []:
                    self.retirerElementPlan("all", element["listeElement"], force_WIMS)

                #on supprime element de la liste où il etait dans le plan
                while element in listeElement:
                    listeElement.remove(element)

                infosElement = self.getElementCours().get(element["idElement"])

                if infosElement:
                    #dans le cas des autoevaluations et examens, on ne supprime pas l'element du plan, on ne fait que le déplacer
                    if infosElement["typeElement"] in ["AutoEvaluation", "Examen"] and force_WIMS is False:
                        self.ajouterElementPlan(element["idElement"])
                    else:

                        if not (element["idElement"] in self.getGlossaire() or element["idElement"] in self.getBibliographie()):
                            # Si ce n'est pas un element Biblio ou Glossaire, on le supprime des objets du cours
                            del self._elements_cours[element["idElement"]]
                            self.setElementsCours(self._elements_cours)

                    if infosElement["typeElement"] not in ["Titre", "TexteLibre", "AutoEvaluation", "Examen", "BoiteDepot", "Forum", "SalleVirtuelle"]:
                        self.detacherElement(element["idElement"], infosElement["createurElement"], infosElement["typeElement"].replace(" ", ""))

                    if infosElement["typeElement"] == "BoiteDepot":
                        boite = getattr(self, element["idElement"])
                        boite.retirerTousElements()

                    if (infosElement["typeElement"] in ["Forum", "BoiteDepot"]) or (force_WIMS is True and infosElement["typeElement"] in ["AutoEvaluation", "Examen"]):
                        self.manage_delObjects([element["idElement"]])

            elif "listeElement" in element:
                # Si on tombe sur un titre, on vérifie alors qu'il ne contient pas idElement
                self.retirerElementPlan(idElement, element["listeElement"], force_WIMS)

        if start:
            self.plan = tuple(listeElement)
        return listeElement

    def purgerDepots(self):
        #self.plone_log("purgerDepots")
        for boite in self.objectValues("JalonBoiteDepot"):
            boite.purgerDepots()
        self.setProperties({"DateDerniereModif": DateTime()})

    def supprimerAnnonce(self, annonce):
        #self.plone_log("supprimerAnnonce")
        self.annonce.manage_delObjects([annonce])

    def verifType(self, typeElement):
        #self.plone_log("verifType")
        return typeElement.replace(" ", "")

    def test(self, condition, valeurVrai, valeurFaux):
        #self.plone_log("test")
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

    def jalon_quote(self, encode):
        #self.plone_log("jalon_quote")
        return jalon_utils.jalon_quote(encode)

    def jalon_unquote(self, decode):
        #self.plone_log("jalon_unquote")
        return jalon_utils.jalon_unquote(decode)

    #autoriserAffichageSousObjet : définit si l'affichage de l'objet 'idElement' est autorisé ou pas.
    # utile pour empecher l'affichage des activités vides par exemple
    def autoriserAffichageSousObjet(self, idElement, typeElement=None):
        #self.plone_log("autoriserAffichageSousObjet")
        ret = {"val": True, "reason": ""}
        if not typeElement:
            typeElement = self.getTypeSousObjet(idElement)
        if typeElement in ['AutoEvaluation', 'Examen']:
            # dans le cas d'une activité WIMS, on n'affiche l'objet que s'il contient des exercices.
            infosActivite = self.getSousObjet(idElement)
            ret = infosActivite.autoriser_Affichage()
        return ret

    def getPhotoTrombi(self, login):
        #self.plone_log("getPhotoTrombi")
        return jalon_utils.getPhotoTrombi(login)

    def retirerEspace(self, mot):
        #self.plone_log("retirerEspace")
        return jalon_utils.retirerEspace(mot)

    def getBaseAnnuaire(self):
        #self.plone_log("getBaseAnnuaire")
        return jalon_utils.getBaseAnnuaire()

    def getFicheAnnuaire(self, valeur, base=None):
        #self.plone_log("getFicheAnnuaire")
        return jalon_utils.getFicheAnnuaire(valeur, base)

    def inscrireMOOC(self, member):
        #self.plone_log("inscrireMOOC")
        if self.getLibre():
            inscriptionsLibres = list(self.getInscriptionsLibres())
            if not member in inscriptionsLibres:
                inscriptionsLibres.append(member)
                self.setProperties({"InscriptionsLibres": inscriptionsLibres,
                                    "DateDerniereModif":  DateTime()})

    def getParamMooc(self):
        #self.plone_log("getParamMooc")
        return urllib2.quote("".join(["?action=mooc&amp;idcours=", self.getId(), "&auteur=", self.Creator(), "&amp;came_from=", self.absolute_url()]))

    def getInfosConnexion(self):
        #self.plone_log("getInfosConnexion")
        return jalon_utils.getInfosConnexion()

    def isLDAP(self):
        #self.plone_log("isLDAP")
        return jalon_utils.isLDAP()

    def convertirDate(self, date):
        #self.plone_log("convertirDate")
        return jalon_utils.convertirDate(date)

    def majCours(self):
        #self.plone_log("majCours")
        if not getattr(self, "forum", None):
            commentaires_sociaux = BooleanField("commentaires_sociaux",
                                                required=True,
                                                accessor="getCommentaires_sociaux",
                                                searchable=False,
                                                default=False,
                                                widget=BooleanWidget(label=_(u"Commentaires sur Facebook"))
                                                )
            self.schema.addField(commentaires_sociaux)
            jaime_sociaux = BooleanField("jaime_sociaux",
                                         required=True,
                                         accessor="getJaime_sociaux",
                                         searchable=False,
                                         default=False,
                                         widget=BooleanWidget(label=_(u"J'aime sur Facebook"))
                                         )
            self.schema.addField(jaime_sociaux)
            self.invokeFactory(type_name='Ploneboard', id="forum")
            forum = getattr(self, "forum")
            forum.setTitle("Liste des forums du cours")
            username = self.getAuteurPrincipal()
            if not username:
                username = self.Creator()
            forum.manage_setLocalRoles(username, ["Owner"])
        return "fait"

    #fonction centrale dans l'automatisation de la mise en place de tag sur les ressources d'un serveur primo liées à des cours jalon
    def tagBU(self, action, ressource=None):
        #self.plone_log("tagBU")
        portal_jalon_properties = getToolByName(self, 'portal_jalon_properties')
        if portal_jalon_properties.getPropertiesMonEspace('activer_tags_catalogue_bu'):
            if not ressource:
                elem = dict(self.getElementCours())
                for cle_element in elem.keys():
                    prop_element = elem[cle_element]
                    if prop_element["typeElement"] == "Catalogue BU":
                        self.tagBU(action, cle_element)
            else:
                portal_primo = getToolByName(self, "portal_primo")
                nomAuteur = self.getAuteur()["nom"]
                listeTag = []
                listeTag = portal_primo.recupTagBU(ressource)
                try:
                    elemTag = action.split(None, 1)[1]
                except:
                    pass
                action = action.split(None, 1)[0]

                #suppression de tag si un de ses elements change
                if action in ["diplome", "nom"]:
                    for ancienTag in listeTag:
                        ancienTagSplit = ancienTag.split(None, 2)
                        if len(ancienTagSplit) == 2:
                            ancienTag = ancienTag.replace(" ", "%20")
                            if action == "diplome":
                                if nomAuteur == ancienTagSplit[0]:  # and ancienTagSplit[2] in titreCour:
                                    portal_primo.tagBU(ressource, ancienTag, "remove")
                            if action == "nom":
                                ancienNom = self.getInfosMembre(elemTag)["nom"]
                                if ancienNom == ancienTagSplit[0]:  # ancienTagSplit[2] in titreCour and
                                    portal_primo.tagBU(ressource, ancienTag, "remove")
                    action = "add"

                #recuperation des code diplome associé au cours
                for public in self.getInfosListeAcces():
                    COD_ETU = public[1]
                    if COD_ETU not in ["email", "perso"]:
                        tag = nomAuteur + "%20" + COD_ETU  # + "%20" + titreCour
                        tag = tag.replace("%20", " ")
                        if len(tag) > 34:
                            tag = tag[0:34]
                        tag = tag.replace(" ", "%20")

                        #si j'ajoute une nouvelle ressourceBU
                        if action in ["add", "remove"]:
                            portal_primo.tagBU(ressource, tag, action)

    #pour montrer les nouveaux éléments dans le cours
    def isNouveau(self, idElement, listeActualites=None):
        #self.plone_log("isNouveau")
        if listeActualites is None:
            #self.plone_log("***** Not listeActualites")
            listeActualites = self.getActualitesCours(True)["listeActu"]
        for actualite in listeActualites:
            if idElement["titreElement"] in actualite["titre"]:
                member = self.portal_membership.getAuthenticatedMember()
                if member.getId() == self.Creator():
                    if cmp(actualite["date"], member.getProperty('login_time', None)) > 0:
                        return True
                    return False
                elif cmp(actualite["date"], self.getLastLogin()) > 0:
                    return True
        return False

    #Pour passer l'information dans le portal_catalog et l'utiliser dans la liste de cours
    def getDateDerniereActu(self):
        #self.plone_log("getDateDerniereActu")
        try:
            return DateTime(self.getLastDateActu())
        except:
            return DateTime()

    def setDateDerniereActu(self, listeActualites=None):
        #self.plone_log("setDateDerniereActu")
        #self.plone_log("***** listeActualites : %s" % str(listeActualites))
        retour = self.created()
        paramDate = "dateActivation"
        if listeActualites is None:
            listeActualites = self.getActualitesCours(True)["listeActu"]
            paramDate = "date"
        for actualite in listeActualites:
            if cmp(actualite[paramDate], retour) > 0:
                retour = actualite[paramDate]
        self.dateDerniereActu = retour

    def insererConsultation(self, user, type_cons, id_cons):
        #self.plone_log("insererConsultation")
        if user.has_role("Personnel"):
            if self.isAuteur(username):
                public_cons = "Auteur"
            if username in self.coAuteurs:
                public_cons = "Co-auteur"
            if username in self.coLecteur:
                public_cons = "Lecteur"
        if user.has_role("EtudiantJalon") or user.has_role("Etudiant"):
            public_cons = "Etudiant"
        if user.has_role("Manager"):
            public_cons = "Manager"
        if user.has_role("Secretaire"):
            public_cons = "Secretaire"
        portal = self.portal_url.getPortalObject()
        portal.portal_jalon_bdd.insererConsultation(SESAME_ETU=user.getId(), ID_COURS=self.getId(), TYPE_CONS=type_cons, ID_CONS=id_cons, PUBLIC_CONS=public_cons)

    def getConsultation(self):
        #self.plone_log("getConsultation")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByCoursByDate(self.getId())

    def getConsultationByCoursByYearForGraph(self):
        #self.plone_log("getConsultationByCoursByYearForGraph")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByCoursByYearForGraph(self.getId())

    def getConsultationElementsByCours(self, elements_list, elements_dict):
        #self.plone_log("getConsultationElementsByCours")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationElementsByCours(self.getId(), elements_list=elements_list, elements_dict=elements_dict)

    def getConsultationByElementByCours(self, element_id):
        #self.plone_log("getConsultationByElementByCours")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByElementByCours(self.getId(), element_id)

    def getConsultationByElementByCoursByYearForGraph(self, element_id):
        #self.plone_log("getConsultationByElementByCoursByYearForGraph")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByElementByCoursByYearForGraph(self.getId(), element_id)

    def genererGraphIndicateurs(self, months_dict):
        #self.plone_log("genererGraphIndicateurs")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.genererGraphIndicateurs(months_dict)

    #Recupere la liste des fichiers d'un cours pouvant etre telecharges
    def getFichiersCours(self, page=None):
        #self.plone_log("getFichiersCours")
        #fixe le nb d'element voulu par page
        nbElem = 15  # doit etre identique a celui de nbPage
        elem = dict(self.getElementCours())
        retour = []
        i = 0
        #Pour la 1er page ou s'il n'y en a qu'une
        if page in [None, 1, '']:
            for cle_element in elem.keys():
                element = elem[cle_element]
                if self.isInPlan(cle_element):
                    if i < nbElem:
                        if element["typeElement"] in ["File", "Image"] and not "." in cle_element:
                            if self.isAfficherElement(element['affElement'], element['masquerElement'])['val'] == 1:
                                element.update({'taille': self.getTailleFichiers(cle_element, element['createurElement'])})
                                retour.append(element)
                                i = i + 1
        else:
            limitte = nbElem * int(page)
            limitteInf = nbElem * (int(page) - 1)
            for cle_element in elem.keys():
                element = elem[cle_element]
                #Pour les pages avant l'actuel
                if self.isInPlan(cle_element):
                    if i < limitteInf:
                        if element["typeElement"] in ["File", "Image"] and not "." in cle_element:
                            if self.isAfficherElement(element['affElement'], element['masquerElement'])['val'] == 1:
                                i = i + 1
                    #pour la page actuel
                    elif i >= limitteInf and i < limitte:
                        if element["typeElement"] in ["File", "Image"] and not "." in cle_element:
                            if self.isAfficherElement(element['affElement'], element['masquerElement'])['val'] == 1:
                                element.update({'taille': self.getTailleFichiers(cle_element, element['createurElement'])})
                                retour.append(element)
                                i = i + 1
        return retour

    #donne la taille d'un fichier
    def getTailleFichiers(self, idElement, createurElement):
        #self.plone_log("getTailleFichiers")
        portal = self.portal_url.getPortalObject()
        home = getattr(getattr(portal.Members, createurElement), "Fichiers", None)
        objid = idElement
        if "*-*" in idElement:
            objid = objid.replace("*-*", ".")
        try:
            objid = objid.replace(" ", "-")
        except:
            pass
        for obj in home.objectValues(["ATBlob", "ATDocument"]):
            if objid in obj.id:
                return obj.getObjSize()

    def nbPage(self):
        #self.plone_log("nbPage")
        nbPage = 0
        #fixe le nb d'element voulu par page
        nbElem = 15
        i = 0
        retour = []
        elem = dict(self.getElementCours())
        for cle_element in elem.keys():
            if self.isInPlan(cle_element):
                element = elem[cle_element]
                if i < nbElem:
                    if element["typeElement"] in ["File", "Image"] and not "." in cle_element:
                        if self.isAfficherElement(element['affElement'], element['masquerElement'])['val'] == 1:
                            i = i + 1
                #si on depasse le nombre d'element par page on ajoute une page
                else:
                    nbPage = nbPage + 1
                    retour.append(nbPage)
                    i = 0
                    if element["typeElement"] in ["File", "Image"] and not "." in cle_element:
                        if self.isAfficherElement(element['affElement'], element['masquerElement'])['val'] == 1:
                            i = 1
        if i > 0:
            nbPage = nbPage + 1
            retour.append(nbPage)
        return retour

    def telecharger(self, HTTP_USER_AGENT, fichiers):
        #self.plone_log("telecharger")
        import tempfile
        fd, path = tempfile.mkstemp('.zipfiletransport')
        close(fd)
        zipFile = ZipFile(path, 'w', ZIP_DEFLATED)
        portal = self.portal_url.getPortalObject()
        elems = dict(self.getElementCours())
        cours = self.supprimerCaractereSpeciaux(self.Title())
        dansArchive = []
        for cle_element in elems.keys():
            element = elems[cle_element]
            for fichier in fichiers:
                # on ne prend que les fichiers coché parmi tout les fichiers du cours
                if element["titreElement"] == fichier and cle_element not in dansArchive:
                    createurElement = element["createurElement"]
                    # on vas chercher le fichier dans l'espace du prof a qui il appartient
                    home = getattr(getattr(portal.Members, createurElement), "Fichiers", None)
                    #"ATBlob", "ATDocument" sont les 2 seuls qui fonctionnent
                    if "*-*" in cle_element:
                        cle_element = cle_element.replace("*-*", ".")
                    try:
                        objid = cle_element.replace(" ", "-")
                    except:
                        objid = cle_element
                    for obj in home.objectValues(["ATBlob", "ATDocument"]):
                        if objid in obj.id:
                            if len(fichiers) == 1 and fichiers[0] == element["titreElement"] and element["typeElement"] not in ["Image"]:
                                return {"situation": 1, "data": '%s/at_download/file' % obj.absolute_url()}
                            dansArchive.append(cle_element)
                            file_data = str(obj.data)
                            #nom du dossier/ nom du fichier dans le zip
                            filename_path = "%s/%s" % (cours, obj.id)
                            if 'Windows' in HTTP_USER_AGENT:
                                try:
                                    filename_path = filename_path.decode('utf-8').encode('cp437')
                                except:
                                    pass
                            zipFile.writestr(filename_path, file_data)
                            pass
        zipFile.close()
        fp = open(path, 'rb')
        data = fp.read()
        fp.close()
        return {"length": str(os.stat(path)[6]), "data": data, "situation": 3}

    def hasParticipants(self):
        formations = self.getAffichageFormations()
        if formations:
            return True
        nomminatives = self.getInfosGroupe()
        if nomminatives:
            return True
        invitations = self.getInfosInvitations()
        if invitations:
            return True
        lecteurs = self.getCoLecteurs()
        if lecteurs:
            return True
        return False

    def telechargerListingParticipants(self):
        import tempfile
        from os import close
        from xlwt import Workbook, Style, Pattern, XFStyle

        portal_membership = getToolByName(self, "portal_membership")
        authMember = portal_membership.getAuthenticatedMember()

        fd, path = tempfile.mkstemp('.%s-xlfiletransport' % authMember.getId())
        close(fd)

        # Définition du style des entêtes
        styleEnTete = XFStyle()
        patternEnTete = Pattern()
        patternEnTete.pattern = Pattern.SOLID_PATTERN
        patternEnTete.pattern_fore_colour = Style.colour_map["black"]
        styleEnTete.pattern = patternEnTete
        styleEnTete.font.colour_index = Style.colour_map["white"]

        # création du Workbook
        listing = Workbook(encoding="utf-8")

        # ajout des étudiants de l'offre de formations
        bdd = getToolByName(self, "portal_jalon_bdd")
        dicoAffFormation = {"etape":  "Diplôme",
                            "ue":     "Unité d'enseignement",
                            "uel":    "Unité d'enseignement libre",
                            "groupe": "Groupe"}
        formations = self.getAffichageFormations()
        for formation in formations:
            # création d'une feuille de formation
            feuille = listing.add_sheet("Formation%s" % formation[1])

            #Première Ligne : Titre de la formation ; Type ; Code
            feuille.write(0, 0, "Liste des participants du cours :")
            feuille.write(0, 1, self.Title())
            feuille.write(1, 0, dicoAffFormation[formation[-1]])
            feuille.write(1, 1, formation[0])
            feuille.write(1, 2, "(%s)" % formation[1])

            # ajout des en-têtes
            feuille.write(3, 0, 'Nom', styleEnTete)
            feuille.write(3, 1, 'Prénom', styleEnTete)
            feuille.write(3, 2, 'Sésame', styleEnTete)
            feuille.write(3, 3, 'Numéro', styleEnTete)
            feuille.write(3, 4, 'Courriel', styleEnTete)

            listeEtudiants = bdd.rechercherEtudiantXLS(formation[1])
            i = 4
            for etudiant in listeEtudiants:
                ligne = feuille.row(i)
                ligne.write(0, etudiant["LIB_NOM_PAT_IND"])
                ligne.write(1, etudiant["LIB_PR1_IND"])
                ligne.write(2, etudiant["SESAME_ETU"])
                ligne.write(3, etudiant["COD_ETU"])
                ligne.write(4, etudiant["EMAIL_ETU"])
                i = i + 1

            # ajustement de la largeur d'une colonne
            feuille.col(4).width = 8000

        # Ajout des inscriptions nomminatives
        nomminatives = self.getInfosGroupe()
        if nomminatives:
            # Création de la feuille des inscriptiosn nomminatives
            feuille = listing.add_sheet("InscriptionsNomminatives")

            # Première Ligne : Titre de la formation ; Type ; Code
            feuille.write(0, 0, "Liste des participants du cours :")
            feuille.write(0, 1, self.Title())
            feuille.write(1, 0, "Inscription(s) nomminative(s)")

            # ajout des en-têtes
            feuille.write(3, 0, 'Nom', styleEnTete)
            feuille.write(3, 1, 'Prénom', styleEnTete)
            feuille.write(3, 2, 'Sésame', styleEnTete)
            feuille.write(3, 3, 'Numéro', styleEnTete)
            feuille.write(3, 4, 'Courriel', styleEnTete)

            listeEtudiants = nomminatives
            i = 4
            for etudiant in listeEtudiants:
                ligne = feuille.row(i)
                ligne.write(0, etudiant["nom"])
                ligne.write(1, etudiant["prenom"])
                ligne.write(2, etudiant["sesame"])
                ligne.write(3, etudiant["num_etu"])
                ligne.write(4, etudiant["email"])
                i = i + 1

            # ajustement de la largeur d'une colonne
            feuille.col(4).width = 8000

        # Ajout des invitations par courriel
        invitations = self.getInfosInvitations()
        if invitations:
            # Création de la feuille des inscriptiosn nomminatives
            feuille = listing.add_sheet("InvitationsCourriel")

            # Première Ligne : Titre de la formation ; Type ; Code
            feuille.write(0, 0, "Liste des participants du cours :")
            feuille.write(0, 1, self.Title())
            feuille.write(1, 0, "Invitations(s) par courriel(s)")

            # ajout des en-têtes
            feuille.write(3, 0, 'Nom', styleEnTete)
            feuille.write(3, 1, 'Prénom', styleEnTete)
            feuille.write(3, 2, 'Sésame', styleEnTete)
            feuille.write(3, 3, 'Numéro', styleEnTete)
            feuille.write(3, 4, 'Courriel', styleEnTete)

            listeEtudiants = invitations
            i = 4
            for etudiant in listeEtudiants:
                ligne = feuille.row(i)
                try:
                    nom, prenom = etudiant["nom"].split(" ")
                except:
                    nom = prenom = etudiant["nom"]
                ligne.write(0, nom)
                ligne.write(1, prenom)
                ligne.write(2, etudiant["email"])
                ligne.write(3, "Non défini")
                ligne.write(4, etudiant["email"])
                i = i + 1

            # ajustement de la largeur d'une colonne
            feuille.col(2).width = 8000
            feuille.col(4).width = 8000

        # Ajout des lecteurs enseignants
        lecteurs = self.getCoLecteurs()
        if lecteurs:
            # Création de la feuille des lecteurs enseignants
            feuille = listing.add_sheet("LecteursEnseignants")

            # Première Ligne : Titre de la formation ; Type ; Code
            feuille.write(0, 0, "Liste des participants du cours :")
            feuille.write(0, 1, self.Title())
            feuille.write(1, 0, "Lecteur(s) enseignant(s)")

            # Ajout des en-têtes
            feuille.write(3, 0, 'Nom', styleEnTete)
            feuille.write(3, 1, 'Prénom', styleEnTete)
            feuille.write(3, 2, 'Sésame', styleEnTete)
            feuille.write(3, 3, 'Numéro', styleEnTete)
            feuille.write(3, 4, 'Courriel', styleEnTete)

            listeEtudiants = jalon_utils.getIndividus(list(lecteurs), "listdict")
            i = 4
            for etudiant in listeEtudiants:
                ligne = feuille.row(i)
                ligne.write(0, etudiant["nom"])
                ligne.write(1, etudiant["prenom"])
                ligne.write(2, etudiant["sesame"])
                ligne.write(3, "Non défini")
                ligne.write(4, etudiant["email"])
                i = i + 1

            # ajustement de la largeur d'une colonne
            feuille.col(4).width = 8000

        listing.save(path)

        fp = open(path, 'rb')
        data = fp.read()
        fp.close()
        return {"length": str(os.stat(path)[6]), "data": data}

    def supprimerCaractereSpeciaux(self, chaine):
        return jalon_utils.supprimerCaractereSpeciaux(chaine)

    def getSessionConnect(self, user_id, repertoire):
        #self.plone_log("getSessionConnect")
        portal = self.portal_url.getPortalObject()
        home = getattr(getattr(portal.Members, user_id), repertoire)
        return home.getSessionConnect(user_id)

    def getReunion(self, user_id, request, repertoire):
        #self.plone_log("getReunion")
        portal = self.portal_url.getPortalObject()
        home = getattr(getattr(portal.Members, user_id), repertoire)
        return home.getReunion(user_id)

    def getShortText(self, text, limit=75):
        #self.plone_log("getShortText")
        return jalon_utils.getShortText(text, limit)

    def getJalonMenu(self, portal_url, user, request):
        return jalon_utils.getJalonMenu(self, portal_url, user, request)

    #Suppression marquage HTML
    def supprimerMarquageHTML(self, chaine):
        return jalon_utils.supprimerMarquageHTML(chaine)

    def delElem(self, element):
        #self.plone_log("delElem")
        del self._elements_cours[element]
        self.getElementCours()
        self.setElementsCours(self._elements_cours)


# enregistrement dans la registery Archetype
registerATCT(JalonCours, PROJECTNAME)
