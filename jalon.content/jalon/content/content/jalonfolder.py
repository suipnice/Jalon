# -*- coding: utf-8 -*-
""" Jalon Folder."""
from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.folder import ATFolder, ATFolderSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonFolder
from jalon.content.browser.config.jalonconfig import IJalonConfigControlPanel
#from jalon.content.browser.config.jalonconfiguration import IJalonConfigurationControlPanel

from Acquisition import aq_inner
from DateTime import DateTime

import locale
import json
import urllib
import urllib2
import random
import jalon_utils
import string
import jalonressourceexterne
import cStringIO
import os
import copy

from logging import getLogger
LOG = getLogger('[JalonFolder]')
"""
# Log examples :
LOG.debug('debug message')
LOG.info('info message')
LOG.warn('warn message')
LOG.error('error message')
LOG.critical('critical message')
"""

JalonFolderSchema = ATFolderSchema.copy() + atpublic.Schema((
    atpublic.StringField("password",
                         required=False,
                         accessor="getPassword",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Mot de passe"),
                                                      description=_(u"Le mot de passe du dossier"),)
                         ),
    atpublic.StringField("complement",
                         required=False,
                         accessor="getComplement",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Complement propre a chaque dossier"),
                                                      description=_(u"Le complement du dossier"),)
                         ),
))

listeSubJalonFolder = [["Fichiers", "Fichiers"],
                       ["Sonorisation", u"Présentations sonorisées".encode("utf-8")],
                       ["Wims", "Exercices Wims"],
                       ["Externes", "Liens"],
                       ["Glossaire", "Termes de glossaire"],
                       ["Webconference", u"Webconférences".encode("utf-8")],
                       ["CatalogueBU", "Catalogue BU"],
                       ["Video", "Vidéos"]]

SIZE_CONST = {'KB': 1024, 'MB': 1024 * 1024, 'GB': 1024 * 1024 * 1024}


def addSubJalonFolder(obj, event):
    for subfolder in listeSubJalonFolder:
        obj.invokeFactory(type_name='JalonFolder', id=subfolder[0])
        rep = getattr(obj, subfolder[0])
        rep.setDefaultPage("jalonfolder_view")
        rep.setTitle(subfolder[1])
        rep.setPortlets()
        rep.reindexObject()


