# -*- coding: utf-8 -*-
"""L'objet "Cours" de Jalon."""
from zope.interface import implements
from zope.component import getMultiAdapter

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
# from zipfile import ZipFile, ZIP_DEFLATED

import json
# import urllib2
import string
import jalon_utils
import random
import os
import copy

# from logging import getLogger
# LOG = getLogger('[JalonCours]')

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
    BooleanField("course_map_display",
                 required=True,
                 accessor="getCourseMapDisplay",
                 searchable=False,
                 default=False,
                 widget=BooleanWidget(label=_(u"Affichage du plan en mode page"))),
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
                widget=StringWidget(label=_(u"Le lien court MOOC d'un cours"),
                                    description=_(u"Le lien court MOOC n'existe que pour le cours en accès libre"),)),
    LinesField("plan",
               required=False,
               accessor="getPlan",
               searchable=False,
               widget=LinesWidget(label=_(u"Plan interactif"),
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
                 default=True,
                 widget=StringWidget(label=_(u"Envoie de courriels"),
                                     description=_(u"Envoyer un courriel à tous les utilisateurs du cours à chaque message posté dans un forum."),)),
    BooleanField("add_forum_permission",
                 required=False,
                 accessor="getAddForumPermission",
                 searchable=False,
                 widget=StringWidget(label=_(u"Permission d'ajout de forum par les étudiants"),
                                     description=_(u"EPermission d'ajout de forum par les étudiants."),)),
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
    LinesField("archive",
               required=False,
               accessor="getArchive",
               searchable=False,
               default=[],
               widget=LinesWidget(label=_(u"Utilisateur ayant archivé ce cours."),
                                  description=_(u"Archive(s) du cours."),
                                  visible={'view': 'visible', 'edit': 'invisible'},)),
))


