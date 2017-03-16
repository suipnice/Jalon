# -*- coding: utf-8 -*-
"""Jalon Folder."""
from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.folder import ATFolder, ATFolderSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager

from persistent.dict import PersistentDict

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonFolder

from Acquisition import aq_inner
from DateTime import DateTime

import locale
import json
import urllib
import random
import jalon_utils
import string
import os
import copy

from logging import getLogger
LOG = getLogger('[JalonFolder]')
"""
# Log examples :
#LOG.debug('debug message')
# LOG.info('info message')
#LOG.warn('warn message')
#LOG.error('error message')
#LOG.critical('critical message')
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
    """Un dossier Jalon."""

    implements(IJalonFolder)
    meta_type = 'JalonFolder'
    schema = JalonFolderSchema

    folder_my_space_dict = {"Fichiers":      "mes_ressources/mes_fichiers",
                            "Sonorisation":  "mes_ressources/mes_presentations_sonorisees",
                            "Wims":          "mes_ressources/mes_exercices_wims",
                            "Externes":      "mes_ressources/mes_ressources_externes",
                            "Glossaire":     "mes_ressources/mes_termes_glossaire",
                            "Webconference": "mes_ressources/mes_webconferences",
                            "Video":         "mes_ressources/mes_videos_pod"}

    _subjects_dict = {}

    def __init__(self, *args, **kwargs):
        super(JalonFolder, self).__init__(*args, **kwargs)
        self.uploader_id = self._uploader_id()

    # --------------------- #
    #  Installation method  #
    # --------------------- #
    def addSubJalonFolder(self, memberid):
        addSubJalonFolder(self, memberid)

    def setPortlets(self):
        manager = getUtility(IPortletManager, name=u"plone.leftcolumn")
        blacklist = getMultiAdapter((self, manager), ILocalPortletAssignmentManager)
        blacklist.setBlacklistStatus("context", True)
        self.reindexObject()

    # -------------------- #
    #  My Space Utilities  #
    # -------------------- #
    def getMySpaceFolder(self):
        # LOG.info("----- getMySpaceFolder -----")
        return self.folder_my_space_dict[self.getId()]

    def getMySubSpaceFolder(self, user_id, folder_id):
        # LOG.info("----- getMySubSpaceFolder -----")
        portal = self.portal_url.getPortalObject()
        return getattr(getattr(portal.Members, user_id), folder_id)

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

    def isObjectAttached(self, object_context):
        # LOG.info("----- isObjectAttached -----")
        return "is_object_attached" if len(object_context.getRelatedItems()) else "isnt_object_attached"

    def getSearchPodVideosBreadcrumbs(self):
        return [{"title": _(u"Mes ressources"),
                 "icon":  "fa fa-folder-open",
                 "link":  self.aq_parent.absolute_url()},
                {"title": _(u"Mes contenus UNSPod"),
                 "icon":  "fa fa-youtube-play",
                 "link":  self.absolute_url()},
                {"title": _(u"Rechercher un contenu sur UNSPod"),
                 "icon":  "fa fa-search",
                 "link":  "%s/search_pod_videos_form" % self.absolute_url()}]

    # ---------------------- #
    #  My Courses utilities  #
    # ---------------------- #

    def getCourseUserFolder(self, user_id):
        # LOG.info("----- getCourseUserFolder -----")
        return jalon_utils.getCourseUserFolder(self, user_id)

    def getCourseProperties(self, course_id):
        LOG.info("----- getCourseProperties -----")
        portal = self.portal_url.getPortalObject()
        portal_catalog = portal.portal_catalog
        course_object = portal_catalog.searchResults(portal_type="JalonCours", getId=course_id)[0].getObject()
        course_desc = course_object.getRawDescription()
        if not course_desc:
            course_desc = "Description non renseignée."
        return {"course_title": course_object.Title(),
                "course_desc":  course_desc,
                "course_link":  course_object.absolute_url()}

    def isFavorite(self, user_id, course_id):
        # LOG.info("----- isFavorite -----")
        course_user_folder = self.getCourseUserFolder(user_id)
        course = getattr(course_user_folder, course_id)
        favorites = list(course.Subject())
        # LOG.info("favorites : %s" % favorites)
        return True if user_id in favorites else False

    def modifyFavoriteCourse(self, user_id, course_id):
        # LOG.info("----- modifyFavorite -----")
        course_user_folder = jalon_utils.getCourseUserFolder(self, user_id)
        course = getattr(course_user_folder, course_id)
        favorites = list(course.Subject())
        if user_id not in favorites:
            favorites.append(user_id)
            archives = list(course.getArchive())
            if user_id in archives:
                archives.remove(user_id)
                course.setArchive(tuple(archives))
        else:
            favorites.remove(user_id)
        course.setSubject(tuple(favorites))
        course.setCourseProperties({"DateDerniereModif": DateTime()})

    def modifyArchiveCourse(self, user_id, course_id):
        # LOG.info("----- modifyFavorite -----")
        course_user_folder = jalon_utils.getCourseUserFolder(self, user_id)
        course = getattr(course_user_folder, course_id)
        archives = list(course.getArchive())
        if user_id not in archives:
            archives.append(user_id)
            favorites = list(course.Subject())
            if user_id in favorites:
                favorites.remove(user_id)
                course.setSubject(tuple(favorites))
        else:
            archives.remove(user_id)
        course.setArchive(tuple(archives))
        course.setCourseProperties({"DateDerniereModif": DateTime()})

    def getDataCourseFormAction(self, user_id, course_id):
        # LOG.info("----- getDataCourseFormAction -----")
        course_user_folder = jalon_utils.getCourseUserFolder(self, user_id)
        course_object = getattr(course_user_folder, course_id)
        return course_object.getDataCourseFormAction(user_id, course_id)

    def getDataCourseWimsActivity(self, user_id, course_id):
        # LOG.info("----- getDataCourseWimsActivity -----")
        course_user_folder = jalon_utils.getCourseUserFolder(self, user_id)
        course_object = getattr(course_user_folder, course_id)
        return course_object.getDataCourseWimsActivity(user_id, course_id)

    def getClefsDico(self, dico):
        return jalon_utils.getClefsDico(dico)

    def getJalonCategories(self):
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return dict(jalon_properties.getCategorie())

    def getListeCours(self, authMember):
        portal = self.portal_url.getPortalObject()
        portal_catalog = getToolByName(portal, "portal_catalog")
        listeCours = list(portal_catalog.searchResults(
            portal_type="JalonCours", Creator=authMember))
        listeCoursAuteur = list(portal_catalog.searchResults(
            portal_type="JalonCours", getAuteurPrincipal=authMember))
        if listeCoursAuteur:
            listeCours.extend(listeCoursAuteur)
        listeCoursCoAuteur = list(portal_catalog.searchResults(
            portal_type="JalonCours", getCoAuteurs=authMember))
        if listeCoursCoAuteur:
            listeCours.extend(listeCoursCoAuteur)

        dicoAccess = {}
        bdd = getToolByName(portal, "portal_jalon_bdd")
        for cours in listeCours:
            for acces in cours.getListeAcces:
                type, code = acces.split("*-*")
                if code not in dicoAccess:
                    if type == "etape":
                        retour = bdd.getInfosEtape(code)
                        if not retour:
                            elem = ["Le code %s n'est plus valide pour ce diplôme." %
                                code, code, "0"]
                        else:
                            elem = list(retour)
                    if type in ["ue", "uel"]:
                        retour = bdd.getInfosELP2(code)
                        if not retour:
                            elem = ["Le code %s n'est plus valide pour cette UE / UEL." %
                                code, code, "0"]
                        else:
                            elem = list(retour)
                    if type == "groupe":
                        retour = bdd.getInfosGPE(code)
                        if not retour:
                            elem = ["Le code %s n'est plus valide pour ce groupe." %
                                code, code, "0"]
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

    def getCourseStatistics(self, course_id):
        LOG.info("----- getCourseStatistics START %s -----" % DateTime().strftime("%d/%m/%Y - %H:%M:%S"))
        portal = self.portal_url.getPortalObject()
        course_brain = portal.portal_catalog.searchResults(
            portal_type="JalonCours", id=course_id)[0]

        course_object = course_brain.getObject()
        frequentation_graph = ""
        requete = course_object.getConsultationByCoursByUniversityYearByDate(
            None, True, "Etudiant").all()
        if requete:
            requete_dict = dict(requete)
            frequentation_graph = course_object.genererFrequentationGraph(requete_dict)

        LOG.info("----- getCourseStatistics END %s -----" % DateTime().strftime("%d/%m/%Y - %H:%M:%S"))
        return {"course_link":  "%s/course_statistics_view" % course_object.absolute_url(),
                "course_graph": frequentation_graph}

    def insererConsultation(self, user, course_id, type_cons, id_cons):
        # LOG.info("----- insererConsultation -----")
        public_cons = "Anonymous"
        if user.has_role("Personnel"):
            public_cons = "Personnel"
            #username = user.getId()
            #if self.isAuteur(username):
            #    public_cons = "Auteur"
            #if username in self.coAuteurs:
            #    public_cons = "Co-auteur"
            #if username in self.coLecteurs:
            #    public_cons = "Lecteur"
        if user.has_role("EtudiantJalon") or user.has_role("Etudiant"):
            public_cons = "Etudiant"
        if user.has_role("Manager"):
            public_cons = "Manager"
        if user.has_role("Secretaire"):
            public_cons = "Secretaire"
        portal = self.portal_url.getPortalObject()
        portal.portal_jalon_bdd.insererConsultation(SESAME_ETU=user.getId(), ID_COURS=course_id, TYPE_CONS=type_cons, ID_CONS=id_cons, PUBLIC_CONS=public_cons)

    # ----------------------- #
    #  My Students Utilities  #
    # ----------------------- #
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
    #def getInfosMembre(self, username):
    #    # self.plone_log("getInfosMembre")
    #    return jalon_utils.getInfosMembre(username)

    def getListeEtudiants(self, code, typeCode):
        bdd = getToolByName(self, "portal_jalon_bdd")
        listeEtudiant = bdd.rechercherUtilisateurs(code, "Etudiant", True)
        return listeEtudiant

    def getListeEtudiantsTSV(self, cod_etp, cod_vrs_vet):
        listeEtudiant = self.getListeEtudiants(cod_etp, cod_vrs_vet)
        TSV = ["\t".join(["NOM", "PRENOM", "SESAME", "NUMERO ETUDIANT", "COURRIEL"])]
        for etudiant in listeEtudiant:
            TSV.append("\t".join([etudiant["LIB_NOM_PAT_IND"], etudiant["LIB_PR1_IND"], etudiant[
                       "SESAME_ETU"], str(etudiant["COD_ETU"]), etudiant["EMAIL_ETU"]]))
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
        feuil1.write(0, 3, "Numéro", styleEnTete)
        feuil1.write(0, 4, "Université", styleEnTete)
        feuil1.write(0, 5, "Courriel", styleEnTete)

        i = 1
        for etudiant in listeEtudiants:
            ligne1 = feuil1.row(i)
            ligne1.write(0, etudiant["LIB_NOM_PAT_IND"])
            ligne1.write(1, etudiant["LIB_PR1_IND"])
            ligne1.write(2, etudiant["SESAME_ETU"])
            ligne1.write(3, etudiant["COD_ETU"])
            ligne1.write(4, etudiant["UNIV_IND"])
            ligne1.write(5, etudiant["EMAIL_ETU"])
            i = i + 1

        listing.save(path)

        fp = open(path, 'rb')
        data = fp.read()
        fp.close()
        return {"length": str(os.stat(path)[6]), "data": data}

    def getLocaleDate(self, date, format="%d/%m/%Y"):
        return jalon_utils.getLocaleDate(date, format)

    def getConnectDate(self, data, sortable=False):
        return jalon_utils.getConnectDate(data, sortable)

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
        return typeLien

    def getShortText(self, text, limit=75):
        return jalon_utils.getShortText(text, limit)

    def getPlainShortText(self, html, limit=75):
        # self.plone_log("getPlainShortText")
        return jalon_utils.getPlainShortText(html, limit)

    # --------------------------------- #
    #  OLD TAG -> DELETE WHEN FINISHED  #
    # --------------------------------- #
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

    def ajouterTag(self, tag):
        if not tag in self.Subject():
            tags = list(self.Subject())
            tags.append(tag)
            self.setSubject(tuple(tags))
            self.reindexObject()

    # --------------------------------- #
    #  NEW TAG                          #
    # --------------------------------- #
    def getSubjectsDict(self, key=None):
        """Fournit le dictionnaire des étiquettes du dossier."""
        # LOG.info.info("----- getSubjectsDict -----")
        # LOG.info("***** item_id : %s" % key)
        # LOG.info.info("self._subjects_dict : %s" % self._subjects_dict)
        if key:
            return self._subjects_dict.get(key, None)
        return copy.deepcopy(self._subjects_dict)

    def setSubjectsDict(self, subjects_dict):
        """Définit le dictionnaire des étiquettes du dossier."""
        # LOG.info("----- setSubjectsDict -----")
        if type(self._subjects_dict).__name__ != "PersistentMapping":
            self._subjects_dict = PersistentDict(subjects_dict)
        else:
            self._subjects_dict = subjects_dict

    def getDisplaySubjects(self):
        """Affichage des étiquettes sur le formulaire étiquettage."""
        # LOG.info("----- getDisplaySubjects -----")

        folder_dict = {"mes_fichiers":                 "Fichiers",
                       "mes_presentations_sonorisees": "Sonorisation",
                       "mes_exercices_wims":           "Wims",
                       "mes_ressources_externes":      "Externes",
                       "mes_termes_glossaire":         "Glossaire",
                       "mes_webconferences":           "Webconference",
                       "mes_videos_pod":               "Video"}

        if self.getId() in folder_dict.keys():
            portal = self.portal_url.getPortalObject()
            member_id = portal.portal_membership.getAuthenticatedMember().getId()
            home = getattr(portal.Members, member_id)

            folder = getattr(home, folder_dict[self.getId()])
            folder_subjects = folder.getSubjectsDict()
        else:
            folder_subjects = self.getSubjectsDict()

        if folder_subjects:
            subjects_list = [{"tag_id": key, "tag_title": folder_subjects[key]}
                for key in folder_subjects.keys()]
            subjects_list.sort(lambda x, y: cmp(x["tag_title"], y["tag_title"]))
            # LOG.info("subjects_list : %s" % subjects_list)
            return subjects_list
        return []

    def getSelectedTags(self):
        # LOG.info("----- getSelectedTags -----")
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
            # LOG.info(tags)
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
        # LOG.info.info("----- getTag -----")
        retour = []
        mots = list(self.Subject())
        mots.sort()
        if self.getId() in ["Webconference", "Sonorisation"]:
            for mot in mots:
                locale.setlocale(locale.LC_ALL, 'fr_FR')
                try:
                    retour.append(
                        {"tag": urllib.quote(mot), "titre": DateTime(mot).strftime("%B %Y")})
                except:
                    retour.append({"tag": urllib.quote(mot), "titre": mot})
        else:
            tags_dict = self.getSubjectsDict()
            for mot in mots:
                retour.append({"tag": mot, "titre": tags_dict[mot]})
        return retour

    def getNewTagId(self):
        LOG.info("----- getNewTagId -----")
        portal = self.portal_url.getPortalObject()
        member_id = portal.portal_membership.getAuthenticatedMember().getId()
        home = getattr(portal.Members, member_id)

        folder_dict = {"mes_fichiers":                 "Fichiers",
                       "mes_presentations_sonorisees": "Sonorisation",
                       "mes_exercices_wims":           "Wims",
                       "mes_ressources_externes":      "Externes",
                       "mes_termes_glossaire":         "Glossaire",
                       "mes_webconferences":           "Webconference",
                       "mes_videos_pod":               "Video"}
        folder = getattr(home, folder_dict[self.getId()])

        folder_subjects = folder.getSubjectsDict()
        tag_id_list = folder_subjects.keys()
        if len(tag_id_list) > 0:
            tag_id_list.sort()
            return int(tag_id_list[-1]) + 1
        else:
            return "1"

    def addTagFolder(self, tag_id, tag_title):
        # LOG.info("----- addTagFolder -----")
        portal = self.portal_url.getPortalObject()
        member_id = portal.portal_membership.getAuthenticatedMember().getId()
        home = getattr(portal.Members, member_id)

        folder_dict = {"mes_fichiers":                 "Fichiers",
                       "mes_presentations_sonorisees": "Sonorisation",
                       "mes_exercices_wims":           "Wims",
                       "mes_ressources_externes":      "Externes",
                       "mes_termes_glossaire":         "Glossaire",
                       "mes_webconferences":           "Webconference",
                       "mes_videos_pod":               "Video"}
        folder = getattr(home, folder_dict[self.getId()])
        folder_subjects = folder.getSubjectsDict()
        if tag_title not in folder_subjects.values():
            folder_subjects[tag_id] = tag_title
            # LOG.info.info("folder_subjects : %s" % folder_subjects)
            folder.setSubjectsDict(folder_subjects)
            tags = list(folder.Subject())
            tags.append(tag_id)
            folder.setSubject(tuple(tags))
            folder.reindexObject()

    def editTagFolder(self, tag_id, tag_title):
        # LOG.info("----- addTagFolder -----")
        portal = self.portal_url.getPortalObject()
        member_id = portal.portal_membership.getAuthenticatedMember().getId()
        home = getattr(portal.Members, member_id)

        folder_dict = {"mes_fichiers":                 "Fichiers",
                       "mes_presentations_sonorisees": "Sonorisation",
                       "mes_exercices_wims":           "Wims",
                       "mes_ressources_externes":      "Externes",
                       "mes_termes_glossaire":         "Glossaire",
                       "mes_webconferences":           "Webconference",
                       "mes_videos_pod":               "Video"}
        folder = getattr(home, folder_dict[self.getId()])
        folder_subjects = folder.getSubjectsDict()
        if tag_id in folder_subjects.keys():
            folder_subjects[tag_id] = tag_title
            # LOG.info.info("folder_subjects : %s" % folder_subjects)
            folder.setSubjectsDict(folder_subjects)
            folder.reindexObject()

    def deleteTagFolder(self, tag):
        tag = urllib.unquote(tag)
        portal = self.portal_url.getPortalObject()
        member_id = portal.portal_membership.getAuthenticatedMember().getId()
        home = getattr(portal.Members, member_id)

        folder_dict = {"mes_fichiers":                 "Fichiers",
                       "mes_presentations_sonorisees": "Sonorisation",
                       "mes_exercices_wims":           "Wims",
                       "mes_ressources_externes":      "Externes",
                       "mes_termes_glossaire":         "Glossaire",
                       "mes_webconferences":           "Webconference",
                       "mes_videos_pod":               "Video"}
        folder = getattr(home, folder_dict[self.getId()])

        tags = list(folder.Subject())
        if tag in tags:
            tags.remove(tag)
            folder.setSubject(tuple(tags))
            folder_subjects = folder.getSubjectsDict()
            del folder_subjects[tag]
            folder.setSubjectsDict(folder_subjects)
            folder.reindexObject()

            # Mise à jour des sélections enregistrées en session
            tags_in_session = self.REQUEST.SESSION.get('tags')
            spaceName = folder.getId().lower()
            selected = tags_in_session[spaceName].split(",")
            try:
                selected.remove(tag)
            except ValueError:
                pass
            tags_in_session[spaceName] = ','.join(selected)
            self.REQUEST.SESSION.set('tags', tags_in_session)

    # -------- #
    #  DIVERS  #
    # -------- #
    def ajouterUtilisateurJalon(self, form):
        portal = self.portal_url.getPortalObject()
        portal_registration = getToolByName(portal, 'portal_registration')
        portal_membership = getToolByName(portal, 'portal_membership')
        password = portal_registration.generatePassword()
        portal_membership.addMember(form["login"], password, ("EtudiantJalon", "Member",), "", {
                                    "fullname": form["fullname"], "email": form["email"]})
        portal_registration.registeredNotify(form["login"])

    def majFichier(self, fichier):
        items = fichier.getRelatedItems()
        for item in items:
            if item.portal_type in ["JalonCours"]:
                element_cours = copy.deepcopy(item.getCourseItemProperties())
                idFichier = fichier.getId()
                #if "." in idFichier:
                idFichier = idFichier.replace(".", "*-*")
                if idFichier in element_cours:
                    if "titreElementMonEspace" in element_cours[idFichier]:
                        element_cours[idFichier]["titreElementMonEspace"] = fichier.Title()
                    else:
                        element_cours[idFichier]["titreElement"] = fichier.Title()
                    item.setCourseItemsProperties(element_cours)
            if item.portal_type in ["JalonBoiteDepot", "JalonCoursWims"]:
                dico = copy.deepcopy(item.getDocumentsProperties())
                idFichier = fichier.getId()
                #if "." in idFichier:
                idFichier = idFichier.replace(".", "*-*")
                if idFichier in dico:
                    dico[idFichier]["titreElement"] = fichier.Title()
                    item.setDocumentsProperties(dico)

    def dupliquerCours(self, idcours, creator, manager=False):
        """Permet de dupliquer le cours Jalon 'idcours'."""
        # LOG.info("----- dupliquerCours -----")
        import time
        home = self
        home_id = self.getId()
        if manager:
            home = getattr(self.aq_parent, manager)
            home_id = home.getId()

        cours = getattr(self, idcours)
        infos_element = copy.deepcopy(cours.getCourseItemProperties())

        try:
            idobj = home.invokeFactory(
                type_name='JalonCours', id="Cours-%s-%s" % (home_id, DateTime().strftime("%Y%m%d%H%M%S")))
        except:
            time.sleep(1)
            idobj = home.invokeFactory(
                type_name='JalonCours', id="Cours-%s-%s" % (home_id, DateTime().strftime("%Y%m%d%H%M%S")))
        duplicata = getattr(home, idobj)

        # On duplique chaque classe de la liste getListeClasses() coté Wims,
        # et on assigne les identifiants des nouvelles classes au cours dupliqué
        listeClasses = cours.getListeClasses()
        # LOG.error('original.getListeClasses() : %s' % listeClasses)
        new_listeClasses = []

        # Cree une nouvelle classe WIMS pour chaque createur d'activité
        for index, dico in enumerate(listeClasses):
            new_listeClasses.append({})
            for auteur in dico:
                classe_id = dico[auteur]
                dico_wims = {"job": "copyclass", "code": self.portal_membership.getAuthenticatedMember(
                    ).getId(), "qclass": classe_id}
                rep_wims = self.wims("callJob", dico_wims)
                rep_wims = self.wims("verifierRetourWims",
                                     {"rep": rep_wims,
                                      "fonction": "jalonfolder.py/dupliquerCours",
                                      "message":  "parametres de la requete : %s\ncours d'origine : %s\nduplicata : %s\nauteur : %s\n" % (dico_wims, idcours, idobj, auteur)})
                if rep_wims["status"] == "OK":
                    # LOG.info('rep_wims["status"] : %s' % rep_wims["status"])
                    new_listeClasses[index][auteur] = rep_wims["new_class"]
                else:
                    portal_jalon_properties = getToolByName(self, 'portal_jalon_properties')
                    contact_link = portal_jalon_properties.getLienContact()
                    admin_link = u"%s?subject=[%s] Erreur de duplication WIMS&amp;body=cours d'origine : %s%%0Dduplicata : %s%%0D%%0DDécrivez précisément votre souci svp:\n" % (
                        contact_link["contact_link"], contact_link["portal_title"], idcours, idobj)
                    message = _(
                        u'Une erreur est survenue lors de la duplication des activités WIMS du cours. Merci de <a href="%s"><i class="fa fa-envelope-o"></i>contacter votre administrateur</a> svp.' % admin_link)
                    self.plone_utils.addPortalMessage(message, type='error')
        # LOG.info('new_listeClasses : %s' % new_listeClasses)

        duplicata.setListeClasses(new_listeClasses)
        param = {"Title":                  "%s (Duplicata du %s)" % (cours.Title(), DateTime().strftime("%d/%m/%Y - %H:%M:%S")),
                 "Description":            cours.Description(),
                 "Elements_glossaire":     cours.getGlossaire(),
                 "Elements_bibliographie": cours.getBibliographie(),
                 }
        duplicata.setCourseProperties(param)
        duplicata.setCourseItemsProperties(infos_element)
        duplicata.invokeFactory(type_name='Folder', id="annonce")
        duplicata.invokeFactory(type_name='Ploneboard', id="forum")
        forum = getattr(duplicata, "forum")
        forum.setTitle("Liste des forums du cours")
        duplicata.setCourseMap(copy.deepcopy(cours.getPlan()))

        dicoRep = {"Image":                    "Fichiers",
                   "File":                     "Fichiers",
                   "Page":                     "Fichiers",
                   "Lienweb":                  "Externes",
                   "Lecteurexportable":        "Externes",
                   "Referencebibliographique": "Externes",
                   "CatalogueBU":              "Externes",
                   "TermeGlossaire":           "Glossaire",
                   "Presentationssonorisees":  "Sonorisation",
                   "Sonorisation":             "Sonorisation",
                   "Webconference":            "Webconference",
                   "ExerciceWims":             "Wims",
                   "ExercicesWims":            "Wims",
                   "Video":                    "Video"}

        portal_members = getattr(self.portal_url.getPortalObject(), "Members")

        # dico_espaces contiendra les espaces enseignants précédement chargés,
        # afin d'optimiser le traitement.
        dico_espaces = {}

        new_infos_element = copy.deepcopy(infos_element)
        for key in infos_element:
            # LOG.info('[dupliquerCours] KEY : %s' % key)
            duplicataObjet = None

            if key.startswith("BoiteDepot"):
                boite = getattr(cours, key, None)
                if boite:
                    duplicata.invokeFactory(type_name="JalonBoiteDepot", id=key)
                    duplicataObjet = getattr(duplicata, key)
                    param = {"Title":                   boite.Title(),
                             "Description":             boite.Description(),
                             "DateDepot":               boite.getDateDepot(),
                             "DateRetard":              boite.getDateRetard(),
                             "ListeSujets":             copy.deepcopy(boite.getDocumentsList()),
                             "ListeCorrections":        copy.deepcopy(boite.getListeCorrections()),
                             "DateAff":                 boite.getDateAff(),
                             "DateMasq":                boite.getDateMasq(),
                             "Profile":                 boite.getProfile(),
                             "CorrectionIndividuelle":  boite.getCorrectionIndividuelle(),
                             "NotificationCorrection":  boite.getNotificationCorrection(),
                             "Notation":                boite.getNotation(),
                             "NotificationNotation":    boite.getNotificationNotation(),
                             "AccesDepots":             boite.getAccesDepots(),
                             "AccesCompetences":        boite.getAccesCompetences(),
                             "AfficherCompetences":     boite.getAfficherCompetences(),
                             "ModifierCompetences":     boite.getModifierCompetences(),
                             "DateCorrection":          boite.getDateCorrection(),
                             "NombreCorrection":        boite.getNombreCorrection(),
                             "Penalite":                boite.getPenalite(),
                             "AdjustementPoints":       boite.getAdjustementPoints(),
                             "AccesGrille":             boite.getAccesGrille(),
                             "AccesEvaluation":         boite.getAccesEvaluation(),
                             "AutoriserAutoEvaluation": boite.getAutoriserAutoEvaluation(),
                             "AffectationEvaluation":   boite.getAffectationEvaluation()}
                    duplicataObjet.setProperties(param)
                    duplicataObjet.setDocumentsProperties(
                        copy.deepcopy(boite.getDocumentsProperties()))
                    duplicataObjet.setCriteriaDict(copy.deepcopy(boite.getCriteriaDict()))
                    duplicataObjet.setCompetences(copy.deepcopy(boite.getCompetences()))

                    # Met a jour les relatedItems des documents.
                    infos_elements_activite = duplicataObjet.getDocumentsProperties()
                    # LOG.info("infos_elements_activite : %s" % infos_elements_activite)
                    # LOG.info("liste sujets : %s" % duplicataObjet.getDocumentsList())
                    self.associerCoursListeObjets(duplicataObjet, duplicataObjet.getDocumentsList(),
                                                  infos_elements_activite, dico_espaces,
                                                  dicoRep, portal_members)
                    relatedItems = boite.getRelatedItems()
                    duplicataObjet.setRelatedItems(relatedItems)
                    duplicataObjet.reindexObject()
                else:
                    duplicataObjet = "Invalide"

            # Cas des activités WIMS
            if key.startswith("AutoEvaluation") or key.startswith("Examen"):
                activite = getattr(cours, key, None)
                if activite:
                    duplicata.invokeFactory(type_name="JalonCoursWims", id=key)
                    duplicataObjet = getattr(duplicata, key)
                    dico_Properties = activite.getDicoProperties()
                    duplicataObjet.setJalonProperties(dico_Properties)

                    # Met a jour les relatedItems des documents et exercices.
                    infos_elements_activite = dico_Properties["DocumentsProperties"]
                    self.associerCoursListeObjets(duplicataObjet, duplicataObjet.getListeSujets(),
                                                  infos_elements_activite, dico_espaces,
                                                  dicoRep, portal_members)
                    self.associerCoursListeObjets(duplicataObjet, duplicataObjet.getListeExercices(),
                                                  infos_elements_activite, dico_espaces,
                                                  dicoRep, portal_members)
                else:
                    duplicataObjet = "Invalide"
                    # On retire l'objet d'infos_element, afin qu'il ne soit pas listé dans le
                    # cours dupliqué.
                    del new_infos_element[key]
                    duplicata.setCourseItemsProperties(new_infos_element)
                    # On retire également l'objet des infos_element du cours d'origine, afin
                    # de corriger le bug.
                    cours.setCourseItemsProperties(new_infos_element)
                    rep = '{"status": "ERROR", "message": "duplicata Objet Invalide"}'
                    self.wims("verifierRetourWims", {"rep": rep,
                                                     "fonction": "jalonfolder.py/dupliquerCours",
                                                     "message": "ID cours : %s | ID objet : %s | L'id a été supprimé des 2 cours, ce bug ne devrait plus survenir ici." % (idcours, key)})

            # L'objet n'a pas été dupliqué (tout sauf les activités)
            if not duplicataObjet:
                repertoire = infos_element[key]["typeElement"].replace(" ", "")
                # LOG.info("typeElement : %s" % repertoire)
                if repertoire in dicoRep and (cours.isInCourseMap(key) or key in cours.getGlossaire() or key in cours.getBibliographie()):
                    self.associerCoursListeObjets(
                        duplicata, [key], infos_element, dico_espaces, dicoRep, portal_members)

        relatedItems = cours.getRelatedItems()
        duplicata.setRelatedItems(relatedItems)
        duplicata.reindexObject()
        # LOG.error('duplicata.getListeClasses : %s' % str(duplicata.getListeClasses()))
        return duplicata.getId()

    def associerCoursListeObjets(self, conteneur_object, liste_objets, infos_elements, dico_espaces, dicoRep, portal_members):
        u"""ajoute l'element "conteneur_object" aux relatedItems de tous les objets de liste_objets.

        * infos_elements : les infos de l'objet ?
        * dico_espaces   : les objets précédement chargés, afin d'optimiser le traitement.
        * dicoRep
        * portal_members : dossier "Members", qu'on fournit afin d'optimiser.

        """
        # LOG.info("----- associerCoursListeObjets -----")
        # LOG.info('[associerCoursListeObjets] dico_espaces : %s' % dico_espaces)
        for id_objet in liste_objets:
            # LOG.info("object_id : %s" % id_objet)
            infos_objet = infos_elements[id_objet]
            repertoire = infos_objet["typeElement"].replace(" ", "")
            # LOG.info("typeElement : %s" % repertoire)
            if repertoire in dicoRep:
                repertoire = dicoRep[repertoire]
            if "*-*" in id_objet:
                id_objet = id_objet.replace("*-*", ".")
            # On en profite pour remplir "dico_espaces", qui nous permettra d'éviter de trop nombreux appels à "getattr",
            # afin d'optimiser la tache pour des cours avec beaucoup d'objets.
            createur = infos_objet["createurElement"]
            if createur not in dico_espaces:
                dico_espaces[createur] = {"espace": getattr(portal_members, createur)}
            espace_createur = dico_espaces[createur]["espace"]

            if repertoire not in infos_objet["createurElement"]:
                dico_espaces[createur][repertoire] = getattr(espace_createur, repertoire)
            rep_createur = dico_espaces[createur][repertoire]

            objet = getattr(rep_createur, id_objet, None)
            if objet:
                # LOG.info("object found")
                relatedItems = objet.getRelatedItems()
                if conteneur_object not in relatedItems:
                    LOG.info('---- on ajoute  ##%s## aux relatedItems de ##%s## ----' %
                             (conteneur_object.getId(), id_objet))
                    # on ajoute  ##<JalonCoursWims at
                    # AutoEvaluation-bado-20161201175055577435>## aux relatedItems de
                    # ##classerparpropriete-bado-20140901113857## ----
                    relatedItems.append(conteneur_object)
                    LOG.info('---- puis on ecrase les anciens relatedItems ---')
                    objet.setRelatedItems(relatedItems)
                    LOG.info("---- et enfin on réindexe l'objet ---")
                    objet.reindexObject()

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

    # ------------------------ #
    #    Utilitaire Connect    #
    # ------------------------ #
    def connect(self, methode, param):
        # LOG.info("----- connect -----")
        return self.portal_connect.__getattribute__(methode)(param)

    def getSessionConnect(self, authMember):
        motdepasse = self.getComplement()
        self.connect('connexion', {})
        if not motdepasse:
            motdepasse = ''.join(
                [random.choice(string.ascii_letters + string.digits) for i in range(8)])
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
            self.connect('creerUser', {
                         'userid': authMember, "password": motdepasse, "fullname": fullname, "email": auth_email})
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
                reunion = self.connect('creerReunion', {
                                       'userid': authMember, "password": motdepasse, "fullname": fullname, "modele": modele, "repertoire": self.getId()})
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
        """renvoit true si url1 pointe sur le meme serveur qu'url2. """
        return jalon_utils.isSameServer(url1, url2)

    # ---------------------- #
    #    Utilitaires Wims    #
    # ---------------------- #
    def wims(self, methode, param):
        """Lien vers la fonction WIMS du connecteur. """
        # LOG.info("----- wims -----")
        return self.portal_wims.__getattribute__(methode)(param)

    def transfererExosWIMS(self, user_source):
        u"""Transfert des exercices WIMS d'un prof "user_source" vers le jalonfolder courant.

        # Exemple de script a créer dans la ZMI pour pouvoir utiliser cette fonction par l'admin :
        #       portal = context.portal_url.getPortalObject()
        #       dossierWIMS = getattr(getattr(portal.Members, "id_destination"), "Wims")
        #       return dossierWIMS.transfererExosWIMS("id_source")

        """
        # On verifie que self est bien un dossier wims.
        if self.getId() != "Wims":
            return {"status": "ERROR", "message": "Cette fonction doit etre appelee depuis un dossier WIMS"}
        portal = self.portal_url.getPortalObject()
        source = getattr(getattr(portal.Members, user_source), "Wims")

        # On demande la liste des exercices WIMS, ce qui aura pour conséquence la
        # création du groupement si celui-ci n'existait pas.
        listeExos = source.objectValues("JalonExerciceWims")

        """
        # Procedure liee aux images WIMS :
        # TODO : Si un dossier d'images existe sur WIMS, il faudrait le transferer également.
        """

        listeSubject = list(self.Subject())
        etiquette = jalon_utils.getIndividu(user_source, "dict")["fullname"]

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
                # on reporte le traitement à plus tard. il faut d'abord que tous les exos
                # soient importés.

            # Cas classique : on ajoute l'exercice côté WIMS
            else:
                fichierWims = self.wims("callJob", {
                                        "job": "getexofile", "qclass": "%s_1" % source.getComplement(), "qexo": idExo, "code": authMember})
                try:
                    retourWIMS = json.loads(fichierWims)
                    # Si json arrive a parser la reponse, c'est une erreur. WIMS doit être
                    # indisponible.
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

            # self.setTagDefaut(newExo)
            subject = list(newExo.Subject())
            subject.append(urllib.quote(etiquette))
            newExo.setSubject(subject)

            # Mise à jour des étiquettes du parent
            if etiquette not in listeSubject:
                listeSubject.append(etiquette)
            newExo.reindexObject()

            nbExos = nbExos + 1

        # on reparcourt uniquement les groupes d'exercices, pour pouvoir mettre a
        # jour les "relatedItems"
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

    def delClassesWims(self, listClasses, request=None):
        """Supprime l'ensemble des classes WIMS de "listClasses"."""
        deleted_classes = []
        for classe in listClasses:
            dico = {"job": "delclass", "code":
                    self.portal_membership.getAuthenticatedMember().getId(), "qclass": classe}
            rep_wims = self.wims("callJob", dico)
            rep_wims = self.wims("verifierRetourWims",
                                 {"rep": rep_wims,
                                  "fonction": "jalonfolder.py/delClassesWims",
                                  "message": "parametres de la requete : %s" % dico,
                                  "jalon_request": request})
            if rep_wims["status"] == "OK":
                deleted_classes.append(classe)

        return deleted_classes

    def delExoWims(self, paths):
        u"""Suppression (coté wims) de la liste des exercices donnés en "paths"."""
        for path in paths:
            exo_id = path.split("/")[-1]
            exo = getattr(self, exo_id)
            exo.delExoWims()

    def getModelesWims(self):
        u"""Fournit le dico complet des modèles d'exercices WIMS (groupe compris)."""
        modele_wims = self.wims("getWimsProperty", "modele_wims")
        modele_wims["groupe"] = "Groupe d'exercices"
        return modele_wims

    # -------------------- #
    #   Utilitaire Primo   #
    # -------------------- #
    def searchBUCatalog(self, term_search, type_search="liste"):
        portal_primo = getToolByName(self, "portal_primo")
        if type_search == "liste":
            resultat = portal_primo.searchBUCatalog(term_search)
        elif type_search == "BU":
            resultat = portal_primo.BUResult(term_search)
        elif type_search == "suggestion":
            resultat = portal_primo.BUacquisition()
        else:
            pass
        return resultat

    # ----------------------- #
    #  Utilitaire JalonBDD    #
    # ----------------------- #
    def jalonBDD(self, methode, param):
        bdd = getToolByName(self, "portal_jalon_bdd")
        return bdd.__getattribute__(methode)(**param)

    def getIndividu(self, sesame, return_type=None):
        return jalon_utils.getIndividu(sesame, return_type)

    def getIndividus(self, sesame_list, return_type=None):
        return jalon_utils.getIndividus(sesame_list, return_type)

    # --------------------------- #
    #  Utilitaire Elasticsearch   #
    # --------------------------- #
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

    # ------------------ #
    #  Utilitaire Wowza  #
    # ------------------ #
    def searchVod(self, page, term_search=None):
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        return portal_jalon_wowza.searchExtraits(page, term_search)

    def getExpirationDate(self, streaming_id):
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        return portal_jalon_wowza.getExpirationDate(streaming_id.split("-")[-1])

    def isStreamingAuthorized(self, streaming_id, request):
        if not request.has_key("HTTP_X_REAL_IP"):
            return False
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        return portal_jalon_wowza.isStreamingAuthorized(streaming_id, request["HTTP_X_REAL_IP"])

    def askStreaming(self, streaming_id, member_id):
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        portal_jalon_wowza.askStreaming(streaming_id, member_id)

    # ---------------- #
    #    Utilitaires   #
    # ---------------- #
    def getPropertiesMessages(self, key=None):
        jalon_properties = self.portal_jalon_properties
        return jalon_properties.getPropertiesMessages(key)

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

    def isLDAP(self):
        return jalon_utils.isLDAP()

    def getJalonPhoto(self, user_id):
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return jalon_properties.getJalonPhoto(user_id)

    # Suppression marquage HTML
    def supprimerMarquageHTML(self, chaine):
        return jalon_utils.supprimerMarquageHTML(chaine)

    # supprimerCaractereSpeciaux
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

    def getBreadcrumbs(self):
        # Permet d'obtenir un fil d'ariane minimaliste.
        # (utile pour certaines pages communes comme les 404 par exemple)
        portal = self.portal_url.getPortalObject()
        return [{"title": _(u"Mes cours"),
                 "icon":  "fa fa-university",
                 "link":  "%s/mes_cours" % portal.absolute_url()}]

    # ------------------------------ #
    #   Utilitaire GoogleAnalytics   #
    # ------------------------------ #
    def gaEncodeTexte(self, chemin, texte):
        return jalon_utils.gaEncodeTexte(chemin, texte)

    # -------------------------- #
    #   Utilitaire Intracursus   #
    # -------------------------- #
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