class JalonFolder(ATFolder):
    """ Un dossier Jalon. """

    implements(IJalonFolder)
    meta_type = 'JalonFolder'
    schema = JalonFolderSchema

    def __init__(self, *args, **kwargs):
        super(JalonFolder, self).__init__(*args, **kwargs)
        self.uploader_id = self._uploader_id()

    def addSubJalonFolder(self, memberid):
        addSubJalonFolder(self, memberid)

    def setPortlets(self):
        manager = getUtility(IPortletManager, name=u"plone.leftcolumn")
        blacklist = getMultiAdapter((self, manager), ILocalPortletAssignmentManager)
        blacklist.setBlacklistStatus("context", True)
        self.reindexObject()

    def getItemSize(self, item_size):
        """ Convert "Human friendly" file size into original size, in bytes."""
        display_size = item_size.split(" ")
        # if the size is a float, then make it an int
        # happens for large files
        try:
            size = float(display_size[0])
        except (ValueError, TypeError):
            size = 0
        units = display_size[-1]
        if units in SIZE_CONST:
            size = size * SIZE_CONST[units]
        return size

    def getContents(self, subject, typeR, authMember, repertoire, categorie=None):
        """Founi la liste des elements d'un jalonfolder."""
        dico = {"portal_type": typeR}
        if typeR == "Fichiers":
            dico["portal_type"] = ["File", "Image", "Document"]

        idreunion = None
        if "-" in repertoire:
            repertoire, idreunion = repertoire.split("-")
        if repertoire in ["Webconference", "Sonorisation"] and subject in ["", None, "last"]:
            self.getContentsConnect(authMember, idreunion, dico)

        if typeR == "JalonExerciceWims" and subject in ["", None, "last"]:
            self.getContentsWims(authMember)

        if self.getId() == "Video":
            maj_video = True if subject == "last" else False
            self.getContentsVideo(authMember, maj_video)

        if subject not in ["", None, "last"]:
            last = False
            subjects = []
            tags = subject.split(',')
            if "last" in tags:
                tags.remove("last")
                last = True
            for tag in tags:
                subjects.append(urllib.quote(tag))
            if len(subjects) > 1:
                dico['Subject'] = {'query': subjects, 'operator': 'and'}
            else:
                dico['Subject'] = subjects[0]
            if last:
                dico["sort_on"] = "modified"
                dico["sort_order"] = "descending"
                return self.getFolderContents(contentFilter=dico, batch=True, b_size=20)
            else:
                return self.getFolderContents(contentFilter=dico)
        elif subject == "last":
            dico["sort_on"] = "modified"
            dico["sort_order"] = "descending"
            return self.getFolderContents(contentFilter=dico, batch=True, b_size=20)
        else:
            dico["sort_on"] = "modified"
            dico["sort_order"] = "descending"
            return self.getFolderContents(contentFilter=dico)

    def getContentsConnect(self, authMember, idreunion, dico):
        if not idreunion:
            idreunion = self.getReunion(authMember, None)["idreunion"]
        enregistrements_connect = self.connect('rechercherEnregistrements', {'id': idreunion})
        #setConnect = set([o["id"] for o in enregistrements_connect])
        #enregistrements_jalon = self.getFolderContents(contentFilter=dico)
        reindex = False
        listeIdJalon = self.objectIds()
        #listeIdJalon = [o.getId for o in enregistrements_jalon]
        for enregistrement in enregistrements_connect:
            if not enregistrement["id"] in listeIdJalon:
                idobj = self.invokeFactory(type_name='JalonConnect', id=enregistrement["id"])
                obj = getattr(self, idobj)
                obj.setProperties({"Title":     enregistrement["title"],
                                   "DateAjout": str(enregistrement["created"]),
                                   "DateUS":    enregistrement["dateUS"],
                                   "Duree":     enregistrement["duration"],
                                   "UrlEnr":    enregistrement["url"]})
                obj.reindexObject()
                reindex = True
        if reindex:
            self.reindexObject()
        #return self.getFolderContents(contentFilter=dico)

    def getContentsWims(self, authMember):
        classe = self.getComplement()
        if not classe:
            #1er  cas : Aucune classe n'existe pour cet utilisateur

            #member = self.portal_membership.getMemberById(authMember)
            member = self.getInfosMembre(authMember)
            auth_email = member["email"]
            fullname = member["fullname"]
            #if not fullname:
            #    fullname = member.getProperty("displayName")
            #if not auth_email:
            #    auth_email = str(member.getProperty("mail"))
            groupement = self.wims("creerClasse", {"authMember": authMember, "fullname": fullname, "auth_email": auth_email, "type": "2", "qclass": ""})
            if groupement["status"] == "OK":
                idClasse = self.wims("creerClasse", {"authMember": authMember, "fullname": fullname, "auth_email": auth_email, "type": "0", "titre_classe": "Mes exercices", "qclass": groupement["class_id"]})
                if idClasse:
                    self.complement = str(groupement["class_id"])
                    return []
            else:
                #print "*****    Mauvais parametrage de votre connexion WIMS  *****"
                #print "[jalonfolder.py/getContents] Creation du groupement impossible"
                #print " Reponse WIMS : %s" % groupement
                #print "*****                                                 *****"
                return {"erreur": "wims_bad_conf"}
        else:
            #2e  cas : l'utilisateur courant dispose deja d'une classe. on liste ses exercices.
            #print "Classe %s" % self.getComplement()
            #exercices={}
            #try:
            exercices = self.wims("getExercicesWims",
                                  {"authMember": authMember,
                                   "qclass": "%s_1" % self.getComplement(),
                                   "jalon_URL": self.absolute_url()
                                   })
            if exercices["status"] == "ERROR":
                #en cas d'indisponibilite, le code retour de WIMS donne un type "HTTPError"
                if "type" in exercices:
                    return {"erreur": "wims_unavailable"}
                else:
                    return {"erreur": "wims_bad_conf"}
            #except:
            #   mail_body = "*****    WIMS indisponible ou Mauvais parametrage de La connexion WIMS  *****\n"
            #   mail_body += "[jalonfolder.py/getContents] getExercicesWims\n"
            #   mail_body += "#2e  cas : l'utilisateur courant dispose deja d'une classe. on liste ses exercices.\n\n"
            #   mail_body += " authMember : %s \n" % authMember
            #   mail_body += " qclass : %s_1 \n" % self.getComplement()
            #   mail_body += "*****                                                                   *****\n"
            #   print mail_body
            #   mail_erreur["message"] = mail_body
            #   self.envoyerMailErreur(mail_erreur)
            #   Si getExercicesWIMS plante, c'est :
            #   soit une mauvaise configuration de WIMS  par l'admin (elle a du etre changee entre temps, puisqu'il dispose d'une classe ici)
            #   soit que wims est actuellement indisponible. (cas un peu plus probable que le 1er)
            #   return {"erreur" : "wims_unavailable" }

            exercices_jalon = self.objectIds()
            if "exocount" in exercices:
                if exercices["exocount"] == 0:
                    exercices_wims = []
                else:
                    exercices_wims = exercices["exotitlelist"]
                if len(exercices_jalon) < len(exercices_wims):
                    liste_modeles = self.getListeModelesWims()
                    #On recupere les exos de wims pour les créer sur jalon
                    for exo_wims in exercices_wims:
                        exo_ok = False
                        for exo_jalon in exercices_jalon:
                            if exo_wims["id"] == exo_jalon:
                                exo_ok = True
                        if not exo_ok:
                            modele = exo_wims["id"].split("-")[0]
                            if modele not in liste_modeles:
                                modele = "exercicelibre"
                            #CREATION de l'exercice %s sur Jalon " % exo_wims["id"]
                            idobj = self.invokeFactory(type_name='JalonExerciceWims', id=exo_wims["id"])
                            obj = getattr(self, idobj)
                            obj.setProperties({"Title": exo_wims["title"],
                                               "Modele": modele})
            else:
                #*****serveur WIMS indisponible ou mauvaise configuration de l'acces WIMS"
                # Si WIMS est indisponible, on ignore simplement sa liste d'exercices et on affiche celle de Jalon uniquement.
                #print "*****    Mauvais parametrage de votre connexion WIMS  *****"
                #print "[jalonfolder.py] getExercicesWims : %s" % exercices
                #print "*****                                                *****"
                return "wims_unavailable"

    def getContentsVideo(self, member_id, maj_video):
        if maj_video:
            jalon_videos_id = set([object_id.split("-")[-1] for object_id in self.objectIds()])
            response_elasticsearch = self.searchElasticsearch("mes_videos", "", 1)
            nb_pages = response_elasticsearch["nb_pages"]
            if nb_pages:
                dico_videos_pod = {}
                videos_ids = []
                for video in response_elasticsearch["liste_videos"]:
                    videos_ids.append(video["id"])
                    dico_videos_pod[video["id"]] = video

                if nb_pages > 1:
                    for page in range(2, nb_pages):
                        response_elasticsearch = self.searchElasticsearch("mes_videos", "", page)
                        for video in response_elasticsearch["liste_videos"]:
                            videos_ids.append(video["id"])
                            dico_videos_pod[video["id"]] = video

                videos_ids = set(videos_ids)
                #videos_del = jalon_videos_id.difference(videos_ids)

                videos_add = videos_ids.difference(jalon_videos_id)
                for video_id in videos_add:
                    video = dico_videos_pod[video_id]
                    idobj = "Externe-%s-%s" % (member_id, video_id)
                    obj = getattr(self, idobj, None)
                    if not obj:
                        self.invokeFactory(type_name='JalonRessourceExterne', id=idobj)
                        obj = getattr(self, idobj)
                        video = self.searchElasticsearch(type_search="video", term_search=video_id)
                        LOG.info(video)
                        param = {"Title":                video["title"],
                                 "TypeRessourceExterne": "Video",
                                 "Videourl":             video["full_url"],
                                 "Description":          video["text"],
                                 "Lecteur":              video["iframe"],
                                 "Videoauteur":          video["owner"],
                                 "Videoauteurname":      video["owner_full_name"],
                                 "Videothumbnail":       video["thumbnail"]}
                        obj.setProperties(param)
            elif jalon_videos_id:
                #Supprimer toutes les vidéos
                pass

    def DEBUG(self):
        a = set([1, 2, 3, 4])
        b = set([3, 4, 5, 6])

        c = a.difference(b)
        return c

    def getListeCoursEns(self, subject, authMember):
        """ Renvoi la liste des cours pour authMember."""

        listeCours = []
        listeCoursId = []
        listeTousCours = []
        authMemberId = authMember.getId()
        portal_catalog = getToolByName(self, "portal_catalog")
        filtre = {"portal_type": "JalonCours"}
        if subject == "favori":
            filtre["Subject"] = authMemberId
            listeTousCours = list(portal_catalog.searchResults(portal_type="JalonCours", getAuteurPrincipal=authMemberId, Subject=authMemberId))
            listeTousCours.extend(list(portal_catalog.searchResults(portal_type="JalonCours", getCoAuteurs=authMemberId, Subject=authMemberId)))
            listeTousCours.extend(list(portal_catalog.searchResults(portal_type="JalonCours", getCoLecteurs=authMemberId, Subject=authMemberId)))
        else:
            listeTousCours = list(portal_catalog.searchResults(portal_type="JalonCours", getAuteurPrincipal=authMemberId))
            listeTousCours.extend(list(portal_catalog.searchResults(portal_type="JalonCours", getCoAuteurs=authMemberId)))
            listeTousCours.extend(list(portal_catalog.searchResults(portal_type="JalonCours", getCoLecteurs=authMemberId)))
        listeTousCours.extend(list(self.getFolderContents(contentFilter=filtre)))

        dicoAuteur = {}
        for cours in listeTousCours:
            if not cours.getId in listeCoursId:
                if authMemberId in cours.Subject:
                    favori = {"val": "Oui", "icon": "fa-star"}
                else:
                    favori = {"val": "Non", "icon": "fa-star-o"}
                auteur_cours = cours.getAuteurPrincipal
                if not auteur_cours:
                    auteur_cours = cours.Creator
                if auteur_cours in dicoAuteur:
                    name_auteur_cours = dicoAuteur[auteur_cours]
                else:
                    name_auteur_cours = self.getInfosMembre(auteur_cours)["fullname"]
                    dicoAuteur[auteur_cours] = name_auteur_cours
                role = {"is_creator": True, "is_auteur": False, "is_co_auteur": False, "is_lecteur": False, "affichage": "Auteur"}
                roles = cours.getRoleCat
                if authMemberId in roles["auteur"]:
                    role = {"is_creator": True, "is_auteur": True, "is_co_auteur": False, "is_lecteur": False, "affichage": "Auteur"}
                if authMemberId in roles["coauteur"]:
                    role = {"is_creator": False, "is_auteur": False, "is_co_auteur": True, "is_lecteur": False, "affichage": "Co-auteur"}
                if authMemberId in roles["colecteur"]:
                    role = {"is_creator": False, "is_auteur": False, "is_co_auteur": False, "is_lecteur": True, "affichage": "Lecteur"}
                listeCours.append({"id": cours.getId,
                                   "title": cours.Title,
                                   "short_title": self.getShortText(cours.Title),
                                   #"description": cours.Description,
                                   "short_description": self.getPlainShortText(cours.Description, 210),
                                   "auteur_cours": auteur_cours,
                                   "name_auteur_cours": name_auteur_cours,
                                   "is_creator": role["is_creator"],
                                   "is_auteur": role["is_auteur"],
                                   "is_co_auteur": role["is_co_auteur"],
                                   "is_lecteur": role["is_lecteur"],
                                   "role_affichage": role["affichage"],
                                   "is_nouveau": cmp(cours.getDateDerniereActu, authMember.getProperty('login_time', None)) > 0,
                                   "modified": cours.modified,
                                   "is_favori": favori["val"],
                                   "favori_icon": favori["icon"],
                                   "url_cours": cours.getURL,
                                   "is_etudiants": len(cours.getRechercheAcces) > 0,
                                   "is_password": cours.getLibre,
                                   "is_public": cours.getAcces == 'Public'})
                listeCoursId.append(cours.getId)
        return list(listeCours)

    def getInfosApogee(self, code, type):
        portal = self.portal_url.getPortalObject()
        bdd = getToolByName(portal, "portal_jalon_bdd")
        if type == "etape":
            retour = self.encodeUTF8(bdd.getInfosEtape(code))
            if not retour:
                return ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
            return list(retour)
        if type in ["ue", "uel"]:
            retour = self.encodeUTF8(bdd.getInfosELP2(code))
            if not retour:
                return ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
            return list(retour)
        if type == "groupe":
            retour = self.encodeUTF8(bdd.getInfosGPE(code))
            if not retour:
                return ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
            return list(retour)

    # getInfosMembre recupere les infos sur les personnes.
    def getInfosMembre(self, username):
        #self.plone_log("getInfosMembre")
        return jalon_utils.getInfosMembre(username)

    #[DEPRECATED]
    #getDisplayName() permet d'obtenir le nom (+prenom) d'un utilisateur
    #def getDisplayName(self, user_id, request=None, portal=None):
    #    return jalon_utils.getDisplayName(user_id, request, portal)

    def getPropertiesMessages(self, key=None):
        jalon_properties = self.portal_jalon_properties
        return jalon_properties.getPropertiesMessages(key)

    def getCours(self, categorie="1", authMember=None):
        if authMember.has_role("EtudiantJalon"):
            return self.getCoursEtudiantJalon(categorie, authMember.getId())
        else:
            return self.getCoursEtudiant(categorie, authMember.getId())

    def getCoursEtudiant(self, categorie="1", idMember=None):
        listeDiplome = []
        dicoAuteur = {}
        portal = self.portal_url.getPortalObject()
        portal_catalog = getToolByName(portal, "portal_catalog")
        portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")
        portal_membership = getToolByName(portal, "portal_membership")

        authMember = None
        if idMember:
            authMember = portal_membership.getMemberById(idMember)
        if not authMember:
            authMember = portal_membership.getAuthenticatedMember()

        diplomes = []
        COD_ETU = authMember.getId()
        for diplome in portal_jalon_bdd.getInscriptionIND(COD_ETU, "etape"):
            diplomes.append(diplome["COD_ELP"])

        if categorie == "1":
            dicoUE = {}
            #groupes = portal_jalon_bdd.getGroupesEtudiant(COD_ETU)
            #pour les nouveaux étudiant qui n'ont pas encore de diplome
            if not diplomes:
                listeCours = []
                liste = list(portal_catalog.searchResults(portal_type="JalonCours", getRechercheAcces=authMember.getId()))
                for cours in liste:
                    auteur = cours.getAuteurPrincipal
                    if not auteur:
                        auteur = cours.Creator
                    if not auteur in dicoAuteur:
                        dicoAuteur[auteur] = {"nom": auteur, "email": ""}
                        infosMembre = self.getInfosMembre(auteur)
                        dicoAuteur[auteur]["nom"] = infosMembre["fullname"]
                        dicoAuteur[auteur]["email"] = infosMembre["email"]
                    listeCours.append({"id":     cours.getId,
                                       "title":  cours.Title,
                                       "description":  cours.Description,
                                       "auteur": dicoAuteur[auteur]["nom"],
                                       "createur": cours.Creator,
                                       "idauteur": auteur,
                                       "email":  dicoAuteur[auteur]["email"],
                                       "url":    "%s" % cours.getURL(),
                                       "modified":  cours.modified,
                                       "acces":  ["Invité"]})
                listeDiplome.append({"libelle": "Mes cours", "listeCours": listeCours})
                return listeDiplome
            for COD_ELP in diplomes:
                listeUE = []
                etape = portal_jalon_bdd.getVersionEtape(COD_ELP)
                if etape:
                    dicoUE["etape*-*%s" % COD_ELP] = {"type": "etape", "libelle": etape[0]}
                    listeUE.append("etape*-*%s" % COD_ELP)

                    inscription_pedago = portal_jalon_bdd.getInscriptionPedago(COD_ETU, COD_ELP)
                    if not inscription_pedago:
                        inscription_pedago = portal_jalon_bdd.getUeEtape(COD_ELP)
                    for inscription in inscription_pedago:
                        ELP = "*-*".join([inscription["TYP_ELP"], inscription["COD_ELP"]])
                        if not ELP in dicoUE:
                            dicoUE[ELP] = {"type": inscription["TYP_ELP"], "libelle": inscription["LIB_ELP"]}
                            listeUE.append(ELP)

                    listeUE.append(authMember.getId())
                    query = {'query': listeUE, 'operator': 'or'}
                    listeCours = []
                    liste = list(portal_catalog.searchResults(portal_type="JalonCours", getRechercheAcces=query))
                    for cours in liste:
                        listeAcces = []
                        auteur = cours.getAuteurPrincipal
                        if not auteur:
                            auteur = cours.Creator
                        if not auteur in dicoAuteur:
                            dicoAuteur[auteur] = {"nom": auteur, "email": ""}
                            infosMembre = self.getInfosMembre(auteur)
                            dicoAuteur[auteur]["nom"] = infosMembre["fullname"]
                            dicoAuteur[auteur]["email"] = infosMembre["email"]

                        for acces in cours.getListeAcces:
                            if acces in dicoUE:
                                listeAcces.append("%s : %s" % (dicoUE[acces]['type'], dicoUE[acces]['libelle']))
                        if authMember.getId() in cours.getGroupe:
                            listeAcces.append("Invité")
                        try:
                            if authMember.getId() in cours.getInscriptionsLibres:
                                listeAcces.append("Inscription par mot de passe")
                        except:
                            pass
                        listeCours.append({"id":     cours.getId,
                                           "title":  cours.Title,
                                           "description":  cours.Description,
                                           "auteur": dicoAuteur[auteur]["nom"],
                                           "createur": cours.Creator,
                                           "idauteur": auteur,
                                           "email":  dicoAuteur[auteur]["email"],
                                           "url":    cours.getURL(),
                                           "modified":  cours.modified,
                                           "acces":  listeAcces})
                    listeDiplome.append({"libelle":  etape[0], "listeCours": listeCours})
        else:
            listeCours = []
            liste = list(portal_catalog.searchResults(portal_type="JalonCours", getCategorieCours=categorie))
            for cours in liste:
                auteur = cours.getAuteurPrincipal
                if not auteur:
                    auteur = cours.Creator
                if not auteur in dicoAuteur:
                    dicoAuteur[auteur] = {"nom": auteur, "email": ""}
                    infosMembre = self.getInfosMembre(auteur)
                    dicoAuteur[auteur]["nom"] = infosMembre["fullname"]
                    dicoAuteur[auteur]["email"] = infosMembre["email"]
                listeCours.append({"id":       cours.getId,
                                   "title":    cours.Title,
                                   "description":  cours.Description,
                                   "auteur":   dicoAuteur[auteur]["nom"],
                                   "createur": cours.Creator,
                                   "email":    dicoAuteur[auteur]["email"],
                                   "idauteur": auteur,
                                   "modified":  cours.modified,
                                   "url":      "%s" % cours.getURL()})
            listeDiplome.append({"listeCours": listeCours})
        return listeDiplome

    def getCoursEtudiantJalon(self, categorie="1", idMember=None):
        portal = self.portal_url.getPortalObject()
        portal_catalog = getToolByName(portal, "portal_catalog")
        portal_membership = getToolByName(portal, "portal_membership")

        dicoAuteur = {}
        if idMember:
            authMember = portal_membership.getMemberById(idMember)
        else:
            authMember = portal_membership.getAuthenticatedMember()

        dicoAuteur = {}
        listeCours = []
        listeDiplome = []
        if categorie == "1":
            liste = list(portal_catalog.searchResults(portal_type="JalonCours", getRechercheAcces=authMember.getId()))
            for cours in liste:
                auteur = cours.getAuteurPrincipal
                if not auteur:
                    auteur = cours.Creator
                if not auteur in dicoAuteur:
                    dicoAuteur[auteur] = {"nom": auteur, "email": ""}
                    infosMembre = self.getInfosMembre(auteur)
                    dicoAuteur[auteur]["nom"] = infosMembre["fullname"]
                    dicoAuteur[auteur]["email"] = infosMembre["email"]
                listeCours.append({"id"          : cours.getId,
                                   "title"       : cours.Title,
                                   "description" : cours.Description,
                                   "auteur"      : dicoAuteur[auteur]["nom"],
                                   "idauteur"    : auteur,
                                   "createur"    : cours.Creator,
                                   "email"       : dicoAuteur[auteur]["email"],
                                   "url"         : "%s" % cours.getURL(),
                                   "modified"    : cours.modified,
                                   "acces"       : ["Invité"]})
            listeDiplome.append({"libelle": "Mes cours", "listeCours": listeCours})
        else:
            listeCours = []
            liste = list(portal_catalog.searchResults(portal_type="JalonCours", getCategorieCours=categorie))
            for cours in liste:
                auteur = cours.getAuteurPrincipal
                if not auteur:
                    auteur = cours.Creator
                if not auteur in dicoAuteur:
                    dicoAuteur[auteur] = {"nom": auteur, "email": ""}
                    infosMembre = self.getInfosMembre(auteur)
                    dicoAuteur[auteur]["nom"] = infosMembre["fullname"]
                    dicoAuteur[auteur]["email"] = infosMembre["email"]
                listeCours.append({"id"          : cours.getId,
                                   "title"       : cours.Title,
                                   "description" :  cours.Description,
                                   "auteur"      : dicoAuteur[auteur]["nom"],
                                   "idauteur"    : auteur,
                                   "createur"    : cours.Creator,
                                   "email"       : dicoAuteur[auteur]["email"],
                                   "idauteur"    : auteur,
                                   "url"         : "%s" % cours.getURL(),
                                   "modified"    : cours.modified,})
            listeCours.sort(lambda x,y: cmp(x["auteur"], y["auteur"]))
            listeDiplome.append({"listeCours": listeCours})
        return listeDiplome

    def getClefsDico(self, dico):
        return jalon_utils.getClefsDico(dico)

    def getJalonCategories(self):
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return dict(jalon_properties.getCategorie())

    def getListeCours(self, authMember):
        portal = self.portal_url.getPortalObject()
        portal_catalog = getToolByName(portal, "portal_catalog")
        listeCours = list(portal_catalog.searchResults(portal_type="JalonCours", Creator=authMember))
        listeCoursAuteur = list(portal_catalog.searchResults(portal_type="JalonCours", getAuteurPrincipal=authMember))
        if listeCoursAuteur:
            listeCours.extend(listeCoursAuteur)
        listeCoursCoAuteur = list(portal_catalog.searchResults(portal_type="JalonCours", getCoAuteurs=authMember))
        if listeCoursCoAuteur:
            listeCours.extend(listeCoursCoAuteur)

        dicoAccess = {}
        bdd = getToolByName(portal, "portal_jalon_bdd")
        for cours in listeCours:
            for acces in cours.getListeAcces:
                type, code = acces.split("*-*")
                if not code in dicoAccess:
                    if type == "etape":
                        retour = bdd.getInfosEtape(code)
                        if not retour:
                            elem = ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
                        else:
                            elem = list(retour)
                    if type in ["ue", "uel"]:
                        retour = bdd.getInfosELP2(code)
                        if not retour:
                            elem = ["Le code %s n'est plus valide pour cette UE / UEL." % code, code, "0"]
                        else:
                            elem = list(retour)
                    if type == "groupe":
                        retour = bdd.getInfosGPE(code)
                        if not retour:
                            elem = ["Le code %s n'est plus valide pour ce groupe." % code, code, "0"]
                        else:
                            elem = list(retour)
                    nbSeances = 0
                    dicoAccess[code] = {"titre":      elem[0],
                                        "codegpe":    elem[-1],
                                        "type":       type,
                                        "nbetu":      elem[2],
                                        "nbseances":  nbSeances,
                                        "listeCours": [cours.Title]}
                else:
                    dicoAccess[code]["listeCours"].append(cours.Title)
        return dicoAccess

    def getListeEtudiants(self, code, typeCode):
        bdd = getToolByName(self, "portal_jalon_bdd")
        listeEtudiant = bdd.rechercherUtilisateurs(code, "Etudiant", True)
        return listeEtudiant

    def getListeEtudiantsTSV(self, cod_etp, cod_vrs_vet):
        listeEtudiant = self.getListeEtudiants(cod_etp, cod_vrs_vet)
        TSV = ["\t".join(["NOM", "PRENOM", "SESAME", "NUMERO ETUDIANT", "COURRIEL"])]
        for etudiant in listeEtudiant:
            TSV.append("\t".join([etudiant["LIB_NOM_PAT_IND"], etudiant["LIB_PR1_IND"], etudiant["SESAME_ETU"], str(etudiant["COD_ETU"]), etudiant["EMAIL_ETU"]]))
        return "\n".join(TSV)

    def getListeEtudiantsXLS(self, cod_etp):
        import tempfile
        from os import close
        from xlwt import Workbook, Style, Pattern, XFStyle

        bdd = getToolByName(self, "portal_jalon_bdd")
        listeEtudiants = bdd.rechercherEtudiantXLS(cod_etp)

        portal_membership = getToolByName(self, "portal_membership")
        authMember = portal_membership.getAuthenticatedMember()
        fd, path = tempfile.mkstemp('.%s-xlfiletransport' % authMember.getId())
        close(fd)

        # création
        listing = Workbook(encoding="utf-8")

        # création de la feuille 1
        feuil1 = listing.add_sheet("Liste %s" % cod_etp)

        styleEnTete = XFStyle()
        patternEnTete = Pattern()
        patternEnTete.pattern = Pattern.SOLID_PATTERN
        patternEnTete.pattern_fore_colour = Style.colour_map["black"]
        styleEnTete.pattern = patternEnTete
        styleEnTete.font.colour_index = Style.colour_map["white"]

        # ajout des en-têtes
        feuil1.write(0, 0, "Nom", styleEnTete)
        feuil1.write(0, 1, "Prénom", styleEnTete)
        feuil1.write(0, 2, "Sésame", styleEnTete)
        feuil1.write(0, 3, "Université", styleEnTete)
        feuil1.write(0, 4, "Courriel", styleEnTete)

        i = 1
        for etudiant in listeEtudiants:
            ligne1 = feuil1.row(i)
            ligne1.write(0, etudiant["LIB_NOM_PAT_IND"])
            ligne1.write(1, etudiant["LIB_PR1_IND"])
            ligne1.write(2, etudiant["SESAME_ETU"])
            ligne1.write(3, etudiant["UNIV_IND"])
            ligne1.write(4, etudiant["EMAIL_ETU"])
            i = i + 1

        listing.save(path)

        fp = open(path, 'rb')
        data = fp.read()
        fp.close()
        return {"length": str(os.stat(path)[6]), "data": data}

    def getListeModelesWims(self):
        modeles = []
        modeles_conf = jalon_utils.getAttributConf("wims_modele")
        for element in modeles_conf:
            try:
                idmodele, titremodele, catmodele = element.split("*-*")
                modeles.append(idmodele)
            except:
                pass
        return modeles

    def getLocaleDate( self, date, format = "%d/%m/%Y" ):
        return jalon_utils.getLocaleDate( date, format )

    def getConnectDate(self, data, sortable = False):
        return jalon_utils.getConnectDate( data, sortable )

    def getModelesWims(self):
        modeles = {}
        modeles_conf = jalon_utils.getAttributConf("wims_modele")
        for element in modeles_conf:
            try:
                idmodele, titremodele, catmodele = element.split("*-*")
                if not catmodele in modeles:
                    modeles[catmodele] = [{"value": idmodele, "title": titremodele}]
                else:
                    modeles[catmodele].append({"value": idmodele, "title": titremodele})
            except:
                pass
        return modeles

    def getPhotoTrombi(self, login):
        return jalon_utils.getPhotoTrombi(login)

    def getTypeLien(self):
        portal = self.portal_url.getPortalObject()
        jalon_properties = portal.portal_jalon_properties.getPropertiesMonEspace()
        typeLien = []
        if jalon_properties["activer_liens"]:
            typeLien.append({"macro":     "ajout-web",
                             "affichage": _(u"Lien web"),
                             "aide":      _(u"Créer un lien à partir d'une URL"),
                             "checked":   "checked"})
            typeLien.append({"macro":     "ajout-video",
                             "affichage": _(u"Lien vidéo"),
                             "aide":      _(u"Créer un lien à partir d'un lecteur exportable comme Youtube, Dailymotion, WIMS"),
                             "checked":   ""})
        if jalon_properties["activer_liens_catalogue_bu"]:
            checked = ""
            if len(typeLien) == 0:
                checked = "checked"
            typeLien.append({"macro":     "ajout-catalogue",
                             "affichage": _(u"Lien catalogue"),
                             "aide":      _(u"Trouver une oeuvre ou une revue dans le catalogue de la BU"),
                             "checked":   checked})
        """
        if jalon_properties["activer_lille1pod"]:
            checked = ""
            if len(typeLien) == 0:
                checked = "checked"
            typeLien.append({"macro":     "ajout-elasticsearch",
                             "affichage": _(u"Lien UNSPOD"),
                             "aide":      _(u"Trouver une vidéo dans UNSPOD"),
                             "checked":   checked})
        """
        return typeLien

    def getShortText(self, text, limit=75):
        return jalon_utils.getShortText(text, limit)

    def getPlainShortText(self, html, limit=75):
        #self.plone_log("getPlainShortText")
        return jalon_utils.getPlainShortText(html, limit)

    def getSelectedTab(self, cle="onglet", defaut=""):
        # Init
        tabs = {}
        url = self.REQUEST.get('URL')
        spaceName = url[url.rfind('/') + 1:]
        if self.REQUEST.SESSION.has_key('tabs'):
            tabs = self.REQUEST.SESSION.get('tabs')
        # Traitement
        if self.REQUEST.form.has_key(cle):
            # Enregistrement de la sélection
            defaut = self.REQUEST.form[cle]
            tabs[spaceName] = defaut
            self.REQUEST.SESSION.set('tabs', tabs)
        else:
            # Pas de sélection
            if spaceName in tabs:
                # Enregistrement existant -> chargement
                defaut = tabs[spaceName]
        return defaut

    def getSelectedTags(self):
        # Init
        tags = {}
        subjects = ""
        spaceName = self.getId().lower()
        if self.REQUEST.SESSION.has_key('tags'):
            tags = self.REQUEST.SESSION.get('tags')
        # Traitement
        if self.REQUEST.form.has_key('subject'):
            # Enregistrement de la sélection
            subjects = self.REQUEST.form['subject']
            tags[spaceName] = subjects
            self.REQUEST.SESSION.set('tags', tags)
        else:
            # Pas de sélection
            if spaceName in tags:
                # Enregistrement existant -> chargement
                subjects = tags[spaceName]
            else:
                # Pas d'enregistrement -> défaut
                subjects = "last"
        return subjects

    def getTag(self):
        retour = []
        mots = list(self.Subject())
        mots.sort()
        if self.getId() in ["Webconference", "Sonorisation"]:
            for mot in mots:
                locale.setlocale(locale.LC_ALL, 'fr_FR')
                try:
                    retour.append({"tag": urllib.quote(mot), "titre": DateTime(mot).strftime("%B %Y")})
                except:
                    retour.append({"tag": urllib.quote(mot), "titre": mot})
        else:
            for mot in mots:
                retour.append({"tag": urllib.quote(mot), "titre": mot})
        """
        if self.getId() == "Wims":
            tags = self.getTagsWims()
            for mot in mots:
                try:
                    retour.append({"tag": urllib.quote(mot), "titre": tags[mot]})
                except:
                    retour.append({"tag": urllib.quote(mot), "titre": mot})

        if not self.getId() in ["Webconference", "Sonorisation", "Wims"]:
            for mot in mots:
                retour.append({"tag": urllib.quote(mot), "titre": mot})
        """

        """# DEBUG start
        print "\n••• getTag •••\n"
        print "self.id ->", self.getId()
        print "tag ->", tag
        print "mots ->", mots
        print "retour ->", retour
        print "\n"
        # DEBUG end"""

        #self.plone_log( retour )

        return retour

    def ajouterTag(self, tag):
        if not tag in self.Subject():
            tags = list(self.Subject())
            tags.append(tag)
            self.setSubject(tuple(tags))
            self.reindexObject()

    def ajouterUtilisateurJalon(self, form):
        portal = self.portal_url.getPortalObject()
        portal_registration = getToolByName(portal, 'portal_registration')
        portal_membership = getToolByName(portal, 'portal_membership')
        password = portal_registration.generatePassword()
        portal_membership.addMember(form["login"], password, ("EtudiantJalon", "Member",), "", {"fullname": form["fullname"], "email": form["email"]})
        portal_registration.registeredNotify(form["login"])

    def majFichier(self, fichier):
        items = fichier.getRelatedItems()
        for item in items:
            if item.portal_type in ["JalonCours"]:
                element_cours = copy.deepcopy(item.getElementCours())
                idFichier = fichier.getId()
                if "." in idFichier:
                    idFichier = idFichier.replace(".", "*-*")
                if idFichier in element_cours:
                    element_cours[idFichier]["titreElement"] = fichier.Title()
                    item.setElementsCours(element_cours)
            if item.portal_type in ["JalonBoiteDepot", "JalonCoursWims"]:
                dico = copy.deepcopy(item.getInfosElement())
                idFichier = fichier.getId()
                if "." in idFichier:
                    idFichier = idFichier.replace(".", "*-*")
                if idFichier in dico:
                    dico[idFichier]["titreElement"] = fichier.Title()
                    item.setInfosElement(dico)

    def dupliquerCours(self, idcours, creator, manager):
        """Permet de dupliquer le cours Jalon 'idcours'."""
        #LOG.info("[dupliquerCours]")
        import time
        home = self

        if manager:
            home = getattr(self.aq_parent, manager)
        try:
            idobj = home.invokeFactory(type_name='JalonCours', id="Cours-%s-%s" % (self.Creator(), DateTime().strftime("%Y%m%d%H%M%S")))
        except:
            time.sleep(1)
            idobj = home.invokeFactory(type_name='JalonCours', id="Cours-%s-%s" % (self.Creator(), DateTime().strftime("%Y%m%d%H%M%S")))
        duplicata = getattr(home, idobj)
        if self.Creator() == creator:
            cours = getattr(self, idcours)
        else:
            cours = getattr(getattr(self.aq_parent, creator), idcours)
        infos_element = copy.deepcopy(cours.getElementCours())

        # On duplique chaque classe de la liste getListeClasses() coté Wims,
        # et on assigne les identifiants des nouvelles classes au cours dupliqué
        listeClasses = cours.getListeClasses()
        #LOG.error('original.getListeClasses() : %s' % listeClasses)
        new_listeClasses = []

        # Cree une nouvelle classe WIMS pour chaque createur d'activité
        for index, dico in enumerate(listeClasses):
            new_listeClasses.append({})
            for auteur in dico:
                classe_id = dico[auteur]
                dico_wims = {"job": "copyclass", "code": self.portal_membership.getAuthenticatedMember().getId(), "qclass": classe_id}
                rep_wims = self.wims("callJob", dico_wims)
                rep_wims = self.wims("verifierRetourWims", {"rep": rep_wims, "fonction": "jalonfolder.py/dupliquerCours", "message": "parametres de la requete : %s" % dico_wims})
                if rep_wims["status"] == "OK":
                    #LOG.info('rep_wims["status"] : %s' % rep_wims["status"])
                    new_listeClasses[index][auteur] = rep_wims["new_class"]
                else:
                    message = _(u"Une erreur est survenue lors de la duplication des activités WIMS du cours. Merci de contacter votre administrateur svp.")
                    self.plone_utils.addPortalMessage(message, type='error')
        #LOG.info('new_listeClasses : %s' % new_listeClasses)

        duplicata.setListeClasses(new_listeClasses)
        param = {"Title":                  "%s (Duplicata du %s)" % (cours.Title(), DateTime().strftime("%d/%m/%Y - %H:%M:%S")),
                 "Description":            cours.Description(),
                 "Elements_glossaire":     cours.getGlossaire(),
                 "Elements_bibliographie": cours.getBibliographie(),
                 # ListClasse ne passe pas via setproperties : "AttributeError: 'dict' object has no attribute 'strip'""
                 #"Listeclasses":           new_listeClasses
                 }
        duplicata.setProperties(param)
        duplicata.setElementsCours(infos_element)
        duplicata.invokeFactory(type_name='Folder', id="annonce")
        duplicata.invokeFactory(type_name='Ploneboard', id="forum")
        forum = getattr(duplicata, "forum")
        forum.setTitle("Liste des forums du cours")
        duplicata.setPlanCours(copy.deepcopy(cours.getPlan()))

        dicoRep = {"Image":                    "Fichiers",
                   "File":                     "Fichiers",
                   "Page":                     "Fichiers",
                   "Lienweb":                  "Externes",
                   "Lien web":                 "Externes",
                   "Lecteurexportable":        "Externes",
                   "Referencebibliographique": "Externes",
                   "CatalogueBU":              "Externes",
                   "Catalogue BU":             "Externes",
                   "TermeGlossaire":           "Glossaire",
                   "Presentationssonorisees":  "Sonorisation",
                   "Exercice Wims":            "Wims"}

        portal_members = getattr(self.portal_url.getPortalObject(), "Members")

        #dico_espaces contiendra les espaces enseignants précédement chargés, afin d'optimiser le traitement.
        dico_espaces = {}

        for key in infos_element:
            #LOG.info('[dupliquerCours] KEY : %s' % key)
            duplicataObjet = None

            if key.startswith("BoiteDepot"):
                boite = getattr(cours, key, None)
                if boite:
                    duplicata.invokeFactory(type_name="JalonBoiteDepot", id=key)
                    duplicataObjet = getattr(duplicata, key)
                    param = {"Title":            boite.Title(),
                             "Description":      boite.Description(),
                             "DateDepot":        boite.getDateDepot(),
                             "DateRetard":       boite.getDateRetard(),
                             "ListeSujets":      copy.deepcopy(boite.getListeSujets()),
                             "ListeCorrections": copy.deepcopy(boite.getListeCorrections()),
                             "InfosElement":     copy.deepcopy(boite.getInfosElement()),
                             "DateAff":          boite.getDateAff(),
                             "DateMasq":         boite.getDateMasq()}
                    duplicataObjet.setProperties(param)

                    # Met a jour les relatedItems des documents.
                    infos_elements = duplicataObjet.getInfosElement()
                    self.associerCoursListeObjets(duplicata, duplicataObjet.getListeSujets(), infos_elements, dico_espaces, dicoRep, portal_members)

                else:
                    duplicataObjet = "Invalide"

            # Cas des activités WIMS
            if key.startswith("AutoEvaluation") or key.startswith("Examen"):
                activite = getattr(cours, key, None)
                if activite:
                    duplicata.invokeFactory(type_name="JalonCoursWims", id=key)
                    duplicataObjet = getattr(duplicata, key)
                    duplicataObjet.setJalonProperties(activite.getDicoProperties())

                    # Met a jour les relatedItems des documents et exercices.
                    infos_elements = duplicataObjet.getInfosElement()
                    self.associerCoursListeObjets(duplicata, duplicataObjet.getListeSujets(), infos_elements, dico_espaces, dicoRep, portal_members)
                    self.associerCoursListeObjets(duplicata, duplicataObjet.getListeExercices(), infos_elements, dico_espaces, dicoRep, portal_members)
                else:
                    duplicataObjet = "Invalide"
                    rep = '{"status": "ERROR", "message": "duplicata Objet Invalide"}'
                    self.wims("verifierRetourWims", {"rep": rep, "fonction": "jalonfolder.py/dupliquerCours", "message": "ID objet : %s | infos_element = %s" % (key, infos_element)})

            # L'objet n'a pas été dupliqué (tout sauf les activités)
            if not duplicataObjet:
                if infos_element[key]["typeElement"] in dicoRep and cours.isInPlan(key):
                    self.associerCoursListeObjets(duplicata, [key], infos_element[key], dico_espaces, dicoRep)

        relatedItems = cours.getRelatedItems()
        duplicata.setRelatedItems(relatedItems)
        duplicata.reindexObject()
        #LOG.error('duplicata.getListeClasses : %s' % str(duplicata.getListeClasses()))
        return duplicata.getId()

    def associerCoursListeObjets(self, idElement, liste_objets, infos_elements, dico_espaces, dicoRep, portal_members):
        u""" ajoute l'element "idElement" aux relatedItems de tous les objets de liste_objets.

        * infos_elements contient les infos de l'objet ?
        * dico_espaces contient les objets précédement chargés, afin d'optimiser le traitement.

        """
        #LOG.info('[associerCoursListeObjets] dico_espaces : %s' % dico_espaces)
        for id_objet in liste_objets:
            infos_objet = infos_elements[id_objet]
            repertoire = infos_objet["typeElement"]
            if repertoire in dicoRep:
                repertoire = dicoRep[repertoire]
            if "*-*" in id_objet:
                id_objet = id_objet.replace("*-*", ".")
            #On en profite pour remplir "dico_espaces", qui nous permettra d'éviter de trop nombreux appels à "getattr",
            # afin d'optimiser la tache pour des cours avec beacoup d'objets.
            createur = infos_objet["createurElement"]
            if createur not in dico_espaces:
                dico_espaces[createur] = {"espace" : getattr(portal_members, createur)}
            espace_createur = dico_espaces[createur]["espace"]

            if repertoire not in infos_objet["createurElement"]:
                dico_espaces[createur][repertoire] = getattr(espace_createur, repertoire)
            rep_createur = dico_espaces[createur][repertoire]

            objet = getattr(rep_createur, id_objet, None)
            if objet:
                relatedItems = objet.getRelatedItems()
                if self not in relatedItems:
                    relatedItems.append(idElement)
                    objet.setRelatedItems(relatedItems)
                    objet.reindexObject()

    def getElementView(self, idElement):
        return jalon_utils.getElementView(self, "MonEspace", idElement)

    def isNouveau(self, idcours):
        portal = self.portal_url.getPortalObject()
        portal_catalog = getToolByName(portal, "portal_catalog")
        liste = list(portal_catalog.searchResults(portal_type="JalonCours", id=idcours))
        member = self.portal_membership.getAuthenticatedMember()
        for cours in liste:
            if member.getId() == cours.Creator:
                if cmp(cours.getDateDerniereActu, member.getProperty('login_time', None)) > 0:
                    return True
                return False
            elif cmp(cours.getDateDerniereActu, self.getLastLogin()) > 0:
                return True
        return False

    def isPersonnel(self, user, mode_etudiant="false"):
        if mode_etudiant == "true":
            return False
        if user.has_role(["Manager", "Personnel", "Secretaire"]):
            return True
        return False

    #------------------------#
    #   Utilitaire Connect   #
    #------------------------#
    def connect(self, methode, param):
        connect = getToolByName(self, jalon_utils.getAttributConf("%s_connecteur" % self.getId().lower()))
        return connect.__getattribute__(methode)(param)

    def getSessionConnect(self, authMember):
        motdepasse = self.getComplement()
        self.connect('connexion', {})
        if not motdepasse:
            motdepasse = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(8)])
            self.setComplement(motdepasse)
            liste = ["Webconference", "Sonorisation"]
            liste.remove(self.getId())
            idrep = liste[0]
            getattr(self.aq_parent, idrep).setComplement(motdepasse)
            member = self.portal_membership.getMemberById(authMember)
            auth_email = member.getProperty("email")
            fullname = member.getProperty("fullname")
            if not fullname:
                fullname = member.getProperty("displayName")
            if not auth_email:
                auth_email = member.getProperty("mail")
            self.connect('creerUser', {'userid': authMember, "password": motdepasse, "fullname": fullname, "email": auth_email})
        else:
            self.connect('majPasswordUser', {'userid': authMember, "password": motdepasse})
        return self.connect('genererSessionUser', {'userid': authMember, "password": motdepasse})

    def getReunion(self, authMember, request):
        dossiers = self.connect("getAttribut", {"attribut": "dossiers"})
        if dossiers:
            modele = ""
            for ligne in dossiers.split("\n"):
                if self.getId() in ligne:
                    modele = ligne.split(":")[-1]
                    break
            if modele == "":
                return []
            else:
                modele = modele.replace("\r", "")
        else:
            return {"idreunion": "", "urlreunion": ""}
        reunions = self.connect("rechercherReunions", {"login": authMember, "modele": modele})
        if not reunions:
            motdepasse = self.getComplement()
            if motdepasse:
                member = self.portal_membership.getMemberById(authMember)
                fullname = member.getProperty("fullname")
                if not fullname:
                    fullname = member.getProperty("displayName")
                reunion = self.connect('creerReunion', {'userid': authMember, "password": motdepasse, "fullname": fullname, "modele": modele, "repertoire": self.getId()})
                self.plone_log("reunion")
                self.plone_log(reunion)
            else:
                reunion = {"id": "", "url": ""}
        else:
            reunion = reunions[0]
        if request:
            request.SESSION.set("idreunion", reunion["id"])
        return {"idreunion": reunion["id"], "urlreunion": reunion["url"]}

    def delEnregistrementConnect(self, paths):
        for path in paths:
            idEnregistrement = path.split("/")[-1]
            idConnect = idEnregistrement.split("-")[0]
            self.connect("supprimerEnregistrement", {"idEnregistrement": idConnect})

    def isSameServer(self, url1, url2):
        return jalon_utils.isSameServer(url1, url2)

    #---------------------#
    #   Utilitaire Wims   #
    #---------------------#
    def wims(self, methode, param):
        """ Lien vers la fonction wims du connecteur dédié """
        wims = getToolByName(self, jalon_utils.getAttributConf("wims_connecteur"))
        return wims.__getattribute__(methode)(param)

    def transfererExosWIMS(self, user_source):
        u"""Transfert des exercices WIMS d'un prof "user_source" vers le jalonfolder courant.

        # Exemple de script a créer dans la ZMI pour pouvoir utiliser cette fonction par l'admin :
        #       portal = context.portal_url.getPortalObject()
        #       dossierWIMS = getattr(getattr(portal.Members, "id_destination"), "Wims")
        #       return dossierWIMS.transfererExosWIMS("id_source")

        """
        #On verifie que self est bien un dossier wims.
        if self.getId() != "Wims":
            return {"status": "ERROR", "message": "Cette fonction doit etre appelee depuis un dossier WIMS"}
        portal = self.portal_url.getPortalObject()
        source = getattr(getattr(portal.Members, user_source), "Wims")

        # On demande la liste des exercices WIMS, ce qui aura pour conséquence la création du groupement si celui-ci n'existait pas.
        listeExos = source.objectValues("JalonExerciceWims")

        """
        # Procedure liee aux images WIMS :
        # TODO : Si un dossier d'images existe sur WIMS, il faudrait le transferer également.
        """

        listeSubject = list(self.Subject())
        #etiquette = jalon_utils.getDisplayName(user_source)
        #etiquette = etiquette.encode("utf-8")
        etiquette = jalon_utils.getInfosMembre(user_source)["fullname"]

        authMember = self.aq_parent.getId()
        nbExos = 0
        listeSeries = []
        # Une fois le groupement existant, on peut alors y ajouter les exercices.
        for exercice in listeExos:
            idExo = exercice.getId()
            modele = exercice.getModele()
            # Ajout de l'exercice côté Jalon
            self.invokeFactory(type_name='JalonExerciceWims', id=idExo)
            newExo = getattr(self, idExo)
            newExo.manage_setLocalRoles(authMember, ["Owner"])
            newExo.setProperties({"Title": exercice.Title(),
                                  "Modele": modele})

            if modele == "externe":
                newExo.setProperties({"Permalink": exercice.getPermalink()})

            elif modele == "groupe":
                newExo.setProperties({"Qnum":         exercice.getQnum(),
                                      "ListeIdsExos": exercice.getListeIdsExos()})
                listeSeries.append(idExo)
                # on reporte le traitement à plus tard. il faut d'abord que tous les exos soient importés.

            # Cas classique : on ajoute l'exercice côté WIMS
            else:
                fichierWims = self.wims("callJob", {"job": "getexofile", "qclass": "%s_1" % source.getComplement(), "qexo": idExo, "code": authMember})
                try:
                    retourWIMS = json.loads(fichierWims)
                    # Si json arrive a parser la reponse, c'est une erreur. WIMS doit être indisponible.
                    return {"status": "ERROR", "message": "jalonfolder/transfererExosWIMS : Impossible d'ajouter un exercice", "nbExos": nbExos, "user_source": user_source, "user_dest": authMember, "retourWIMS": retourWIMS}
                except:
                    pass
                fichierWims = fichierWims.decode("utf-8").encode("iso-8859-1")
                dico = {"job":    "addexo",
                        "code":   authMember,
                        "data1":  fichierWims,
                        "qexo":   idExo,
                        "qclass": "%s_1" % self.getComplement()}
                json.loads(self.wims("callJob", dico))

            self.setTagDefaut(newExo)
            subject = list(newExo.Subject())
            subject.append(urllib.quote(etiquette))
            newExo.setSubject(subject)

            #Mise à jour des étiquettes du parent
            if not etiquette in listeSubject:
                listeSubject.append(etiquette)
            newExo.reindexObject()

            nbExos = nbExos + 1

        # on reparcourt uniquement les groupes d'exercices, pour pouvoir mettre a jour les "relatedItems"
        for groupe in listeSeries:
            objetGroupe = getattr(self, groupe)
            listeExosGroupe = objetGroupe.getListeIdsExos()

            if len(listeExosGroupe) > 0:
                for exoIdGroupe in listeExosGroupe:
                    exo = getattr(self, exoIdGroupe, None)
                    if exo:
                        relatedItems = exo.getRelatedItems()
                        relatedItems.append(objetGroupe)
                        exo.setRelatedItems(relatedItems)
                        exo.reindexObject()

        self.setSubject(tuple(listeSubject))
        self.reindexObject()

        return {"status": "OK", "message": "import reussi", "nbExos": nbExos, "user_source": user_source, "user_dest": authMember}

    def delClassesWims(self, listClasses):
        for classe in listClasses:
            dico = {"job": "delclass", "code": self.portal_membership.getAuthenticatedMember().getId(), "qclass": classe}
            rep_wims = self.wims("callJob", dico)
            self.wims("verifierRetourWims", {"rep": rep_wims, "fonction": "jalonfolder.py/delClassesWims", "message": "parametres de la requete : %s" % dico})

    def delExoWims(self, paths):
        """ delExoWims() : suppression (coté wims) de la liste des exercices donné en "paths" """
        for path in paths:
            exo_id = path.split("/")[-1]
            exo = getattr(self, exo_id)
            exo.delExoWims()

    def getTagsWims(self):
        tags = {"groupe": "Groupe d'exercices"}
        modeles_conf = jalon_utils.getAttributConf("wims_modele")
        for element in modeles_conf:
            try:
                idmodele, titremodele, catmodele = element.split("*-*")
                if not idmodele in tags:
                    tags[idmodele] = titremodele
            except:
                pass
        return tags

    #----------------------#
    #   Utilitaire Primo   #
    #----------------------#
    def rechercherCatalogueBU(self, termeRecherche, typeRecherche):
        portal_primo = getToolByName(self, "portal_primo")
        if typeRecherche == "liste":
            resultat = portal_primo.rechercherCatalogueBU(termeRecherche)
        elif typeRecherche == "BU":
            resultat = portal_primo.BUResult(termeRecherche)
        elif typeRecherche == "suggestion":
            resultat = portal_primo.BUacquisition()
        else:
            pass
        return resultat

    #-----------------------#
    # Utilitaire JalonBDD   #
    #-----------------------#
    def jalonBDD(self, methode, param):
        bdd = getToolByName(self, "portal_jalon_bdd")
        return bdd.__getattribute__(methode)(**param)

    def getIndividu(self, sesame, return_type=None):
        return jalon_utils.getIndividu(sesame, return_type)

    def getIndividus(self, sesame_list, return_type=None):
        return jalon_utils.getIndividus(sesame_list, return_type)

    #----------------------------#
    # Utilitaire Elasticsearch   #
    #----------------------------#
    def searchElasticsearch(self, type_search=None, term_search=None, page=1):
        portal = self.portal_url.getPortalObject()
        portal_elasticsearch = getattr(portal, "portal_jalon_elasticsearch", None)
        return portal_elasticsearch.searchElasticsearch(type_search, term_search, page)

    def getNameServeurElasticsearch(self):
        portal = self.portal_url.getPortalObject()
        portal_elasticsearch = getattr(portal, "portal_jalon_elasticsearch", None)
        return portal_elasticsearch.getPropertiesElasticsearch()["name_serveur"]

    def getUrlServeurElasticsearch(self):
        portal = self.portal_url.getPortalObject()
        portal_elasticsearch = getattr(portal, "portal_jalon_elasticsearch", None)
        return portal_elasticsearch.getPropertiesElasticsearch()["url_connexion"]

    #-----------------#
    #   Utilitaires   #
    #-----------------#
    def getJalonProperty(self, info):
        return jalon_utils.getJalonProperty(info)

    def _uploader_id(self):
        return 'uploader%s' % str(random.random()).replace('.', '')

    def encodeUTF8(self, itemAEncoder):
        return jalon_utils.encodeUTF8(itemAEncoder)

    def header_upload(self, request):
        session = request.get('SESSION', {})
        medialabel = session.get('mediaupload', request.get('mediaupload', 'files'))
        if '*.' in medialabel:
            medialabel = ''
        if not medialabel:
            return _('Files Quick Upload')
        if medialabel == 'image':
            return _('Images Quick Upload')
        return _('%s Quick Upload' % medialabel.capitalize())

    def script_content(self):
        context = aq_inner(self)
        return context.restrictedTraverse('@@quick_upload_init')(for_id=self.uploader_id)

    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

    def tagFormat(self, tagSet):
        return jalon_utils.tagFormat(tagSet)

    def jalon_quote(self, encode):
        return jalon_utils.jalon_quote(encode)

    def jalon_unquote(self, decode):
        return jalon_utils.jalon_unquote(decode)

    def envoyerMail(self, form):
        jalon_utils.envoyerMail(form)

    def envoyerMailErreur(self, form):
        jalon_utils.envoyerMailErreur(form)

    def getInfosConnexion(self):
        return jalon_utils.getInfosConnexion()

    def getFilAriane(self, portal, folder, authMemberId, pageCours=None):
        return jalon_utils.getFilAriane(portal, folder, authMemberId, pageCours)

    def isLDAP(self):
        return jalon_utils.isLDAP()

    def getJalonPhoto(self, user_id):
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return jalon_properties.getJalonPhoto(user_id)

    #   Suppression marquage HTML
    def supprimerMarquageHTML(self, chaine):
        return jalon_utils.supprimerMarquageHTML(chaine)

    #supprimerCaractereSpeciaux
    def supprimerCaractereSpeciaux(self, chaine):
        return jalon_utils.supprimerCaractereSpeciaux(chaine)

    def getLastLogin(self):
        member = self.portal_membership.getAuthenticatedMember()
        last_login = member.getProperty('last_login_time', None)
        if isinstance(last_login, basestring):
            last_login = DateTime(last_login)
        return last_login

    def getJalonMenu(self, portal_url, user, request):
        return jalon_utils.getJalonMenu(self, portal_url, user, request)

    def getFooter(self):
        return jalon_utils.getFooter()

    #--------------------------------#
    #   Utilitaire GoogleAnalytics   #
    #--------------------------------#
    def gaEncodeTexte(self, chemin, texte):
        return jalon_utils.gaEncodeTexte(chemin, texte)

    #----------------------------#
    #   Utilitaire Intracursus   #
    #----------------------------#
    def creationSeance(self, codeMatiere, annee, periode, publiable, intitule, typeseance, dateseance, heureseance, dureeseance, avecnote, coefficient):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        return intracursus.creationSeanceServer(codeMatiere, annee, periode, publiable, intitule, typeseance, dateseance, heureseance, dureeseance, avecnote, coefficient)

    def listerSeance(self, codeMatiere):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        retour = intracursus.listerSeanceServer(codeMatiere)
        if retour["status"] == "REUSSITE":
            return retour["listeSeances"]
        return []

    def affichageSeance(self, dico):
        dicoType = {"":         "A définir",
                    "TD":       "Travaux Dirigés",
                    "TP":       "Travaux pratiques",
                    "CM":       "Cours Magistral",
                    "EXAM":     "Examen",
                    "EVAL":     "Evaluation",
                    "PART":     "Partiel",
                    "QCM":      "QCM",
                    "ORAL":     "Oral",
                    "CCI":      "CCI",
                    "CCT":      "CTT",
                    "SOUT":     "Soutenance",
                    "MPART":    "Moyenne Partielle",
                    "CCTEXAM":  "CCT ou Examen Terminal",
                    "EXAMTERM": "Examen Terminal"}
        dico["type"] = dicoType[dico["type"]]
        dico["date"] = DateTime(dico["date"], datefmt='international').strftime("%d/%m/%Y")
        if dico["avecnote"] == '0':
            dico["avecnote"] = False
        else:
            dico["avecnote"] = True
        if dico["publiable"] == '0':
            dico["publiable"] = False
        else:
            dico["publiable"] = True
        return dico

# enregistrement dans la registery Archetype
registerATCT(JalonFolder, PROJECTNAME)