class JalonCours(ATFolder):
    """Un cours Jalon."""

    implements(IJalonCours)
    meta_type = 'JalonCours'
    schema = JalonCoursSchema

    _elements_cours = {}
    _twitter_cours = {}

    _folder_my_space_dict = {"mes_fichiers":                 "Fichiers",
                             "mes_presentations_sonorisees": "Sonorisation",
                             "mes_exercices_wims":           "Wims",
                             "mes_ressources_externes":      "Externes",
                             "mes_termes_glossaire":         "Glossaire",
                             "mes_webconferences":           "Webconference",
                             "mes_videos_pod":               "Video"}

    _type_folder_my_space_dict = {"File":                    "Fichiers",
                                  "Image":                   "Fichiers",
                                  "Page":                    "Fichiers",
                                  "ExercicesWims":           "Wims",
                                  "Lienweb":                 "Externes",
                                  "Lecteurexportable":       "Externes",
                                  "CatalogueBU":             "Externes",
                                  "Video":                   "Video",
                                  "VOD":                     "VOD",
                                  "Sonorisation":            "Sonorisation",
                                  "Webconference":           "Webconference",
                                  "TermeGlossaire":          "Glossaire"}

    _activity_dict = {"1": {"activity_id":          "BoiteDepot",
                            "activity_title":       _(u"Boite de dépots"),
                            "activity_portal_type": "JalonBoiteDepot"},
                      "2": {"activity_id":          "AutoEvaluation",
                            "activity_title":       _(u"Entrainement WIMS"),
                            "activity_portal_type": "JalonCoursWims"},
                      "3": {"activity_id":          "Examen",
                            "activity_title":       _(u"Examen WIMS"),
                            "activity_portal_type": "JalonCoursWims"}}

    _actuality_dict = {"chapdispo":          _(u"et son contenu sont maintenant disponibles."),
                       "chapnondispo":       _(u"et son contenu ne sont plus disponibles."),
                       "dispo":              _(u"est disponible."),
                       "nondispo":           _(u"n'est plus disponible."),
                       "message":            _(u"Nouveau message dans le sujet de discussion."),
                       "datedepot":          _(u"Nouvelle date limite de dépôt : "),
                       "datedepotfin":       _(u"Le dépôt n'est plus permis"),
                       "correctiondispo":    _(u"La correction est disponible."),
                       "correctionnondispo": _(u"La correction n'est plus disponible"),
                       "sujetdispo":         _(u"Le sujet est disponible."),
                       "sujetnondispo":      _(u"Le sujet n'est plus disponible."),
                       "nouveauxdepots":     _(u"nouveau(x) dépôt(s) disponible(s)"),
                       "nouveauxmessages":   _(u"nouveau(x) message(s) disponible(s)")}

    _item_actions = [{"item_action_id":   "edit_course_item_visibility_form",
                      "item_action_icon": "fa fa-eye fa-fw",
                      "item_action_name": _(u"Afficher")},
                     {"item_action_id":   "edit_course_item_visibility_form",
                      "item_action_icon": "fa fa-eye-slash fa-fw",
                      "item_action_name": _(u"Masquer")},
                     {"item_action_id":   "edit_course_map_item_form",
                      "item_action_icon": "fa fa-pencil fa-fw",
                      "item_action_name": _(u"Modifier")},
                     {"item_action_id":   "mark_out_course_map_item_form",
                      "item_action_icon": "fa fa-hand-o-left fa-fw",
                      "item_action_name": _(u"Jalonner")},
                     {"item_action_id":   "course_detach_item_form",
                      "item_action_icon": "fa fa-chain-broken fa-fw",
                      "item_action_name": _(u"Détacher")},
                     {"item_action_id":   "course_delete_item_form",
                      "item_action_icon": "fa fa-trash-o fa-fw",
                      "item_action_name": _(u"Supprimer")}]

    _course_map_item_dict = {"1": {"form_title_type":    _(u"titre"),
                                   "is_type_title":      True,
                                   "item_type":          "Titre",
                                   "form_js":            "setRevealFormPlanRefresh('js-editCourseMapItem')"},
                             "2": {"form_title_type":    _(u"texte libre"),
                                   "is_type_title":      False,
                                   "item_type":          "TexteLibre",
                                   "form_js":            "setRevealFormPlanRefresh('js-editCourseMapItem','titreElement')"}}

    _course_delete_item_form = {"Titre":          {"form_title":       _(u"le titre"),
                                                   "form_has_warning": False},
                                "TexteLibre":     {"form_title":       _(u"le texte libre"),
                                                   "form_has_warning": False},
                                "BoiteDepot":     {"form_title":       _(u"la boite de dépôts"),
                                                   "form_has_warning": True,
                                                   "form_waning_text": _(u"vous devez récupérer les devoirs des étudiants avant de supprimer une boite de dépôts !")}}

    _training_offer_type = {"etape":   _(u"Diplôme"),
                            "ue":      _(u"Unité d'enseignement"),
                            "uel":     _(u"Unité d'enseignement libre"),
                            "groupe":  _(u"Groupe"),
                            "inconnu": _(u"Inconnu")}

    def __init__(self, *args, **kwargs):
        super(JalonCours, self).__init__(*args, **kwargs)
        self._elements_cours = {}

    # ------------ #
    #  Utilitaire  #
    # ------------ #
    def getCoursePasswordBreadcrumbs(self):
        # LOG.info("----- getCoursePasswordBreadcrumbs -----")
        portal_link = self.portal_url.getPortalObject().absolute_url()
        return[{"title": _(u"Mes cours"),
                "icon":  "fa fa-university",
                "link":  "%s/mes_cours" % portal_link},
               {"title": _(u"Accès par mot de passe"),
                "icon":  "fa fa-key",
                "link":  "%s/mes_cours?categorie=2" % portal_link},
               {"title": _(u"Vérification du mot de passe"),
                "icon":  "fa fa-search",
                "link":  "%s/check_course_password_form" % self.absolute_url()}]

    def getIconClass(self):
        """Return the course icon CSS class."""
        # LOG.info("----- getIconClass -----")
        return "fa fa-book"

    def checkCourseAuthorized(self, user, request):
        # LOG.info("----- checkCourseAuthorized -----")
        # LOG.info("***** SESSION : %s" % request.SESSION.get("course_authorized_list", []))
        # LOG.info(self.getLibre())
        # if self.getLibre():
        #    return True

        if self.getAcces() == "Public":
            # LOG.info("----- Course Authorized := Public ACCESS -----")
            return True

        if user.has_role(["Manager", "Owner"]):
            return True

        user_id = user.getId()
        if user.has_role(["Personnel", "Secretaire"]):
            if self.isAuteurs(user_id):
                return True
            if self.isCoLecteurs(user_id):
                return True

        course_authorized_list = request.SESSION.get("course_authorized_list", None)
        if course_authorized_list is None:
            portal = self.portal_url.getPortalObject()
            my_courses = getattr(portal.cours, user_id)
            view = getMultiAdapter((my_courses, request), name="mes_cours_view")
            view.getStudentCoursesList(user, "1", my_courses, False)
            course_authorized_list = request.SESSION.get("course_authorized_list", [])

        if not self.getId() in course_authorized_list:
            request.RESPONSE.redirect("%s/insufficient_privileges" % self.absolute_url())
        return True

    def getLastLogin(self):
        """Get last login time."""
        # LOG.info("----- getLastLogin -----")
        member = self.portal_membership.getAuthenticatedMember()
        last_login = member.getProperty('last_login_time', None)
        if isinstance(last_login, basestring):
            last_login = DateTime(last_login)
        return last_login

    def getBreadcrumbs(self):
        """Return the initial breadcrumbs of a course."""
        # LOG.info("----- getBreadcrumbs -----")
        portal = self.portal_url.getPortalObject()
        return [{"title": _(u"Mes cours"),
                 "icon":  "fa fa-university",
                 "link":  "%s/mes_cours" % portal.absolute_url()},
                {"title": self.Title(),
                 "icon":  "fa fa-book",
                 "link":  self.absolute_url()}]

    def getCourseItemProperties(self, key=None):
        """Fournit les propriétés des (ou d'un) element(s) du cours."""
        # Anciennement "getElementCours"
        # LOG.info("----- getCourseItemProperties -----")
        # LOG.info("***** item_id : %s" % key)
        if key:
            return self._elements_cours.get(key, None)
        return self._elements_cours

    def setCourseItemsProperties(self, elements_cours):
        """Définit la liste des propriétés des elements du cours."""
        # Anciennement "setElementCours"
        # LOG.info("----- setCourseItemsProperties -----")
        if type(self._elements_cours).__name__ != "PersistentMapping":
            self._elements_cours = PersistentDict(elements_cours)
        else:
            self._elements_cours = elements_cours

    # def getKeyElementCours(self):
    #    # LOG.info("----- getKeyElementCours -----")
    #    return self._elements_cours.keys()

    """def getDisplayOrHiddenDate(self, idElement, attribut):
        # LOG.info("----- getDisplayOrHiddenDate -----")
        infos_element = self.getCourseItemProperties(idElement)
        if infos_element:
            # LOG.info("item_property : %s" % str(infos_element))
            if infos_element[attribut] != "":
                return infos_element[attribut].strftime("%Y/%m/%d %H:%M")
        return DateTime().strftime("%Y/%m/%d %H:%M")
    """

    def getFormattedDate(self, date):
        """Fournit une date au format "Y/m/d H:M"."""
        # LOG.info("----- getFormattedDate -----")
        if date != "":
            return date.strftime("%Y/%m/%d %H:%M")
        else:
            return DateTime().strftime("%Y/%m/%d %H:%M")

    def setCourseProperties(self, dico):
        """ Met à jour les propriétés du cours (anciennement "setProperties")."""
        # LOG.info("----- setCourseProperties -----")
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        if key == "DateDerniereModif":
            self.reindexObject()

    def getCourseProperty(self, property_id):
        # LOG.info("----- getCourseProperty -----")
        return self.__getattribute__("_%s" % property_id)

    def getMySpaceFolder(self, user_id, folder_id):
        # LOG.info("----- getMySpaceFolder -----")
        return getattr(getattr(portal.Members, user_id), self._folder_my_space_dict[folder_id])

    def getMySubSpaceFolder(self, user_id, folder_id, portal):
        # LOG.info("----- getMySubSpaceFolder -----")
        return getattr(getattr(portal.Members, user_id), folder_id)

    def getCategorieCours(self):
        # LOG.info("----- getCategorieCours -----")
        try:
            return self.categorie[0]
        except:
            return 1

    def getRole(self):
        # LOG.info("----- getRole -----")
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

    # def getSousObjet(self, idElement):
    #    à remplacer par
    #    getattr(self, idElement)

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

    def useJalonUtils(self, method_name, method_parameters_dict):
        # LOG.info("----- useJalonUtils -----")
        # LOG.info("***** method_name : %s" % method_name)
        return jalon_utils.__getattribute__(method_name)(**method_parameters_dict)

    def getLocaleDate(self, date, format="%d/%m/%Y"):
        # LOG.info("----- getLocaleDate -----")
        return jalon_utils.getLocaleDate(date, format)

    def convertirDate(self, date):
        # LOG.info("----- convertirDate -----")
        return jalon_utils.convertirDate(date)

    def getShortText(self, text, limit=75):
        # LOG.info("----- getShortText -----")
        return jalon_utils.getShortText(text, limit)

    def getPlainShortText(self, html, limit=75):
        # LOG.info("----- getPlainShortText -----")
        return jalon_utils.getPlainShortText(html, limit)

    def supprimerMarquageHTML(self, chaine):
        # LOG.info("----- supprimerMarquageHTML -----")
        return jalon_utils.supprimerMarquageHTML(chaine)

    def remplaceChaine(self, chaine, elements):
        # LOG.info("----- remplaceChaine -----")
        return jalon_utils.remplaceChaine(chaine, elements)

    def test(self, condition, valeurVrai, valeurFaux):
        # LOG.info("----- test -----")
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

    def jalon_quote(self, encode):
        # LOG.info("----- jalon_quote -----")
        return jalon_utils.jalon_quote(encode)

    def getBaseAnnuaire(self):
        # LOG.info("----- getBaseAnnuaire -----")
        return jalon_utils.getBaseAnnuaire()

    def getFicheAnnuaire(self, valeur, base=None):
        # LOG.info("----- getFicheAnnuaire -----")
        return jalon_utils.getFicheAnnuaire(valeur, base)

    # -------------------------- #
    #  Course action My Courses  #
    # -------------------------- #
    def addCourseForum(self, forum_title, forum_description, user_id):
        # LOG.info("----- addCourseForum -----")

        forum_folder = self.forum
        forum_id = forum_folder.invokeFactory(type_name="PloneboardForum", id="Forum-%s-%s" % (user_id, DateTime().strftime("%Y%m%d%H%M%S%f")))
        forum_object = getattr(forum_folder, forum_id)

        forum_object.setTitle(forum_title)
        forum_object.setDescription(forum_description)
        forum_object.setMaxAttachments(0)
        forum_object.reindexObject()

        return forum_id

    def isAddForumPermission(self, is_personnel):
        # LOG.info("----- isAddForumPermission -----")
        add_forum_permission = self.getAddForumPermission()
        # LOG.info(add_forum_permission)
        if not add_forum_permission:
            return True if is_personnel else False
        else:
            return True

    def getDataCourseFormAction(self, user_id, course_id):
        # LOG.info("----- getDataCourseFormAction -----")
        return {"course_name":     self.getShortText(self.Title(), 80),
                "is_course_owner": self.isCourseOwner(user_id)}

    def modifyFavorite(self, user_id):
        # LOG.info("----- modifyFavorite -----")
        subjects = list(self.Subject())
        if user_id not in subjects:
            subjects.append(user_id)
            archives = list(self.getArchive())
            if user_id in archives:
                archives.remove(user_id)
                self.setArchive(tuple(archives))
        else:
            subjects.remove(user_id)
        self.setSubject(tuple(subjects))
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def modifyArchive(self, user_id):
        # LOG.info("----- modifyArchive -----")
        archives = list(self.getArchive())
        if user_id not in archives:
            archives.append(user_id)
            subjects = list(self.Subject())
            if user_id in subjects:
                subjects.remove(user_id)
                self.setSubject(tuple(subjects))
        else:
            archives.remove(user_id)
        self.setArchive(tuple(archives))
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    # ---------------- #
    #  Course Heading  #
    # ---------------- #
    def getShortDescription(self):
        # LOG.info("----- getShortDescription -----")
        description = self.Description()
        if not description:
            return {"link": False, "desc": "ce cours n'a pas encore de description."}
        if len(description) > 100:
            return {"link": True, "desc": self.getPlainShortText(description, 100)}
        return {"link": False, "desc": description}

    def isCourseOwner(self, user_id):
        # LOG.info("----- isCourseOwner -----")
        return True if self.aq_parent.getId() == user_id else False

    def isAuteur(self, username):
        # LOG.info("----- isAuteur -----")
        if username == self.Creator():
            return 1
        if username == self.getAuteurPrincipal():
            return 1
        return 0

    def isAuteurs(self, username):
        # LOG.info("----- isAuteurs -----")
        return self.isAuteur(username) or self.isCoAuteurs(username)

    def isInscriptionsLibre(self):
        # LOG.info("----- isInscriptionsLibre -----")
        if len(self.getInscriptionsLibre()) > 0:
            return True
        else:
            return False

    def getCreateur(self):
        # LOG.info("----- getCreateur -----")
        return self.useJalonUtils("getIndividu", {"sesame": self.Creator(), "type": "dict"})

    def getAuteur(self):
        # LOG.info("----- getAuteur -----")
        username = self.getAuteurPrincipal()
        if username:
            return self.useJalonUtils("getIndividu", {"sesame": username, "type": "dict"})
        return self.useJalonUtils("getIndividu", {"sesame": self.Creator(), "type": "dict"})

    def getAuteurs(self):
        # LOG.info("----- getAuteurs -----")
        return {"principal": self.getAuteur(), "coAuteurs": self.getCoAuteursCours()}

    def getAuthorForm(self):
        # LOG.info("----- getAuthorForm -----")
        course_author = self.getAuteur()
        course_creator = self.getCreateur()

        course_author_dict = {"course_author_name":  course_author["fullname"],
                              "course_creator_name": course_creator["fullname"]}

        if self.useJalonUtils("isLDAP", {}):
            ldap_base = self.useJalonUtils("getBaseAnnuaire", {})
            course_author_dict["course_author_link"] = self.useJalonUtils("getFicheAnnuaire", {"valeur": course_author,
                                                                                               "base":   ldap_base})
            course_author_dict["course_creator_link"] = self.useJalonUtils("getFicheAnnuaire", {"valeur": course_creator,
                                                                                                "base":   ldap_base})
        return course_author_dict

    def setAuteur(self, form):
        # LOG.info("----- setAuteur -----")
        ancienPrincipal = self.getAuteurPrincipal()
        if not ancienPrincipal:
            ancienPrincipal = self.Creator()
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été ajouté comme auteur du cours "%s" ayant eu pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace Mes cours.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), self.absolute_url(), portal.Title())
        self.auteurPrincipal = form["username"]
        infosMembre = self.useJalonUtils("getIndividu", {"sesame": form["username"], "type": "dict"})
        # self.tagBU(ancienPrincipal)
        self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                    "objet":   "Vous avez été ajouté à un cours",
                                                    "message": message}})
        infosMembre = self.useJalonUtils("getIndividu", {"sesame": ancienPrincipal, "type": "dict"})
        message = 'Bonjour\n\nVous avez été retiré du cours "%s" ou vous êtiez auteur.\n\nCordialement,\n%s.' % (self.Title(), portal.Title())
        self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                    "objet":   "Vous avez été retiré d'un cours",
                                                    "message": message}})
        self.manage_setLocalRoles(form["username"], ["Owner"])
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def getCoAuteursCours(self):
        # LOG.info("----- getCoAuteursCours -----")
        retour = []
        for username in self.getCoAuteurs():
            if username and username != "***":
                retour.append(self.useJalonUtils("getIndividu", {"sesame": username, "type": "dict"}))
        return retour

    def addCoAuteurs(self, form):
        # LOG.info("----- addCoAuteurs -----")
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été ajouté comme co-auteur du cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), self.absolute_url(), portal.Title())
        coAuteurs = list(self.getCoAuteurs())
        usernames = form["username"].split(",")
        if usernames != ['']:
            for username in usernames:
                if username not in coAuteurs:
                    coAuteurs.append(username)
                    self.manage_setLocalRoles(username, ["Owner"])
                    infosMembre = self.useJalonUtils("getIndividu", {"sesame": username, "type": "dict"})
                    self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                                "objet":   "Vous avez été ajouté à un cours",
                                                                "message": message}})
            self.coAuteurs = tuple(coAuteurs)
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def deleteCoAuteurs(self, form):
        # LOG.info("----- deleteCoAuteurs -----")
        auteurs = []
        if "auteur-actu" in form:
            auteurs = form["auteur-actu"]
        ancienAuteurs = set(self.getCoAuteurs())
        supprAuteurs = ancienAuteurs.difference(set(auteurs))

        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été retiré du cours "%s" ayant pour auteur %s ou vous êtiez co-auteur.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())

        for idMember in supprAuteurs:
            infosMembre = self.useJalonUtils("getIndividu", {"sesame": idMember, "type": "dict"})
            self.useJalonUtils("envoyerMail", {"form": {"a":      infosMembre["email"],
                                                        "objet":  "Vous avez été retiré d'un cours",
                                                        "message": message}})

        if auteurs == []:
            auteurs.append("***")
        self.coAuteurs = tuple(auteurs)
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def setCoursePublicAccess(self, course_public_access):
        # LOG.info("----- setCoursePublicAccess -----")
        if self.getAcces() != course_public_access:
            portal = self.portal_url.getPortalObject()
            portal_workflow = getToolByName(portal, "portal_workflow")

            workflow_action = "submit"
            state = "pending"
            if course_public_access == "Public":
                workflow_action = "publish"
                state = "published"
                court = self.getLienCourt()
                if not court:
                    dont_stop = 1
                    while dont_stop:
                        part1 = ''.join([random.choice(string.ascii_lowercase) for i in range(3)])
                        part2 = ''.join([random.choice(string.digits[1:]) for i in range(3)])
                        short = part1 + part2
                        link_object = getattr(portal.public, short, None)
                        if not link_object:
                            dont_stop = 0
                    portal.public.invokeFactory(type_name="Link", id=short)
                    link_object = getattr(portal.public, short)
                    link_object.setTitle(self.title_or_id())
                    link_object.setRemoteUrl(self.absolute_url())
                    portal_workflow.doActionFor(link_object, workflow_action, "jalon_workflow")
                    link_object.reindexObject()
                    self.setLienCourt(short)

                for course_object in self.objectValues():
                    if portal_workflow.getInfoFor(course_object, "review_state", wf_id="jalon_workflow") != state:
                        portal_workflow.doActionFor(course_object, workflow_action, "jalon_workflow")
                        # On va modifier l'etat de tous les elements contenus dans les activités du cours.
                        # (mais cette étape est pour le moment inutile puisque les activités ne sont pas accessibles dans un cours Public)
                        if course_object.meta_type in ["JalonBoiteDepot", "JalonCoursWims"]:
                            relatedItems = course_object.getRelatedItems()
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
        self.setAcces(course_public_access)

    def isCoAuteurs(self, username):
        # LOG.info("----- isCoAuteurs -----")
        u""" Détermine si l'utilisateur 'username' est un auteur ou co-auteur du cours."""
        if self.isAuteur(username):
            return True
        if username in self.coAuteurs:
            return True
        # Dans le cas de l'admin, isCoAuteurs renvoi 0 aussi
        # LOG.info("----- isCoAuteurs = 0 (ni auteur, ni coAuteur)")
        return 0

    def isCoLecteurs(self, username):
        # LOG.info("----- isCoLecteurs -----")
        return True if username in self.coLecteurs else False

    # ------------ #
    #  Course Map  #
    # ------------ #
    def getProprietesVideo(self, id_video):
        # LOG.info("----- getProprietesVideo -----")
        infos_element = self.getCourseItemProperties(id_video)
        video_title = infos_element["titreElement"]
        video_title_my_space = video_title
        if "titreElementMonEspace" in infos_element:
            video_title_my_space = infos_element["titreElementMonEspace"]
        return {"video_title":          video_title,
                "video_title_my_space": video_title_my_space,
                "is_display_in_map":    "checked" if infos_element["complementElement"]["value"] else ""}

    def getCommentaireEpingler(self, idTester=None):
        # LOG.info("----- getCommentaireEpingler -----")
        if len(self.getAvancementPlan()) <= 1:
            return ""

        if not idTester:
            return self.getAvancementPlan()[1]
        elif idTester == self.getAvancementPlan()[0]:
            return self.getAvancementPlan()[1]

        return ""

    def getDisplayCourseMapAttributes(self, user, mode_etudiant=False):
        # LOG.info("----- getDisplayCourseMapAttributes -----")
        return {"is_personnel":         self.isPersonnel(user, mode_etudiant),
                "user_last_login_time": user.getProperty('login_time', ""),
                "course_news":          self.getActualitesCours(),
                "item_jalonner":        self.getCourseMapItemJalonner(),
                "is_sub_course_map":    True,
                "portal":               self.portal_url.getPortalObject()}

    def getCourseMapItemForm(self, item_type, item_id):
        """Fournit les infos pour le formulaire de creation/modification d'un element du cours."""
        # LOG.info("----- getCourseMapItemForm -----")
        if not item_type:
            item_properties = self.getCourseItemProperties(item_id)
            item_type = "2" if item_properties["typeElement"] == "TexteLibre" else "1"

        form_properties = copy.deepcopy(self._course_map_item_dict[item_type])

        # Creation
        if not item_id:
            form_properties["data-success_msg"] = _(u"L'élément de plan a été créé.")
            form_properties["form_title_text"] = _(u"Créer un")
            form_properties["is_add_form"] = True
            form_properties["form_button_css"] = "button small create radius"
            form_properties["form_button_text"] = _(u"Créer")
            form_properties["form_button_icon"] = "fa fa-plus-circle"
            form_properties["validate_key"] = "create_course_map_item"
            form_properties["typeElement"] = ""
        # Modification
        else:

            form_properties["data-success_msg"] = _(u"L'élément de plan a été modifié.")
            form_properties["form_title_text"] = _(u"Modifier le")
            form_properties["is_add_form"] = False
            form_properties["item_id"] = item_id
            form_properties["form_button_css"] = "button small radius"
            form_properties["form_button_text"] = _(u"Modifier")
            form_properties["form_button_icon"] = "fa fa-pencil"
            form_properties["validate_key"] = "edit_course_map_item"

            form_properties["typeElement"] = item_properties["typeElement"]

            if item_properties["typeElement"] == "Titre":
                """
                Supp. du marquage HTML potentiellement présent dans les titres
                des éléments "titre" (cf. cours annales UFR Droit).
                """
                form_properties["item_title"] = self.supprimerMarquageHTML(
                    item_properties['titreElement'])

            elif item_properties["typeElement"] == "TexteLibre":
                """
                Rétrocompat. supp. listes dans les éléments "texte" :
                    contenu existant présenté lors de l'édition identique à
                    celui présenté dans le plan : CKEditor n'ajoutera pas le
                    tiret de substitution (à supp. si données existantes migrées
                    suite à la suppression des listes dans CKEditor).
                """
                form_properties["item_title"] = self.remplaceChaine(
                    item_properties["titreElement"], {
                        '<ol>':'',
                        '<ul>':'',
                        '</ol>':'',
                        '</ul>':'',
                        '<li>':'<p>- ',
                        '</li>':'</p>'
                    })

            else:
                form_properties["item_title"] = item_properties["titreElement"]

            if (item_type == "1" and form_properties["typeElement"] != "Titre"):
                form_properties["form_title_type"] = _(u"titre de l'élément")

            if item_properties["typeElement"].replace(" ", "") in self._type_folder_my_space_dict.keys():
                form_properties["item_title_in_my_space"] = item_properties["titreElement"]
                if "titreElementMonEspace" in item_properties:
                    form_properties["item_title_in_my_space"] = item_properties["titreElementMonEspace"]

                if item_properties["typeElement"] == "Video":
                    form_properties["is_item_display_in_course_map"] = True
                    form_properties["item_display_in_course_map"] = "checked" if item_properties["complementElement"]["value"] else ""

        return form_properties

    def getCourseMap(self, user_id, user_last_login_time, is_personnel, course_actuality_list, item_jalonner, portal):
        # LOG.info("----- getCourseMap -----")
        return self.getCourseMapItems(self.getPlan(), user_id, user_last_login_time, is_personnel, course_actuality_list, item_jalonner, portal, True)

    def getCourseMapAjax(self, course_map_id, user_id, my_view):
        # LOG.info("----- getCourseMapAjax -----")
        if not course_map_id or course_map_id == "all":
            if len(self.getCourseMapList()) > 50:
                my_view["is_sub_course_map"] = False
            my_view["course_map"] = self.getCourseMap(user_id, my_view['user_last_login_time'], my_view['is_personnel'], my_view['course_news']['listeActu'], my_view['item_jalonner'], my_view['portal'])
        else:
            my_view["course_map"] = self.getCourseMapTitle(course_map_id, user_id, my_view['user_last_login_time'], my_view['is_personnel'], my_view['course_news']['listeActu'], my_view['item_jalonner'], my_view['portal'])
        return my_view

    def getCourseMapTitle(self, course_map_id, user_id, user_last_login_time, is_personnel, course_actuality_list, item_jalonner, portal):
        # LOG.info("----- getCourseMapTitle -----")
        for item in list(self.getPlan()):
            if item["idElement"] == course_map_id:
                # item_properties = item
                # return self.getCourseMapItems([item_properties], user_id, user_last_login_time, is_personnel, course_actuality_list, item_jalonner, portal, True)
                return self.getCourseMapItems(item["listeElement"], user_id, user_last_login_time, is_personnel, course_actuality_list, item_jalonner, portal, True)

        return {"ol_css_id":              "course_plan-plan",
                "ol_css_class":           "",
                "course_map_items_list":  []}

    def getCourseMapFirstTitle(self):
        # LOG.info("----- getCourseMapFirstTitle -----")
        course_map_title = []
        item_properties_dict = self.getCourseItemProperties()
        for item in list(self.getPlan()):
            if item["idElement"].startswith("Titre"):
                item_properties = item_properties_dict[item["idElement"]]
                is_display_item = self.isAfficherElement(item_properties["affElement"], item_properties["masquerElement"])
                if is_display_item["val"]:
                    course_map_title.append({"title_id":   item["idElement"],
                                             "title_text": self.getPlainShortText(item_properties["titreElement"])})
        return course_map_title

    def getCourseMapItems(self, course_map_items_list, user_id, user_last_login_time, is_personnel, course_actuality_list, item_jalonner, portal, is_map_top_level=False):
        """Fournit la liste des elements a afficher dans le plan du cours."""
        # LOG.info("----- getCourseMapItems -----")
        # LOG.info(course_map_items_list)
        ol_css_id = ""
        ol_css_class = ""
        if is_map_top_level:
            ol_css_id = "course_plan-plan"
            if is_personnel:
                ol_css_class = "sortable ui-sortable"

        # index = 0
        course_map_list = []
        for course_map_item in course_map_items_list:
            # index = index + 1
            item_properties = self.getCourseItemProperties(course_map_item["idElement"])
            # LOG.info(course_map_item["idElement"])

            item = {"item_id":      course_map_item["idElement"],
                    "item_title":   item_properties["titreElement"],
                    "item_drop_id": "drop-%s" % course_map_item["idElement"].replace("*-*", ""),
                    "item_link":    "",
                    "item_video":   False}

            if "complementElement" in item_properties:
                if "value" in item_properties["complementElement"] and item_properties["complementElement"]["value"] and "image" in item_properties["complementElement"]:
                    item["item_video"] = True
                    item["item_image"] = item_properties["complementElement"]["image"]
                    item["item_auteur"] = item_properties["complementElement"]["auteur"]
                    try:
                        item["item_description"] = item_properties["complementElement"]["description"]
                    except:
                        item["item_description"] = "Description non disponible"

            is_display_item = self.isAfficherElement(item_properties["affElement"], item_properties["masquerElement"])
            item["is_display_item_bool"] = True if is_display_item["val"] else False
            item["is_display_item_icon"] = "fa %s fa-fw fa-lg no-pad right" % is_display_item["icon"]
            item["is_display_item_text"] = is_display_item["legende"]

            if is_personnel or item["is_display_item_bool"]:
                item["is_item_title"] = False
                item["item_css_class"] = "element"
                course_map_sub_items_list = []
                if "listeElement" in course_map_item:
                    item["is_item_title"] = True
                    item["item_css_class"] = "branch"
                    course_map_sub_items_list = course_map_item["listeElement"]
                else:
                    if item_properties["typeElement"] in ["BoiteDepot", "AutoEvaluation", "Examen", "TexteLibre"]:
                        item["item_div_css"] = "elemactivite"
                        item["item_link"] = "/".join([self.absolute_url(), course_map_item["idElement"], "view"])
                    elif item_properties["typeElement"] == "SalleVirtuelle":
                        item["item_div_css"] = "elemressource"
                        item["item_link"] = "%s/display_course_webconference_page?item_id=%s" % (self.absolute_url(), course_map_item["idElement"])
                    else:
                        item["item_div_css"] = "elemressource"
                        item["item_link"] = "%s?course_id=%s" % ("/".join([portal.absolute_url(), "Members", item_properties["createurElement"], self._type_folder_my_space_dict[item_properties["typeElement"].replace(" ", "")], course_map_item["idElement"].replace("*-*", "."), "view"]), self.getId())

                item["item_css_id"] = "%s-%s" % (item["item_css_class"], course_map_item["idElement"])
                item["item_span_css"] = "type%s" % item_properties["typeElement"].replace(" ", "").lower()
                item["course_map_sub_items_list"] = course_map_sub_items_list

                item["is_item_title_or_text"] = False

                if item_properties["typeElement"] in ["Titre", "TexteLibre"]:
                    item["is_item_title_or_text"] = True
                    item["item_div_css"] = "elem%s" % item_properties["typeElement"].lower()

                    if item_properties["typeElement"] == "Titre":
                        item["item_title"] = self.supprimerMarquageHTML(item["item_title"])

                    elif item_properties["typeElement"] == "TexteLibre":
                        """
                        Rétrocompat. supp. listes dans les éléments "texte" :
                            modification du contenu existant pour présentation
                            dans le plan (à supp. si données existantes migrées
                            suite à la suppression des listes dans CKEditor).
                        """
                        item["item_title"] = self.remplaceChaine(
                            item["item_title"], {
                                '<ol>':'',
                                '<ul>':'',
                                '</ol>':'',
                                '</ul>':'',
                                '<li>':'<p>- ',
                                '</li>':'</p>'
                            })

                item["is_item_readable"] = True if not is_personnel and not item["is_item_title"] else False

                if not is_personnel:
                    item["item_read_link"] = "%s/read_course_map_item_script?item_id=%s" % (self.absolute_url(), course_map_item["idElement"])
                    item["item_read_css"] = "decoche right"
                    item["item_read_icon"] = "fa fa-square-o fa-fw fa-lg no-pad"
                    if item["is_item_readable"] and "marque" in item_properties and user_id in item_properties["marque"]:
                        item["item_read_css"] = "coche right"
                        item["item_read_icon"] = "fa fa-check-square-o fa-fw fa-lg no-pad"
                else:
                    item["item_actions"] = self.getItemActions(item_properties, item["is_display_item_bool"])

                item["is_item_jalonner"] = False
                item["item_jalonner_comment"] = ""
                if course_map_item["idElement"] == item_jalonner["item_jalonner_id"]:
                    item["is_item_jalonner"] = True
                    item["item_jalonner_comment"] = item_jalonner["item_jalonner_comment"]

                item["is_item_new"] = True if item["is_display_item_bool"] and cmp(item_properties["affElement"], user_last_login_time) > 0 else False

                course_map_list.append(item)

        return {"ol_css_id":              ol_css_id,
                "ol_css_class":           ol_css_class,
                "course_map_items_list":  course_map_list}

    def orderCourseMapItems(self, course_map):
        # LOG.info("----- orderCourseMapItems -----")
        plan = []
        dicoplan = {}
        pre_plan = course_map.split("&")
        # LOG.info("***** pre_plan : %s" % pre_plan)
        for element in pre_plan:
            clef, valeur = element.split("=")
            typeElement, idElement = clef[:-1].split("[")
            dicoplan[idElement] = valeur

        def getParentPlan(idElement):
            parent = dicoplan[idElement]
            if parent == "course_plan-plan":
                return {"idElement": "racine", "listeElement": plan}
            else:
                racine = getParentPlan(parent)
                return {"idElement": racine["listeElement"][-1]["idElement"], "listeElement": racine["listeElement"][-1]["listeElement"]}

        dicoElements = self.getCourseItemProperties()
        # LOG.info("***** dicoElements : %s" % dicoElements)
        for element in pre_plan:
            clef, valeur = element.split("=")
            typeElement, idElement = clef[:-1].split("[")
            infosElement = dicoElements[idElement]
            infosElement = dicoElements[idElement]
            isAfficherElement = self.isAfficherElement(infosElement["affElement"], infosElement["masquerElement"])["val"]

            p = getParentPlan(idElement)
            if typeElement == "branch":
                p["listeElement"].append({"idElement": idElement, "listeElement": []})
            else:
                p["listeElement"].append({"idElement": idElement})
            if p["idElement"] != "racine":
                pInfosElement = self.getCourseItemProperties(p["idElement"])
                isPAfficherElement = self.isAfficherElement(pInfosElement["affElement"], pInfosElement["masquerElement"])["val"]
                if isAfficherElement and not isPAfficherElement:
                    if typeElement == "branch":
                        self.editCourseTitleVisibility(idElement, DateTime(), "masquerElement")
                    else:
                        self.editCourseItemVisibility(idElement, DateTime(), "masquerElement")

            """
            if typeElement == "branch":
                p = getParentPlan(idElement)
                if p["idElement"] != "racine":
                    pInfosElement = self.getCourseItemProperties(p["idElement"])
                    isPAfficherElement = self.isAfficherElement(pInfosElement["affElement"], pInfosElement["masquerElement"])["val"]
                    if isAfficherElement and not isPAfficherElement:
                        self.editCourseTitleVisibility(idElement, DateTime(), "masquerElement")
                p["listeElement"].append({"idElement": idElement, "listeElement": []})
            else:
                p = getParentPlan(idElement)
                if p["idElement"] != "racine":
                    pInfosElement = self.getCourseItemProperties(p["idElement"])
                    isPAfficherElement = self.isAfficherElement(pInfosElement["affElement"], pInfosElement["masquerElement"])["val"]
                    if isAfficherElement and not isPAfficherElement:
                        self.editCourseItemVisibility(idElement, DateTime(), "masquerElement")
                p["listeElement"].append({"idElement": idElement})
            """

        self.plan = tuple(plan)
        self.setCourseProperties({"DateDerniereModif": DateTime()})
        # return self.getPlanCours(True)

    def isAfficherElement(self, affElement, masquerElement):
        # LOG.info("----- isAfficherElement -----")
        return jalon_utils.isAfficherElement(affElement, masquerElement)

    def getCourseMapItemJalonner(self):
        # LOG.info("----- getCourseMapItemJalonner -----")
        item_jalonner = {"item_jalonner_id":      "",
                         "item_jalonner_comment": ""}
        if len(self.getAvancementPlan()):
            item_jalonner["item_jalonner_id"] = self.getAvancementPlan()[0]
            try:
                item_jalonner_comment = self.getAvancementPlan()[1]
                item_jalonner["item_jalonner_comment"] = item_jalonner_comment.replace("'", "’")
            except:
                item_jalonner["item_jalonner_comment"] = "Élément jalonné par l&rsquo;enseignant"
        return item_jalonner

    def getItemActions(self, item_properties, is_display_item_bool):
        """Fournit la liste des actions possibles pour l'item "item_properties"."""
        # LOG.info("----- getItemActions -----")
        item_actions = self._item_actions[:]

        if is_display_item_bool:
            del item_actions[0]
        else:
            del item_actions[1]

        if item_properties["typeElement"] in ["BoiteDepot", "AutoEvaluation", "Examen", "Titre", "TexteLibre"]:
            # Retire l'option "détacher"
            del item_actions[-2]
        else:
            # Retire l'option "supprimer"
            del item_actions[-1]

        if item_properties["typeElement"] in ["AutoEvaluation", "Examen"]:
            # Retire l'option "supprimer"
            del item_actions[-1]

        return item_actions

    def getCourseMapForm(self):
        # LOG.info("----- getCourseMapForm -----")
        return self.restrictedTraverse("cours/%s/%s/course_map_form" % (self.aq_parent.getId(), self.getId()))()

    def getCourseMapList(self, liste=None):
        # LOG.info("----- getCourseMapList -----")
        plat = []
        if liste is None:
            liste = list(self.plan)
            if not liste:
                return []
        for titre in liste:
            plat.append(titre["idElement"])
            if "listeElement" in titre:
                plat.extend(self.getCourseMapList(titre["listeElement"]))
        return plat

    def isInCourseMap(self, idElement, listeElement=None):
        # LOG.info("----- getCourseMapList -----")
        if not listeElement:
            listeElement = self.getCourseMapList()
        if idElement in listeElement:
            return 1
        return 0

    def getCourseAddActivityForm(self, activity_type):
        # LOG.info("----- getCourseAddActivityForm -----")
        return self._activity_dict[activity_type]["activity_title"]

    def readCourseMapItem(self, item_id):
        # LOG.info("----- readCourseMapItem -----")
        item_properties = self.getCourseItemProperties(item_id)
        user_id = self.portal_membership.getAuthenticatedMember().getId()
        if "marque" in item_properties:
            if user_id not in item_properties["marque"]:
                item_properties["marque"].append(user_id)
            else:
                item_properties["marque"].remove(user_id)
        else:
            item_properties["marque"] = [user_id]
        self._elements_cours[item_id] = item_properties
        self.setCourseItemsProperties(self._elements_cours)

    def getMarkOutCourseMapItemForm(self, item_id):
        # LOG.info("----- getMarkOutCourseMapItemForm -----")
        item_properties = self.getCourseItemProperties(item_id)
        return {"form_title":         self.getPlainShortText(item_properties['titreElement'], 80),
                "is_visible_item":    self.isAfficherElement(item_properties["affElement"], item_properties["masquerElement"])["val"],
                "mark_out_item_text": self.getCommentaireEpingler(item_id)}

    def getDisplayItemForm(self, item_id):
        """Fournit les infos du formulaire d'affichage/masquage d'un element "item_id" directement inclus dans le cours."""
        # LOG.info("----- getDisplayItemForm -----")
        item_properties = self.getCourseItemProperties(item_id)
        form_properties = self.getDisplayItemFormProperties(item_properties)

        item_parent_properties = self.getParentPlanElement(item_id, "racine", "")
        if item_parent_properties["idElement"] != "racine":
            display_parent_properties = self.isAfficherElement(item_parent_properties["affElement"], item_parent_properties["masquerElement"])
            if not display_parent_properties["val"]:
                form_properties["is_item_parent_title"] = True
                form_properties["item_parent_title_id"] = item_parent_properties["idElement"]
                form_properties["item_parent_title"] = item_parent_properties["titreElement"]

        if item_properties["typeElement"] in ["AutoEvaluation", "Examen"]:
            form_properties["is_delay_allowed"] = False
            is_authorized_activity = getattr(self, item_id).autoriser_Affichage()
            if not is_authorized_activity["val"]:
                form_properties["is_display_allowed"] = False
                form_properties["help_css"] = "panel warning radius"
                if is_authorized_activity["reason"] == "listeExos":
                    form_properties["help_text"] = "Vous ne pouvez pas afficher un entrainement ou un examen tant que sa liste d'exercices est vide."
                else:
                    form_properties["help_text"] = "Vous ne pouvez pas afficher cette ressource. %s" % is_authorized_activity["reason"]
        return form_properties

    def getDisplayItemFormProperties(self, item_properties):
        """Fournit les infos du formulaire d'affichage/masquage a partir des "item_properties" fournies."""
        form_properties = {"is_item_title":            False,
                           "is_item_parent_title":     False,
                           "help_css":                 "panel callout radius",
                           "help_text":                "Vous êtes sur le point d'afficher cette ressource à vos étudiants.",
                           "wims_help_text":           "",
                           "is_display_allowed":       True,
                           "is_delay_allowed":         True}

        display_properties = self.isAfficherElement(item_properties["affElement"], item_properties["masquerElement"])
        if display_properties["val"]:
            form_properties["help_text"] = _(u"Vous êtes sur le point de masquer cette ressource à vos étudiants.")
            form_properties["help_css"] = "panel radius warning"
            form_properties["form_button_css"] = "button small radius warning"
            form_properties["form_button_directly_text"] = _(u"Masquer l'élément maintenant")
            form_properties["form_button_lately_text"] = _(u"Programmer le masquage de l'élément à l'instant choisi")
            form_properties["item_property_name"] = "masquerElement"
            if item_properties["typeElement"] == "TexteLibre":
                form_properties["form_title_text"] = "Masquer l'élément : %s" % self.getPlainShortText(item_properties["titreElement"], 80)
            else:
                form_properties["form_title_text"] = "Masquer l'élément : %s" % item_properties["titreElement"]
            form_properties["form_title_icon"] = "fa fa-eye-slash no-pad"
            form_properties["item_parent_title"] = ""

            form_properties["text_title_lately"] = _(u"… ou programmer son masquage.")
            if item_properties["typeElement"] == "Titre":
                form_properties["is_item_title"] = True
                form_properties["text_title_directly"] = _(u"Masquer directement le titre / sous titre et son contenu…")
            else:
                form_properties["text_title_directly"] = _(u"Masquer directement…")

            form_properties["form_name"] = "masquer-element"
            form_properties["item_date"] = self.getFormattedDate(item_properties["masquerElement"])
        else:
            form_properties["form_button_css"] = "button small radius"
            form_properties["form_button_directly_text"] = _(u"Afficher l'élément maintenant")
            form_properties["form_button_lately_text"] = _(u"Programmer l'affichage de l'élément à l'instant choisi")
            form_properties["item_property_name"] = "affElement"
            if item_properties["typeElement"] == "TexteLibre":
                form_properties["form_title_text"] = "Afficher l'élément : %s" % self.getPlainShortText(item_properties["titreElement"], 80)
            else:
                form_properties["form_title_text"] = "Afficher l'élément : %s" % item_properties["titreElement"]
            form_properties["form_title_icon"] = "fa fa-eye no-pad"

            form_properties["text_title_lately"] = _(u"… ou programmer son affichage.")
            if item_properties["typeElement"] == "Titre":
                form_properties["is_item_title"] = True
                form_properties["text_title_directly"] = _(u"Afficher directement le titre / sous titre et son contenu…")
                form_properties["wims_help_text"] = "<strong><i class=\"fa fa-warning\"></i>Attention :</strong> les autoévaluations et examens vides ne seront pas affichés avec le titre."
            else:
                form_properties["text_title_directly"] = _(u"L'afficher directement…")
                if item_properties["typeElement"] == "Examen":
                    form_properties["wims_help_text"] = "<strong><i class=\"fa fa-warning\"></i>Attention :</strong> vous allez activer votre examen, il ne pourra plus être modifié."

            form_properties["form_name"] = "afficher-element"
            form_properties["item_date"] = self.getFormattedDate(item_properties["affElement"])

        return form_properties

    def editAllCourseMapVisibility(self, display_or_hide):
        """Edit All Course Map Visibility."""
        # LOG.info("----- editAllCourseMapVisibility -----")
        item_date = DateTime()
        item_property_name = "affElement" if display_or_hide == "display" else "masquerElement"
        for item_id in self.getCourseMapList():
            item_id_start = item_id.split("-")[0]
            context_object = getattr(self, item_id) if item_id_start in ["BoiteDepot", "AutoEvaluation", "Examen"] else self
            context_object.editCourseItemVisibility(item_id, item_date, item_property_name)

    def editCourseTitleVisibility(self, item_id, item_date, item_property_name, items_list=None):
        """Edit the Visibility of a Course Title and all its contents ."""
        # LOG.info("----- editCourseTitleVisibility (item_id = %s)-----" % item_id)
        actuality_code = "chapdispo" if item_property_name == "affElement" else ""

        if actuality_code:
            self.updateActualities(item_id, item_date, actuality_code)

        if items_list is None:
            items_list = list(self.getPlan())

        for item in items_list:
            if item["idElement"] == item_id or item_id == "all":
                # on commence par modifier le chapitre lui-même
                self.editCourseItemVisibility(item["idElement"], item_date, item_property_name, True)
                if "listeElement" in item:
                    # puis on modifie ses sous-elements
                    for sub_item in item["listeElement"]:
                        item_type_from_id = sub_item["idElement"].split("-")[0]
                        if item_type_from_id in ["BoiteDepot", "AutoEvaluation", "Examen"]:
                            context_object = getattr(self, sub_item["idElement"])
                        else:
                            context_object = self
                        context_object.editCourseItemVisibility(sub_item["idElement"], item_date, item_property_name, True)
                        if "listeElement" in sub_item:
                            # Si un des éléments est un sous-chapitre, on affiche son contenu recursivement.
                            self.editCourseTitleVisibility("all", item_date, item_property_name, sub_item["listeElement"])
                # Lorsqu'on a trouvé le chapitre qu'on cherchait, plus besoin de continuer à parcourir le plan.
                if item["idElement"] == item_id:
                    break
            elif "listeElement" in item:
                self.editCourseTitleVisibility(item_id, item_date, item_property_name, item["listeElement"])

    def editCourseItemVisibility(self, item_id, item_date, item_property_name, is_update_from_title=False):
        u"""Modifie l'etat de la ressource quand on modifie sa visibilité ("attribut" fournit l'info afficher / masquer)."""
        # LOG.info("----- editCourseItemVisibility (item_id = %s)-----" % item_id)
        item_properties = self.getCourseItemProperties(item_id)

        # if item_properties["typeElement"] in ["BoiteDepot", "AutoEvaluation", "Examen"]:
        #    item_object = getattr(self, item_id)
        #    item_object.afficherRessource(item_id, item_date, item_property_name)

        update_actuality = False
        if item_property_name == "affElement":
            item_properties["masquerElement"] = ""
            if item_properties["typeElement"] in self._type_folder_my_space_dict:
                portal = self.portal_url.getPortalObject()
                portal_workflow = getToolByName(portal, "portal_workflow")
                course_state = portal_workflow.getInfoFor(self, "review_state", wf_id="jalon_workflow")
                if course_state == "published":
                    item_object = getattr(getattr(getattr(portal.Members, item_properties["createurElement"]), self._type_folder_my_space_dict[item_properties["typeElement"]]), item_id.replace("*-*", "."))
                    item_object_state = portal_workflow.getInfoFor(item_object, "review_state", wf_id="jalon_workflow")
                    if course_state != item_object_state:
                        portal_workflow.doActionFor(item_object, "publish", "jalon_workflow")

            if not is_update_from_title:
                update_actuality = True
                self.updateActualities(item_id, item_date, "dispo")
        else:
            self.deleteCourseActuality(item_id)

        item_properties[item_property_name] = item_date
        self._elements_cours[item_id] = item_properties
        self.setCourseItemsProperties(self._elements_cours)

        if not update_actuality:
            self.setCourseProperties({"DateDerniereModif": DateTime()})

    def editCourseParentTitleVisibility(self, item_parent_id, item_date):
        """Edit Course Parent Title Visibility."""
        # LOG.info("----- editCourseParentTitleVisibility (item_parent_id = %s) -----" % item_parent_id)
        item_properties = self.getCourseItemProperties(item_parent_id)

        item_properties["affElement"] = item_date
        item_properties["masquerElement"] = ""
        self._elements_cours[item_parent_id] = item_properties
        self.setCourseItemsProperties(self._elements_cours)

        item_parent = self.getParentPlanElement(item_parent_id, 'racine', '')
        if item_parent["idElement"] == "racine":
            self.updateActualities(item_parent_id, item_date, "chapdispo")
        else:
            self.editCourseParentTitleVisibility(item_parent["idElement"], item_date)

    def updateActualities(self, item_id, item_date, actuality_code):
        """Update Actualities."""
        # LOG.info("----- updateActualities -----")
        actualities_list = list(self.getActualites())
        actuality_dict = {"reference":      item_id,
                          "dateActivation": item_date,
                          "code":           actuality_code,
                          "nb":             0,
                          "dateDepot":      None,
                          "acces":          ["auteurs", "etudiants"]}
        if actuality_dict not in actualities_list:
            self.setActuCours(actuality_dict)

    def getParentPlanElement(self, idElement, idParent, listeElement):
        # LOG.info("----- getParentPlanElement -----")
        if idParent == "racine":
            listeElement = self.plan
        # LOG.info("***** listeElement : %s" % str(listeElement))
        for element in listeElement:
            if idElement == element["idElement"]:
                if idParent == "racine":
                    return {"idElement": "racine", "affElement": "", "masquerElement": ""}
                else:
                    dico = dict(self.getCourseItemProperties(idParent))
                    dico["idElement"] = idParent
                    return dico
            elif "listeElement" in element:
                retour = self.getParentPlanElement(idElement, element["idElement"], element["listeElement"])
                if retour:
                    return retour
        return None

    def getEnfantPlanElement(self, idElement, listeElement=None):
        # LOG.info("----- getEnfantPlanElement -----")
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

    def addMySpaceItem(self, folder_object, item_id, item_type, user_id, display_item, map_position, display_in_plan, portal_workflow):
        # LOG.info("----- addMySpaceItem -----")
        item_id_no_dot = item_id.replace(".", "*-*")
        if self.isInCourseMap(item_id_no_dot):
            return None

        item_object = getattr(folder_object, item_id)

        if display_item:
            cours_state = portal_workflow.getInfoFor(self, "review_state", wf_id="jalon_workflow")
            if cours_state == "published":
                objet_state = portal_workflow.getInfoFor(item_object, "review_state", wf_id="jalon_workflow")
                if cours_state != objet_state:
                    portal_workflow.doActionFor(item_object, "publish", "jalon_workflow")

        item_object_related = item_object.getRelatedItems()
        if self not in item_object_related:
            item_object_related.append(self)
            item_object.setRelatedItems(item_object_related)
            item_object.reindexObject()

        course_related = self.getRelatedItems()
        if item_object not in course_related:
            course_related.append(item_object)
            self.setRelatedItems(course_related)

        complement_element = None
        if item_type in ["Video", "VOD"]:
            complement_element = {"value":       display_in_plan,
                                  "auteur":      item_object.getVideoauteurname(),
                                  "image":       item_object.getVideothumbnail(),
                                  "description": item_object.Description()}

        self.addItemInCourseMap(item_id_no_dot, map_position)
        self.addItemProperty(item_id_no_dot, item_type, item_object.Title(), user_id, display_item, complement_element)

    def addItemInCourseMap(self, item_id, map_position):
        # LOG.info("----- addItemInCourseMap -----")
        course_map = list(self.getPlan())

        item_properties = {"idElement": item_id, "listeElement": []} if item_id.startswith("Titre") else {"idElement": item_id}

        if map_position == "debut_racine":
            course_map.insert(0, item_properties)
        elif map_position == "fin_racine":
            course_map.append(item_properties)
        else:
            course_title_list = map_position.split("*-*")
            self.setCourseMapPosition(item_id, item_properties, course_map, course_title_list[1:])

        self.plan = tuple(course_map)

    def addMySpaceItemGlossary(self, folder_object, item_id, item_type, user_id):
        # LOG.info("----- addMySpaceItemGlossary -----")
        glossary = list(self.getGlossaire())
        glossary.append(item_id)
        self.setElements_glossaire(glossary)

        item_object = getattr(folder_object, item_id)

        item_object_related = item_object.getRelatedItems()
        if self not in item_object_related:
            item_object_related.append(self)
            item_object.setRelatedItems(item_object_related)
            item_object.reindexObject()

        course_related = self.getRelatedItems()
        if item_object not in course_related:
            course_related.append(item_object)
            self.setRelatedItems(course_related)

        self.addItemProperty(item_id, item_type, item_object.Title(), user_id, "", None)

    def addMySpaceItemBibliography(self, folder_object, item_id, item_type, user_id):
        # LOG.info("----- addMySpaceItemBibliography -----")
        bibliography = list(self.getBibliographie())
        bibliography.append(item_id)
        self.setElements_bibliographie(bibliography)

        item_object = getattr(folder_object, item_id)

        item_object_related = item_object.getRelatedItems()
        if self not in item_object_related:
            item_object_related.append(self)
            item_object.setRelatedItems(item_object_related)
            item_object.reindexObject()

        course_related = self.getRelatedItems()
        if item_object not in course_related:
            course_related.append(item_object)
            self.setRelatedItems(course_related)

        item_data = self.getCourseItemProperties().get(item_id)
        if not item_data:
            self.addItemProperty(item_id, item_type, item_object.Title(), user_id, "", None)

    def setCourseMap(self, plan):
        # LOG.info("----- setCourseMap -----")
        self.plan = tuple(plan)

    def setCourseMapPosition(self, item_id, item_properties, items_list, course_title_list):
        # LOG.info("----- setCourseMapPosition -----")
        if len(course_title_list) > 1:
            for item in items_list:
                if item["idElement"] == course_title_list[0]:
                    self.setCourseMapPosition(item_id, item_properties, item["listeElement"], course_title_list[1:])
        else:
            for item in items_list:
                if item["idElement"] == course_title_list[0]:
                    item["listeElement"].append(item_properties)
                    break

    def addItemProperty(self, item_id, item_type, item_title, item_creator, display_item, complement_element):
        # LOG.info("----- addItemProperty -----")
        parent = self.getParentPlanElement(item_id, 'racine', '')
        # LOG.info("***** parent : %s" % str(parent))
        if parent and parent['idElement'] != 'racine':
            is_display_parent = self.isAfficherElement(parent['affElement'], parent['masquerElement'])
            # LOG.info("***** is_display_parent : %s" % str(is_display_parent))
            if not is_display_parent['val']:
                display_item = ""

        items_properties = self.getCourseItemProperties()
        if item_id not in items_properties:
            items_properties[item_id] = {"titreElement":    item_title,
                                         "typeElement":     item_type,
                                         "createurElement": item_creator,
                                         "affElement":      display_item,
                                         "masquerElement":  ""}
            if display_item:
                dicoActu = {"reference":      item_id,
                            "code":           "dispo",
                            "dateActivation": display_item}
                self.setActuCours(dicoActu)

            if complement_element:
                items_properties[item_id]["complementElement"] = complement_element
            self.setCourseItemsProperties(items_properties)

    def addCourseActivity(self, user_id, activity_type, activity_title, activity_description, map_position):
        """Ajoute une activité dans le cours."""
        # LOG.info("----- addCourseActivity -----")
        activity_dict = self._activity_dict[activity_type]
        activity_id = self.invokeFactory(type_name=activity_dict["activity_portal_type"], id="-".join([activity_dict["activity_id"], user_id, DateTime().strftime("%Y%m%d%H%M%S%f")]))

        activity = getattr(self, activity_id)
        activity.setProperties({"Title":       activity_title,
                                "Description": activity_description})

        self.addItemInCourseMap(activity_id, map_position)
        self.addItemProperty(activity_id, activity_dict["activity_id"], activity_title, user_id, "", None)
        return activity_id

    def detachCourseItem(self, item_id, item_creator, folder_id):
        # LOG.info("----- detachCourseItem ----- %s" % item_id)

        item_object = getattr(getattr(getattr(self.portal_url.getPortalObject().Members, item_creator), self._type_folder_my_space_dict[folder_id]), item_id)
        item_relatedItems = item_object.getRelatedItems()
        try:
            item_relatedItems.remove(self)
            item_object.setRelatedItems(item_relatedItems)
            item_object.reindexObject()
        except:
            pass

        try:
            course_relatedItems = self.getRelatedItems()
            course_relatedItems.remove(item_object)
            self.setRelatedItems(course_relatedItems)
        except:
            pass

        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def modifierInfosBoitePlan(self, idElement, param):
        # LOG.info("----- modifierInfosBoitePlan -----")
        dico = self.getCourseItemProperties(idElement)
        for attribut in param.keys():
            dico[attribut] = param[attribut]
        self._elements_cours[idElement] = dico
        self.setCourseItemsProperties(self._elements_cours)
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def editCourseMapItem(self, item_id, item_title, display_item_in_course_map):
        """Modifie le titre d'un element existant du plan de cours."""
        # LOG.info("----- editCourseMapItem -----")
        item_properties = self.getCourseItemProperties(item_id)

        if "titreElementMonEspace" not in item_properties:
            item_properties["titreElementMonEspace"] = item_properties["titreElement"][:]

        if item_title == "":
            item_properties["titreElement"] = item_properties["titreElementMonEspace"][:]
        else:
            item_properties["titreElement"] = item_title

        if display_item_in_course_map:
            item_properties["complementElement"]["value"] = True
        else:
            try:
                item_properties["complementElement"]["value"] = False
            except:
                pass

        self._elements_cours[item_id] = item_properties
        self.setCourseItemsProperties(self._elements_cours)

    def ordonnerElementPlan(self, pplan):
        # LOG.info("----- ordonnerElementPlan -----")
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

        dicoElements = self.getCourseItemProperties()
        for element in pre_plan:
            clef, valeur = element.split("=")
            typeElement, idElement = clef[:-1].split("[")
            infosElement = dicoElements[idElement]
            isAfficherElement = self.isAfficherElement(infosElement["affElement"], infosElement["masquerElement"])["val"]
            if typeElement == "chapitre":
                p = getParentPlan(idElement)
                if p["idElement"] != "racine":
                    pInfosElement = self.getCourseItemProperties(p["idElement"])
                    isPAfficherElement = self.isAfficherElement(pInfosElement["affElement"], pInfosElement["masquerElement"])["val"]
                    if isAfficherElement and not isPAfficherElement:
                        self.afficherRessourceChapitre(idElement, DateTime(), "masquerElement")
                p["listeElement"].append({"idElement": idElement, "listeElement": []})
            else:
                p = getParentPlan(idElement)
                if p["idElement"] != "racine":
                    pInfosElement = self.getCourseItemProperties(p["idElement"])
                    isPAfficherElement = self.isAfficherElement(pInfosElement["affElement"], pInfosElement["masquerElement"])["val"]
                    if isAfficherElement and not isPAfficherElement:
                        self.afficherRessource(idElement, DateTime(), "masquerElement")
                p["listeElement"].append({"idElement": idElement})

        self.plan = tuple(plan)
        self.setCourseProperties({"DateDerniereModif": DateTime()})
        return self.getPlanCours(True)

    def retirerElement(self, idElement):
        # LOG.info("----- retirerElement -----")
        elements_glossaire = list(self.getGlossaire())
        if idElement in elements_glossaire:
            elements_glossaire.remove(idElement)
            self.elements_glossaire = tuple(elements_glossaire)
            infos_element = self.getCourseItemProperties()
            infosElement = infos_element[idElement]
            self.detachCourseItem(idElement, infosElement["createurElement"], infosElement["typeElement"].replace(" ", ""))
            del infos_element[idElement]
        elements_bibliographie = list(self.getBibliographie())
        if idElement in elements_bibliographie:
            elements_bibliographie.remove(idElement)
            self.elements_bibliographie = tuple(elements_bibliographie)
            if not self.isInCourseMap(idElement):
                infos_element = self.getCourseItemProperties()
                infosElement = infos_element[idElement]
                self.detachCourseItem(idElement, infosElement["createurElement"], infosElement["typeElement"].replace(" ", ""))
                del infos_element[idElement]
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def deleteCourseMapItem(self, idElement, listeElement=None, force_WIMS=False):
        # LOG.info("----- deleteCourseMapItem %s %s-----" % (idElement, listeElement))
        # LOG.info("***** item_id : %s" % idElement)
        """ Fonction recursive qui supprime l'element idElement du plan, ainsi que tout son contenu si c'est un Titre."""
        # anciennement "retirerElementPlan"
        start = False
        if listeElement is None:
            listeElement = list(self.getPlan())
            start = True
        for element in listeElement[:]:
            # LOG.info("FOR : %s" % element)
            # LOG.info("1 listeElement : %s" % listeElement)
            if element["idElement"] == idElement or idElement == "all":
                # Si element contient lui-même une liste d'elements, on appelle a nouveau cette fonction
                #   avec le parametre "all" et la liste des elements a supprimer
                if "listeElement" in element and element["listeElement"] != []:
                    self.deleteCourseMapItem("all", element["listeElement"], force_WIMS)

                # On supprime element de la liste où il etait dans le plan
                while element in listeElement:
                    # LOG.info("remove : %s" % element)
                    listeElement.remove(element)
                # LOG.info("2 listeElement : %s" % listeElement)

                infosElement = self.getCourseItemProperties().get(element["idElement"])

                if infosElement:
                    # Dans le cas des activités WIMS, on ne supprime pas l'element du plan, on ne fait que le déplacer
                    if infosElement["typeElement"] in ["AutoEvaluation", "Examen"] and force_WIMS is False:
                        self.addItemInCourseMap(element["idElement"], "fin_racine")
                    elif not (element["idElement"] in self.getGlossaire() or element["idElement"] in self.getBibliographie()):
                        # Si ce n'est pas un element Biblio ou Glossaire, on le supprime des objets du cours
                        del self._elements_cours[element["idElement"]]
                        self.setCourseItemsProperties(self._elements_cours)

                    if infosElement["typeElement"] not in ["Titre", "TexteLibre", "AutoEvaluation", "Examen", "BoiteDepot", "Forum", "SalleVirtuelle"]:
                        if (not infosElement["typeElement"].replace(" ", "") in ["Lienweb", "Lecteurexportable", "CatalogueBU"]) or (not idElement in list(self.getBibliographie())):
                            self.detachCourseItem(element["idElement"].replace("*-*", "."), infosElement["createurElement"], infosElement["typeElement"].replace(" ", ""))

                    if infosElement["typeElement"] == "BoiteDepot":
                        boite = getattr(self, element["idElement"])
                        boite.detachAllDocuments()

                    if (infosElement["typeElement"] in ["Forum", "BoiteDepot"]) or (force_WIMS is True and infosElement["typeElement"] in ["AutoEvaluation", "Examen"]):
                        self.manage_delObjects([element["idElement"]])
                # LOG.info("3 listeElement : %s" % listeElement)
            elif "listeElement" in element:
                # LOG.info("***** parent item_id : %s" % element["idElement"])
                # Si on tombe sur un titre, on vérifie alors qu'il ne contient pas idElement
                self.deleteCourseMapItem(idElement, element["listeElement"], force_WIMS)
            # LOG.info("4 listeElement : %s" % listeElement)

        if start:
            self.plan = tuple(listeElement)
        return listeElement

    def detachGlossaryItem(self, item_id):
        # LOG.info("----- detachGlossaryItem -----")
        elements_glossaire = list(self.getGlossaire())
        if item_id in elements_glossaire:
            elements_glossaire.remove(item_id)
            self.elements_glossaire = tuple(elements_glossaire)
            item_data = self.getCourseItemProperties().get(item_id)
            if item_data:
                del self._elements_cours[item_id]
                self.setCourseItemsProperties(self._elements_cours)
            self.detachCourseItem(item_id, item_data["createurElement"], item_data["typeElement"].replace(" ", ""))

    def detachBibliographyItem(self, item_id):
        # LOG.info("----- detachBibliographyItem -----")
        bibliography_items = list(self.getBibliographie())
        if item_id in bibliography_items:
            bibliography_items.remove(item_id)
            self.elements_bibliographie = tuple(bibliography_items)
            if not self.isInCourseMap(item_id):
                item_data = self.getCourseItemProperties().get(item_id)
                if item_data:
                    del self._elements_cours[item_id]
                    self.setCourseItemsProperties(self._elements_cours)
                self.detachCourseItem(item_id, item_data["createurElement"], item_data["typeElement"].replace(" ", ""))

    def getCourseDeleteItemForm(self, item_id):
        # LOG.info("----- getCourseDeleteItemForm -----")
        item_properties = self.getCourseItemProperties(item_id)
        form_properties = copy.deepcopy(self._course_delete_item_form[item_properties["typeElement"]])
        """
        Rétro-compatibilité avec l'existant
        (présence possible de HTML dans les titres des éléments "titres").
        """
        if item_properties["typeElement"] in ["Titre", "TexteLibre"]:
            form_properties["item_short_title"] = self.getPlainShortText(
                item_properties['titreElement'], 80)
        else:
            form_properties["item_short_title"] = self.getShortText(
                item_properties['titreElement'], 80)
        """
        À remplacer par ce qui suit si une migration permettant de supprimer
        tout marquage HTML dans les titres est effectuée.

        if item_properties["typeElement"] == "TexteLibre":
            form_properties["item_short_title"] = self.getPlainShortText(
                item_properties['titreElement'], 80)
        else:
            form_properties["item_short_title"] = self.getShortText(
                item_properties['titreElement'], 80)

        """
        return form_properties

    def verifType(self, typeElement):
        # LOG.info("----- verifType -----")
        return typeElement.replace(" ", "")

    def isStreamingAuthorized(self, streaming_id, request):
        # LOG.info("----- isStreamingAuthorized -----")
        if not request.has_key("HTTP_X_REAL_IP"):
            return False
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        return portal_jalon_wowza.isStreamingAuthorized(streaming_id, request["HTTP_X_REAL_IP"])

    def delElem(self, element):
        # LOG.info("----- ----- delElem -----")
        del self._elements_cours[element]
        self.getCourseItemProperties()
        self.setCourseItemsProperties(self._elements_cours)

    def get_id_from_filename(self, filename, context):
        return jalon_utils.get_id_from_filename(filename, context)

    # --------------------------------- #
    #  Course Activity (Boite dépôts)   #
    # --------------------------------- #
    def purgerDepots(self):
        # LOG.info("----- purgerDepots -----")
        for boite in self.objectValues("JalonBoiteDepot"):
            boite.purgerDepots()
            boite.setPeersDict({})
            boite.setCompEtudiants({})
            boite.reindexObject()
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def deleteDepositBox(self):
        # LOG.info("----- deleteDepositBox -----")
        for item_id in self.objectIds():
            if item_id.startswith("BoiteDepot-"):
                deposit_box = getattr(self, item_id)
                deposit_box.detachAllDocuments()

    # --------------------------------- #
    #  Course Activity (WIMS Activity)  #
    # --------------------------------- #
    def setListeClasses(self, valeur):
        # LOG.info("----- setListeClasses -----")
        self.listeclasses = tuple(valeur)

    def authUser(self, quser=None, qclass=None, request=None):
        # LOG.info("----- authUser -----")
        return jalon_utils.authUser(self, quser, qclass, request)

    def getDataCourseWimsActivity(self, user_id, course_id):
        # LOG.info("----- getDataCourseWimsActivity -----")
        wims_classes_list = self.getListeClasses()
        can_delete = True if wims_classes_list and (user_id in wims_classes_list[0] or self.isAuteur(user_id)) else False

        course_author_data = self.getAuteur()

        # [TODO] à finir : ne tient pas compte de si pas d'annuaire LDAP
        record_user_book_base = self.useJalonUtils("getBaseAnnuaire", {})
        course_author_record_user_link = self.useJalonUtils("getFicheAnnuaire", {"valeur": course_author_data,
                                                                                 "base":   record_user_book_base})

        is_course_author = self.isAuteur(user_id)
        can_delete_all_wims_classes_css = "" if is_course_author else "disabled"

        return {"course_name":                     self.getShortText(self.Title(), 80),
                "is_course_owner":                 self.isCourseOwner(user_id),
                "wims_classe_list":                wims_classes_list,
                "can_delete":                      can_delete,
                "course_author_fullname":          course_author_data["fullname"],
                "course_author_record_user_link":  course_author_record_user_link,
                "is_course_author":                is_course_author,
                "can_delete_all_wims_classes_css": can_delete_all_wims_classes_css}

    def purgerActivitesWims(self):
        # LOG.info("----- purgerActivitesWims -----")
        u"""Supprime l'ensemble des travaux effectués dans toutes les activités Wims d'un cours."""
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

    def getScoresWims(self, auteur, authMember, request=None, file_format="csv"):
        u"""Liste (pour téléchargement) les notes de tous les examens WIMS créées par 'auteur' dans le cours."""
        # LOG.info("[----- getScoresWims -----")
        dicoClasses = list(self.getListeClasses())[0]

        separators = {"csv": ",",
                      "tsv": "\t",
                      "xls": ";"}

        liste_activitesWIMS = []

        for idElement in self.objectIds():

            if (idElement.startswith("AutoEvaluation") or idElement.startswith("Examen")):
                activite = getattr(self, idElement)

                if auteur == "All" or activite.getCreateur() == auteur:
                    if activite.typeWims == "Examen":
                        if activite.idExam:
                            # On ne demande que les examens créés coté WIMS
                            liste_activitesWIMS.append("exam%s" % activite.getIdExam())
                    elif activite.isActif():
                        # Pour les feuilles, on ne demande que les actives.
                        liste_activitesWIMS.append("sheet%s" % activite.getIdFeuille())
        retour = {}
        if len(liste_activitesWIMS) > 0:
            # LOG.info("----- [getScoresWims] listeClasses :'%s'" % listeClasses)
            # for user in dicoClasses:
            #    if auteur == "All" or user == auteur:
            columns = "login,name,%s" % (",".join(liste_activitesWIMS))
            if auteur in dicoClasses:
                dico = {"qclass": dicoClasses[auteur],
                        "code": authMember,
                        "job": "getcsv",
                        "format": file_format,
                        "option": columns}
                # LOG.info("----- [getScoresWims] callJob dico :'%s'" % dico)
                rep_wims = self.wims("callJob", dico)

                try:
                    # Si json arrive a parser la reponse, c'est une erreur. WIMS doit être indisponible.
                    retour = json.loads(rep_wims)
                    self.plone_log("[jaloncours/getScoresWims] ERREUR WIMS / retour = %s" % retour)
                    # Une des erreurs possible, c'est un trop grand nombre :
                    # * d'eleves dans la classe (>400 ?)
                    # * d'activités dans la classe (>64 ?)
                    # * une combinaison des 2 ?
                    self.wims("verifierRetourWims", {"rep": rep_wims,
                                                     "fonction": "jaloncours.py/getScoresWims",
                                                     "message": "Impossible de télécharger les notes (demandeur = %s)" % authMember,
                                                     "jalon_request": request
                                                     })
                except:
                    # Si "fichier" n'est pas un JSON correct, ce doit bien etre un OEF.
                    if file_format == "xls":
                        # Pour le format xls, on remplace le séparateur décimal (.) par une virgule.
                        rep_wims = rep_wims.replace(".", ",")

                    # Ici on ajoute le numéro étudiant dans les colonnes :
                    listETU = []
                    file_lines = rep_wims.rstrip('\n').split('\n')
                    nb_entetes = 3

                    for line in file_lines[nb_entetes:]:
                        # On cree une liste de tous les identifiants
                        listETU.append(line.split(separators[file_format])[0].strip('"'))
                    # On demande toutes les infos disponibles pour la liste d'identifiants
                    dico_ETU = jalon_utils.getIndividus(listETU, type="dict")
                    export_file = []

                    for index, line in enumerate(file_lines):
                        if index >= nb_entetes:
                            id_etu = listETU[index - nb_entetes]
                            if id_etu in dico_ETU:
                                individu = dico_ETU[id_etu]
                                # user["first_name"] = individu["prenom"]
                                # user["last_name"]  = individu["nom"]
                                num_etu = "%s" % individu["num_etu"]
                            else:
                                num_etu = "Non disp."
                        elif index == 1:
                            num_etu = "Num. Etudiant"
                        else:
                            num_etu = "number"
                        if line != "":
                            export_file.append("%s%s%s" % (num_etu.encode("utf-8"), separators[file_format], line))

                    retour = {"status": "OK", "nb_activity": len(liste_activitesWIMS), "data": "\n".join(export_file)}

        else:
            retour = {"status": "not_relevant", "nb_activity": len(liste_activitesWIMS)}

        return retour

    def supprimerActivitesWims(self, utilisateur="All", request=None):
        # LOG.info("----- supprimerActivitesWims -----")
        u"""Suppression de toutes les activites WIMS du cours, créées par 'utilisateur'."""
        # Retire du plan toutes les activités de l'utilisateur "utilisateur"

        # Ici on utilise self.objectIds() plutot que getPlanPlat, afin de lister les objets réellement dans le cours.
        # Cela permet de prendre egalement d'éventuels elements mal supprimés qui sont toujours "la", mais plus dans le plan.

        liste_activitesWIMS = []

        for idElement in self.objectIds():

            if (idElement.startswith("AutoEvaluation") or idElement.startswith("Examen")):
                # self.plone_log("[jaloncours/supprimerActivitesWims] ACTIVITE :'%s'" % element)
                activite = getattr(self, idElement)

                if utilisateur == "All" or activite.getCreateur() == utilisateur:
                    # LOG.info("----- [jaloncours/supprimerActivitesWims] suppression de '%s'" % element)
                    liste_activitesWIMS.append(idElement)

                    # On parcourt ensuite les exo des activitées retirées, pour que chaque exercice n'y fasse plus référence dans ses "relatedITEMS"
                    # retire l'activité des relatedItems pour ses exercices et ses documents.
                    activite.removeAllElements(force_WIMS=True)

                    # Supprime l'activité (du plan du cours et du cours)
                    self.deleteCourseMapItem(idElement, force_WIMS=True)
                    # Supprime l'activité des actus du cours
                    self.deleteCourseActuality(idElement)

                    # ** A utiliser dans un patch correctif : **
                    # (on refait ce que fait normalement deleteCourseMapItem, dans le cas ou l'element n'est plus dans le plan mais toujours dans _elements_cours) :
                    if idElement in self._elements_cours:
                        self.manage_delObjects(idElement)
                        del self._elements_cours[idElement]

        # Supprime toutes les classes du serveur WIMS
        listeClasses = list(self.getListeClasses())
        removing_classes = []
        dico = listeClasses[0]
        # LOG.info("----- [jaloncours/supprimerActivitesWims] Ancienne liste :'%s'" % listeClasses)
        new_listeClasses = []
        for auteur in dico:
            if utilisateur == "All" or utilisateur == auteur:
                removing_classes.append(dico[auteur])
            else:
                if len(new_listeClasses) == 0:
                    new_listeClasses.append({auteur: dico[auteur]})
                else:
                    new_listeClasses[0][auteur] = dico[auteur]
        if removing_classes is not None:
            self.aq_parent.delClassesWims(removing_classes, request)

        # Et enfin remettre à zero la liste des classes du cours.
        # LOG.info("----- [jaloncours/supprimerActivitesWims] Nouvelle liste :'%s'" % new_listeClasses)
        self.setListeClasses(new_listeClasses)

        # Renvoit le nombre d'activités supprimées.
        return len(liste_activitesWIMS)

    """
    #def autoriserAffichageSousObjet(self, idElement, typeElement=None):
    #    à remplacer par
    #    getattr(self, item_id).autoriser_Affichage()

    # pour montrer les nouveaux éléments dans le cours
    #def isNouveau(self, idElement, listeActualites=None):
    #    à remplacer par
    #    True if item["is_display_item_bool"] and cmp(item_properties["affElement"], user_last_login_time) > 0 else False
    """

    # --------------------------------- #
    #  Course Activity (Adobe Connect)  #
    # --------------------------------- #
    def connect(self, methode, param):
        # LOG.info("----- connect -----")
        return self.portal_connect.__getattribute__(methode)(param)

    def getSessionConnect(self, user_id, repertoire):
        # LOG.info("----- getSessionConnect -----")
        portal = self.portal_url.getPortalObject()
        home = getattr(getattr(portal.Members, user_id), repertoire)
        return home.getSessionConnect(user_id)

    def getReunion(self, user_id, request, repertoire):
        # LOG.info("----- getReunion -----")
        portal = self.portal_url.getPortalObject()
        home = getattr(getattr(portal.Members, user_id), repertoire)
        return home.getReunion(user_id)

    def getDisplayCourseWebconference(self, webconference_id):
        # LOG.info("----- getDisplayCourseWebconference -----")
        item_properties = self.getCourseItemProperties(webconference_id)

        item = {"item_id":      webconference_id,
                "item_title":   item_properties["titreElement"],
                "item_link":    self.getWebconferenceUrlById(item_properties["createurElement"], webconference_id)}

        return item

    def getWebconferenceUrlById(self, authMember, webconference_id):
        #self.plone_log("getWebconferenceUrlById")
        for reunion in self.getWebconferencesUser(True, authMember, webconference_id):
            if reunion["id"] == webconference_id:
                return self.getUrlWebconference(reunion['url'])
        return ""

    def getWebconferencesUser(self, personnel, authMember, webconference_id=None):
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
            #actives = self.getWebconferences()
            reunionsCreator = self.connect("rechercherReunions", {"login": authMember, "modele": modele})
            if reunionsCreator:
                for webconference in reunionsCreator:
                    if webconference_id and webconference['id'] == webconference_id:
                        reunions.append(webconference)
                        break
                    elif not webconference_id:
                        reunions.append(webconference)
        return reunions

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

    #---------------------#
    # Course Participants #
    #---------------------#
    def getCourseTrainingOfferForm(self, user, training_offer_searh_type):
        form_properties = {"is_personnel": self.isPersonnel(user)}
        form_properties["training_offer_type"] = [{"training_offer_type_selected": "selected" if training_offer_searh_type == "etape" else "",
                                                   "training_offer_type_value":    "etape",
                                                   "training_offer_type_text":     "Diplôme"},
                                                  {"training_offer_type_selected": "selected" if training_offer_searh_type == "ue" else "",
                                                   "training_offer_type_value":    "ue",
                                                   "training_offer_type_text":     "Unité d'enseignement"},
                                                  {"training_offer_type_selected": "selected" if training_offer_searh_type == "uel" else "",
                                                   "training_offer_type_value":    "uel",
                                                   "training_offer_type_text":     "Unité d'enseignement libre"},
                                                  {"training_offer_type_selected": "selected" if training_offer_searh_type == "groupe" else "",
                                                   "training_offer_type_value":    "groupe",
                                                   "training_offer_type_text":     "Groupe"}]
        form_properties["training_offer_dict"] = self._training_offer_type
        form_properties["training_offer_list"] = self.getCourseTrainingOffer()
        return form_properties

    def getCourseTrainingOffer(self):
        # LOG.info("----- getCourseTrainingOffer -----")
        training_offer_list = []
        course_access_list = self.getListeAcces()
        portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
        for course_access in course_access_list:
            course_access_type, course_access_code = course_access.split("*-*")
            db_result = portal_jalon_bdd.getELPProperties(course_access_code)

            if not db_result:
                training_offer = {"LIB_ELP": "Le code %s n'est plus valide." % course_access_code,
                                  "COD_ELP": course_access_code,
                                  "TYP_ELP": "inconnu",
                                  "nb_etu": "0"}
            else:
                training_offer = db_result[0]
            training_offer_list.append(training_offer)
        # LOG.info("***** training_offer_list : %s" % str(training_offer_list))
        return training_offer_list

    def displayCourseTrainingOffer(self):
        # LOG.info("----- displayCourseTrainingOffer -----")
        return {"is_personnel":        False,
                "training_offer_dict": self._training_offer_type,
                "training_offer_list": self.getCourseTrainingOffer()}

    def searchTrainingOffer(self, training_offer_search_text, training_offer_search_type):
        # LOG.info("----- searchTrainingOffer -----")
        if not training_offer_search_text:
            return ""

        training_offer_search_text.strip()
        training_offer_search_text = "%" + training_offer_search_text + "%"
        training_offer_search_text = training_offer_search_text.replace(" ", "% %")
        training_offer_search_text_list = training_offer_search_text.split(" ")

        portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
        return portal_jalon_bdd.searchELP(training_offer_search_text_list, training_offer_search_type)

    def addCourseTrainingOffer(self, training_offer_list):
        # LOG.info("----- addCourseTrainingOffer -----")
        course_access_list = list(self.getListeAcces())
        for training_offer in training_offer_list:
            if not training_offer in course_access_list:
                course_access_list.append(training_offer)
        self.listeAcces = tuple(course_access_list)
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def deleteCourseTrainingOffer(self, training_offer_list):
        # LOG.info("----- deleteCourseTrainingOffer -----")
        self.listeAcces = tuple(training_offer_list)
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def getNominativeRegistration(self):
        # LOG.info("----- getNominativeRegistration -----")
        groupe = self.getGroupe()
        return jalon_utils.getIndividus(list(groupe), "listdict")

    def addNominativeRegistration(self, nominative_registration_list):
        # LOG.info("----- addNominativeRegistration -----")
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été inscrit au cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), self.absolute_url(), portal.Title())
        course_nominative_registration_list = list(self.getGroupe())
        for nominative_registration in nominative_registration_list:
            if not nominative_registration in course_nominative_registration_list:
                course_nominative_registration_list.append(nominative_registration)
                infosMembre = self.useJalonUtils("getIndividu", {"sesame": nominative_registration, "type": "dict"})
                self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                            "objet":   "Vous avez été inscrit à un cours",
                                                            "message": message}})
        self.setGroupe(tuple(course_nominative_registration_list))
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def deleteNominativeRegistration(self, nominative_registration_list):
        # LOG.info("----- deleteNominativeRegistration -----")
        course_nominative_registration_list = set(self.getGroupe())
        delete_nominative_registration_list = course_nominative_registration_list.difference(set(nominative_registration_list))
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été désinscrit du cours "%s" ayant pour auteur %s.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())
        for delete_nominative_registration in delete_nominative_registration_list:
            infosMembre = self.useJalonUtils("getIndividu", {"sesame": delete_nominative_registration, "type": "dict"})
            self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                        "objet":   "Vous avez été désincrit d'un cours",
                                                        "message": message}})
        self.setGroupe(tuple(nominative_registration_list))
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def editPasswordregistration(self, activate_password):
        # LOG.info("----- editPasswordregistration -----")
        if activate_password == "True" or not self.getLienMooc():
            part1 = ''.join([random.choice(string.ascii_lowercase) for i in range(3)])
            part2 = ''.join([random.choice(string.digits[1:]) for i in range(3)])
            part3 = ''.join([random.choice(string.ascii_uppercase) for i in range(3)])
            short = part1 + part2 + part3
            self.setLienMooc(short)
            self.setCourseProperties({"Categorie": ["2"]})
        else:
            self.setCourseProperties({"Categorie": ["1"]})

        self.setLibre(activate_password)
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def addPasswordStudent(self, member_id):
        # LOG.info("----- addPasswordStudent -----")
        if self.getLibre():
            inscriptionsLibres = list(self.getInscriptionsLibres())
            if not member_id in inscriptionsLibres:
                inscriptionsLibres.append(member_id)
                self.setCourseProperties({"InscriptionsLibres": inscriptionsLibres,
                                          "DateDerniereModif":  DateTime()})

    def deletePasswordStudent(self, password_students):
        # LOG.info("----- deletePasswordStudent -----")
        self.setCourseProperties({"InscriptionsLibres": password_students,
                                  "DateDerniereModif":  DateTime()})

    def getEmailRegistration(self):
        # LOG.info("----- getEmailregistration -----")
        course_email_registration_list = self.getInvitations()
        if not course_email_registration_list:
            return []
        email_registration_list = []
        portal_membership = getToolByName(self, "portal_membership")
        for email_registration in course_email_registration_list:
            username = email_registration
            member = portal_membership.getMemberById(username)
            if member:
                username = member.getProperty("fullname", username)
            email_registration_list.append({"nom": username, "email": email_registration})
        return email_registration_list

    def addEmailRegistration(self, email_registration_list):
        # LOG.info("----- addEmailRegistration -----")
        portal = self.portal_url.getPortalObject()
        portal_membership = getToolByName(portal, 'portal_membership')
        course_email_registration_list = list(self.getInvitations())
        for email_registration in email_registration_list:
            email_registration = email_registration.strip()
            if "<" in email_registration:
                email_registration_name, email_registration_email = email_registration.rsplit("<", 1)
                email_registration_email = email_registration_email.replace(">", "")
            else:
                email_registration_name = email_registration.replace("@", " ")
                email_registration_email = email_registration
            email_registration_email = email_registration_email.lower()
            if not email_registration_email in course_email_registration_list:
                if not portal_membership.getMemberById(email_registration_email):
                    portal_registration = getToolByName(portal, 'portal_registration')
                    password = portal_registration.generatePassword()
                    portal_membership.addMember(email_registration_email, password, ("EtudiantJalon", "Member",), "", {"fullname": email_registration_name, "email": email_registration_email})
                    portal_registration.registeredNotify(email_registration_email)
                course_email_registration_list.append(email_registration_email)
                message = 'Bonjour\n\nVous avez été inscrit au cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), self.absolute_url(), portal.Title())
                self.useJalonUtils("envoyerMail", {"form": {"a":       email_registration_email,
                                                            "objet":   "Vous avez été inscrit à un cours",
                                                            "message": message}})
        self.setInvitations(tuple(course_email_registration_list))
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def deleteEmailRegistration(self, email_registration_list):
        # LOG.info("----- deleteEmailRegistration -----")
        course_email_registration_list = set(self.getInvitations())
        delete_email_registration_list = course_email_registration_list.difference(set(email_registration_list))
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été désinscrit du cours "%s" ayant pour auteur %s.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())
        for email_registration in delete_email_registration_list:
            infosMembre = self.useJalonUtils("getIndividu", {"sesame": email_registration, "type": "dict"})
            self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                        "objet":   "Vous avez été désincrit d'un cours",
                                                        "message": message}})
        self.setInvitations(tuple(email_registration_list))
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def getCourseNbReader(self):
        # LOG.info("----- getCourseNbReader -----")
        nb_reader = 0
        for username in self.getCoLecteurs():
            if username != "***":
                nb_reader = nb_reader + 1
        return nb_reader

    def getCourseReader(self):
        # LOG.info("----- getCourseReader -----")
        retour = []
        for username in self.getCoLecteurs():
            if username != "***":
                retour.append(self.useJalonUtils("getIndividu", {"sesame": username, "type": "dict"}))
        return retour

    def addCourseReader(self, course_reader_list):
        # LOG.info("----- addCourseReader -----")
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été ajouté comme lecteur du cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), self.absolute_url(), portal.Title())
        course_readers_list = list(self.getCoLecteurs())
        if course_reader_list != ['']:
            for course_reader in course_reader_list:
                if not course_reader in course_readers_list:
                    course_readers_list.append(course_reader)
                    infosMembre = self.useJalonUtils("getIndividu", {"sesame": course_reader, "type": "dict"})
                    self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                                "objet":   "Vous avez été ajouté à un cours",
                                                                "message": message}})
            self.coLecteurs = tuple(course_readers_list)
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def deleteCourseReader(self, course_reader_list):
        # LOG.info("----- deleteCourseReader -----")
        ancienLecteurs = set(self.getCoLecteurs())
        supprLecteurs = ancienLecteurs.difference(set(course_reader_list))
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été retiré du cours "%s" ayant pour auteur %s ou vous êtiez lecteur.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())
        for idMember in supprLecteurs:
            infosMembre = self.useJalonUtils("getIndividu", {"sesame": idMember, "type": "dict"})
            self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                        "objet":   "Vous avez été retiré d'un cours",
                                                        "message": message}})
        if course_reader_list == []:
            course_reader_list.append("***")
        self.coLecteurs = tuple(course_reader_list)
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def getInfosLibre(self):
        # LOG.info("----- getInfosLibre -----")
        libre = self.getInscriptionsLibres()
        return jalon_utils.getIndividus(list(libre), "listdict")

    def getInfosListeAcces(self):
        # LOG.info("----- getInfosListeAcces -----")
        res = []
        listeAcces = self.getListeAcces()
        portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
        for acces in listeAcces:
            type, code = acces.split("*-*")
            if type == "etape":
                retour = portal_jalon_bdd.getInfosEtape(code)
                if not retour:
                    elem = ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
                else:
                    elem = list(self.useJalonUtils("encodeUTF8", {"itemAEncoder": retour}))
            if type in ["ue", "uel"]:
                retour = portal_jalon_bdd.getInfosELP2(code)
                if not retour:
                    elem = ["Le code %s n'est plus valide pour cette UE / UEL." % code, code, "0"]
                else:
                    elem = list(self.useJalonUtils("encodeUTF8", {"itemAEncoder": retour}))
            if type == "groupe":
                retour = portal_jalon_bdd.getInfosGPE(code)
                if not retour:
                    elem = ["Le code %s n'est plus valide pour ce groupe." % code, code, "0"]
                else:
                    elem = list(self.useJalonUtils("encodeUTF8", {"itemAEncoder": retour}))
            elem.append(type)
            res.append(elem)
        groupe = self.getGroupe()
        if groupe:
            res.append(["Invitations individuelles : étudiant(s) de l'université", "perso", len(groupe), "groupeperso"])
        invitations = self.getInvitations()
        if invitations:
            res.append(["Invitations individuelles : étudiant(s) hors université", "email", len(invitations), "invitationsemail"])
        password = self.getInscriptionsLibres()
        if password:
            res.append(["Accès par mot de passe : ", "libre", len(password), "password"])
        return res

    def getRechercheAcces(self):
        # LOG.info("----- getRechercheAcces -----")
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

    def rechercherUtilisateur(self, username, typeUser, match=False, json=True):
        # LOG.info("----- rechercherUtilisateur -----")
        return jalon_utils.rechercherUtilisateur(username, typeUser, match, json)

    def hasParticipants(self):
        # LOG.info("----- hasParticipants -----")
        formations = self.getFormationsOfferData()
        if formations:
            return True
        nomminatives = self.getGroupe()
        if nomminatives:
            return True
        invitations = self.getInvitations()
        if invitations:
            return True
        password = self.getLibre()
        if password:
            return True
        lecteurs = self.getCoLecteurs()
        if lecteurs and lecteurs != ("***", ):
            return True
        return False

    def getFormationsOfferData(self):
        # LOG.info("----- getFormationsOfferData -----")
        formations_offer = []
        listeAcces = self.getListeAcces()
        portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
        functions_dict = {"etape":  "getInfosEtape",
                          "ue":     "getInfosELP2",
                          "uel":    "getInfosELP2",
                          "groupe": "getInfosGPE"}
        for acces in listeAcces:
            formation_type, formation_code = acces.split("*-*")
            response = portal_jalon_bdd.__getattribute__(functions_dict[formation_type])(formation_code)
            if response:
                element = list(self.encodeUTF8(response))
                element.append(formation_type)
                formations_offer.append(element)
        formations_offer.sort()
        # LOG.info(formations_offer)
        return formations_offer

    def telechargerListingParticipants(self):
        # LOG.info("----- telechargerListingParticipants -----")
        import tempfile
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

        has_participants = False
        # ajout des étudiants de l'offre de formations
        bdd = getToolByName(self, "portal_jalon_bdd")
        dicoAffFormation = {"etape":  "Diplôme",
                            "ue":     "Unité d'enseignement",
                            "uel":    "Unité d'enseignement libre",
                            "groupe": "Groupe"}
        formations = self.getFormationsOfferData()
        for formation in formations:
            # création d'une feuille de formation
            feuille = listing.add_sheet("Formation%s" % formation[1])

            # Première Ligne : Titre de la formation ; Type ; Code
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
            has_participants = True

        # Ajout des inscriptions nominatives
        nomminatives = self.getNominativeRegistration()
        if nomminatives:
            # Création de la feuille des inscriptions nominatives
            feuille = listing.add_sheet("InscriptionsNominatives")

            # Première Ligne : Titre de la formation ; Type ; Code
            feuille.write(0, 0, "Liste des participants du cours :")
            feuille.write(0, 1, self.Title())
            feuille.write(1, 0, "Inscription(s) nominative(s)")

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
            has_participants = True

        # Ajout des invitations par courriel
        invitations = self.getEmailRegistration()
        if invitations:
            # Création de la feuille des inscriptions par email
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
            has_participants = True

        # Ajout des lecteurs enseignants
        lecteurs = self.getCoLecteurs()
        # LOG.info(lecteurs)
        if lecteurs and lecteurs != ("***",):
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
            has_participants = True

        if has_participants:
            listing.save(path)

            fp = open(path, 'rb')
            data = fp.read()
            fp.close()
            return {"length": str(os.stat(path)[6]), "data": data}
        return None

    # -------------------- #
    #  Course Life - News  #
    # -------------------- #
    def getActualitesCours(self, toutes=None):
        # LOG.info("----- getActualitesCours -----")
        actualites = []
        listeActualites = list(self.getActualites())
        listeActualites.sort(lambda x, y: cmp(y["dateActivation"], x["dateActivation"]))
        if not listeActualites:
            return {"nbActu":    0,
                    "listeActu": []}

        infos_elements = self.getCourseItemProperties()

        for actualite in listeActualites:
            if DateTime() > actualite["dateActivation"]:
                infos_element = infos_elements.get(actualite["reference"], '')
                if infos_element:
                    description = self._actuality_dict[actualite["code"]]
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

    def getActuCoursFull(self, date):
        # LOG.info("----- getActuCoursFull -----")
        actualites = []

        listeActualites = list(self.getActualites())
        listeActualites.sort(lambda x, y: cmp(y["dateActivation"], x["dateActivation"]))
        infos_elements = self.getCourseItemProperties()

        for actualite in listeActualites:
            if date > DateTime(actualite["dateActivation"]).Date():
                break
            elif date == DateTime(actualite["dateActivation"]).Date():
                infos_element = infos_elements.get(actualite["reference"], '')
                if infos_element:
                    description = self._actuality_dict[actualite["code"]]
                    if actualite["code"] == "datedepot":
                        description = "%s %s" % (description, DateTime(actualite["dateDepot"], datefmt='international').strftime("%d/%m/%Y %H:%M"))
                    if actualite["code"] == "nouveauxdepots":
                        description = "%s %s" % (str(actualite["nb"]), description)
                    actualites.append({"type":        infos_element["typeElement"],
                                       "titre":       infos_element["titreElement"],
                                       "description": description})
        return actualites

    def setActuCours(self, param):
        # LOG.info("----- setActuCours -----")
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
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    def deleteCourseActuality(self, item_id):
        # LOG.info("----- deleteCourseActuality -----")
        actuality_new = []
        actualities_list = list(self.getActualites())
        for actuality in actualities_list:
            if item_id != actuality["reference"]:
                actuality_new.append(actuality)
        self.actualites = tuple(actuality_new)
        self.setCourseProperties({"DateDerniereModif": DateTime()})

    # Pour passer l'information dans le portal_catalog et l'utiliser dans la liste de cours
    def getDateDerniereActu(self):
        # LOG.info("----- getDateDerniereActu -----")
        try:
            return DateTime(self.getLastDateActu())
        except:
            return DateTime()

    def setDateDerniereActu(self, listeActualites=None):
        # LOG.info("----- setDateDerniereActu -----")
        retour = self.created()
        paramDate = "dateActivation"
        if listeActualites is None:
            listeActualites = self.getActualitesCours(True)["listeActu"]
            paramDate = "date"
        for actualite in listeActualites:
            if cmp(actualite[paramDate], retour) > 0:
                retour = actualite[paramDate]
        self.dateDerniereActu = retour

    # --------------------- #
    #  Course Life - Forum  #
    # --------------------- #
    def toPloneboardTime(self, context, request, time_=None):
        # LOG.info("----- toPloneboardTime -----")
        """Return time formatted for Ploneboard."""
        return toPloneboardTime(context, request, time_)

    def getDicoForums(self, all=None):
        # LOG.info("----- getDicoForums -----")
        if self.getAcces() == "Public":
            return {"nbForums":    0,
                    "listeForums": []}

        listeForums = list(self.forum.objectValues())
        listeForums.sort(lambda x, y: cmp(y.modified(), x.modified()))
        if len(listeForums) > 5:
            return {"nbForums":    len(listeForums),
                    "listeForums": listeForums[:5]}
        else:
            return {"nbForums":    len(listeForums),
                    "listeForums": listeForums}

    # ------------------------ #
    #  Course Life - Announce  #
    # ------------------------ #
    def getAnnonces(self, authMember, mode_etudiant, all_annonce=False):
        # LOG.info("----- getAnnonces -----")
        annonces = []
        listeAnnonces = list(self.annonce.objectValues())
        if not listeAnnonces:
            return {"listeAnnonces": [], "nbAnnonces": 0}

        listeAnnonces.sort(lambda x, y: cmp(y.modified(), x.modified()))
        if mode_etudiant == "false":
            if all_annonce:
                return {"listeAnnonces": listeAnnonces, "nbAnnonces": len(listeAnnonces)}
            else:
                return {"last_announce": listeAnnonces[0], "nbAnnonces": len(listeAnnonces)}

        # LOG.info("***** Not Personnel")
        groupes = []
        diplomes = []
        portal = self.portal_url.getPortalObject()
        portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")
        try:
            idMember = authMember.getId()
        except:
            idMember = authMember
        if idMember and "@" not in idMember:
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
            if not publics:
                # pas besoin de la ligne suivante, si tout est decoche c'est une annonce juste pour l'auteur lui meme
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
        if annonces and all_annonce:
            return {"listeAnnonces": annonces, "nbAnnonces": len(listeAnnonces)}
        elif annonces:
            return {"last_announce": annonces[0], "nbAnnonces": len(listeAnnonces)}
        else:
            return {"listeAnnonces": [], "nbAnnonces": 0}

    def getAnnounce(self, announce_id):
        # LOG.info("----- getAnnounce -----")
        announce_folder = self.annonce
        announce_object = getattr(announce_folder, announce_id)
        return {"announce_title":       announce_object.Title(),
                "announce_description": announce_object.Description()}

    def getPublicsAnnonce(self):
        # LOG.info("----- getPublicsAnnonce -----")
        res = self.getInfosListeAcces()
        if self.getCoAuteurs():
            res.append(["Tous les co-auteurs", "coauteurs", len(self.getCoAuteurs()), "coauteurs"])
        if self.getCoLecteurs():
            res.append(["Tous les co-lecteurs", "colecteurs", len(self.getCoLecteurs()), "colecteurs"])
        return res

    def createAnnounce(self, user_id, announce_title, announce_description, announce_publics, mail_announce):
        # LOG.info("----- createAnnounce -----")
        announce_folder = self.annonce
        announce_id = announce_folder.invokeFactory(type_name="JalonAnnonce", id="Annonce-%s-%s" % (user_id, DateTime().strftime("%Y%m%d%H%M%S%f")))
        announce_object = getattr(announce_folder, announce_id)
        announce_object.setProperties({"Title":       announce_title,
                                       "Description": announce_description,
                                       "Publics":     announce_publics})
        if mail_announce:
            announce_object.envoyerAnnonce()

    def deleteAnnounce(self, announce_id):
        # LOG.info("----- deleteAnnounce -----")
        self.annonce.manage_delObjects([announce_id])

    def deleteAllAnnounce(self):
        # LOG.info("----- deleteAllAnnounce -----")
        announce_folder = self.annonce
        announce_ids = announce_folder.objectIds()
        announce_folder.manage_delObjects(announce_ids)

    def hasAnnounce(self):
        # LOG.info("----- hasAnnounce -----")
        return True if list(self.annonce.objectValues()) else False

    # -------------------------------- #
    #  Course Glossary & Bibliography  #
    # -------------------------------- #
    def getGloBib(self, glo_bib):
        # LOG.info("----- getGloBib -----")
        dicoLettres = {}
        if glo_bib == "glossaire":
            elements = self.getGlossaire()
            folder_id = "Glossaire"
        else:
            elements = self.getBibliographie()
            folder_id = "Externes"
        if elements:
            infos_element = self.getCourseItemProperties()

        portal_link = self.portal_url.getPortalObject().absolute_url()
        for idElement in elements:
            info_element = infos_element.get(idElement)
            if info_element:
                info_element["idElement"] = idElement
                lettre = info_element["titreElement"][0].upper()
                info_element["urlElement"] = "%s/Members/%s/%s/%s/view" % (portal_link, info_element["createurElement"], folder_id, idElement)
                if not lettre in dicoLettres:
                    dicoLettres[lettre] = [info_element]
                else:
                    dicoLettres[lettre].append(info_element)
        return dicoLettres

    # ------------------- #
    #  Course indicators  #
    # ------------------- #
    def insererConsultation(self, user, type_cons, id_cons):
        # LOG.info("----- insererConsultation -----")
        public_cons = "Anonymous"
        if user.has_role("Personnel"):
            username = user.getId()
            if self.isAuteur(username):
                public_cons = "Auteur"
            if username in self.coAuteurs:
                public_cons = "Co-auteur"
            if username in self.coLecteurs:
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
        # LOG.info("----- getConsultation -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByCoursByDate(self.getId())

    def getConsultationByCoursByUniversityYearByDate(self, DATE_CONS_YEAR, FILTER_DATE, PUBLIC_CONS):
        # LOG.info("----- getConsultationByCoursByUniversityYearByDate -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByCoursByUniversityYearByDate(self.getId(), DATE_CONS_YEAR, FILTER_DATE, PUBLIC_CONS)

    def getConsultationByCoursByYearForGraph(self):
        # LOG.info("----- getConsultationByCoursByYearForGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByCoursByYearForGraph(self.getId())

    def getConsultationByCoursByUniversityYearForGraph(self):
        # LOG.info("----- getConsultationByCoursByYearForGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByCoursByUniversityYearForGraph(self.getId())

    def getFrequentationByCoursByUniversityYearByDateForGraph(self, PUBLIC_CONS):
        # LOG.info("----- getFrequentationByCoursByUniversityYearForGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getFrequentationByCoursByUniversityYearByDateForGraph(self.getId(), PUBLIC_CONS)

    def getConsultationElementsByCours(self, elements_list, elements_dict):
        # LOG.info("----- getConsultationElementsByCours -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationElementsByCours(self.getId(), elements_list=elements_list, elements_dict=elements_dict)

    def getConsultationByElementByCours(self, element_id):
        # LOG.info("----- getConsultationByElementByCours -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByElementByCours(self.getId(), element_id)

    def getConsultationByElementByCoursByYearForGraph(self, element_id):
        # LOG.info("----- getConsultationByElementByCoursByYearForGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByElementByCoursByYearForGraph(self.getId(), element_id)

    def getConsultationByElementByCoursByUniversityYearForGraph(self, element_id):
        # LOG.info("----- getConsultationByElementByCoursByUniversityYearForGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByElementByCoursByUniversityYearForGraph(self.getId(), element_id)

    def genererGraphIndicateurs(self, months_dict):
        # LOG.info("----- genererGraphIndicateurs -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.genererGraphIndicateurs(months_dict)

    def genererFrequentationGraph(self, months_dict):
        self.plone_log("genererFrequentationGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.genererFrequentationGraph(months_dict)

    # --------------------------- #
    #  Forum à modifier si mieux  #
    # --------------------------- #
    def getForumBreadcrumbs(self, item, page="basic"):
        item_title = item.Title()
        item_link = item.absolute_url()
        item_parent_title = item.aq_parent.title_or_id()
        item_parent_link = item.aq_parent.absolute_url()
        item_root = item.aq_parent.aq_parent
        item_root_title = item.aq_parent.aq_parent.title_or_id()
        item_root_link = item.aq_parent.aq_parent.absolute_url()

        breadcrumbs = {"Ploneboard": {"jalon_forum_search":    [{"title": item_title,
                                                                 "icon":  "fa fa-comments",
                                                                 "link":  item_link},
                                                                {"title": "Recherche",
                                                                 "icon":   "fa fa-search",
                                                                 "link":  "%s/jalon_forum_search" % item_link}],
                                      "ploneboard_recent":     [{"title": item_title,
                                                                 "icon":  "fa fa-comments",
                                                                 "link":  item_link},
                                                                {"title": "Activité récente",
                                                                 "icon":  "fa fa-comment",
                                                                 "link":  "%s/ploneboard_recent" % item_link}],
                                      "ploneboard_unanswered": [{"title": item_title,
                                                                 "icon":  "fa fa-comments",
                                                                 "link":  item_link},
                                                                {"title": "Conversations sans réponse",
                                                                 "icon":  "fa fa-comment-o",
                                                                 "link":  "%s/ploneboard_unanswered" % item_link}],
                                      "basic":                 [{"title": item_title,
                                                                 "icon": "fa fa-comments",
                                                                 "link":  item_link}]},
                       "PloneboardForum": {"ploneboard_unanswered": [{"title": item_parent_title,
                                                                      "icon":  "fa fa-comments",
                                                                      "link":   item_parent_link},
                                                                     {"title": "Conversations sans réponse",
                                                                      "icon":  "fa fa-comment-o",
                                                                      "link":  "%s/ploneboard_unanswered" % item_link}],
                                           "basic":                 [{"title": item_parent_title,
                                                                      "icon":  "fa fa-comments",
                                                                      "link":  item_parent_link},
                                                                     {"title": item_title,
                                                                      "icon":  "fa fa-comments",
                                                                      "link":  item_link}]},
                       "PloneboardConversation": {"basic": [{"title": item_root_title,
                                                             "icon": "fa fa-comments",
                                                             "link": item_root_link},
                                                            {"title": item_parent_title,
                                                             "icon":  "fa fa-comments",
                                                             "link":  item_parent_link},
                                                            {"title": item_title,
                                                             "icon": "fa fa-comments-o",
                                                             "link":  item_link}]},
                       "PloneboardComment": {"basic": [{"title": item_root.aq_parent.title_or_id(),
                                                        "icon":  "fa fa-comments",
                                                        "link":  item_root.aq_parent.absolute_url()},
                                                       {"title": item_root_title,
                                                        "icon":  "fa fa-comments",
                                                        "link":  item_root_link},
                                                       {"titre": item_title,
                                                        "icone": "fa fa-comments-o",
                                                        "link":  item_link}]}}
        basic_breadcrumbs = [{"title": _(u"Mes cours"),
                              "icon":  "fa fa-university",
                              "link":  "%s/mes_cours" % self.portal_url.absolute_url()},
                             {"title": self.Title(),
                              "icon":  "fa fa-book",
                              "link":  self.absolute_url()}]
        basic_breadcrumbs.extend(breadcrumbs[item.meta_type][page])
        return basic_breadcrumbs

    def ajouterForum(self, user_id, titreElement, descriptionElement):
        # LOG.info("----- ajouterForum -----")
        forum_folder = self.forum
        forum_id = forum_folder.invokeFactory(type_name="PloneboardForum", id="Forum-%s-%s" % (user_id, DateTime().strftime("%Y%m%d%H%M%S%f")))
        forum_object = getattr(forum_folder, forum_id)
        forum_object.setTitle(titreElement)
        forum_object.setDescription(descriptionElement)
        forum_object.setMaxAttachments(0)
        forum_object.reindexObject()


# enregistrement dans la registery Archetype
registerATCT(JalonCours, PROJECTNAME)
