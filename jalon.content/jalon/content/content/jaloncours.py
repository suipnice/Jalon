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

    """ Un cours Jalon."""

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
                            "activity_title":       "Boite de dépots",
                            "activity_portal_type": "JalonBoiteDepot"},
                      "2": {"activity_id":          "AutoEvaluation",
                            "activity_title":       "Auto-évaluation WIMS",
                            "activity_portal_type": "JalonCoursWims"},
                      "3": {"activity_id":          "Examen",
                            "activity_title":       "Examen WIMS",
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
                      "item_action_name": "Afficher"},
                     {"item_action_id":   "edit_course_item_visibility_form",
                      "item_action_icon": "fa fa-eye-slash fa-fw",
                      "item_action_name": "Masquer"},
                     {"item_action_id":   "course_edit_item_form",
                      "item_action_icon": "fa fa-pencil fa-fw",
                      "item_action_name": "Modifier"},
                     {"item_action_id":   "course_jalonner_item_form",
                      "item_action_icon": "fa fa-hand-o-left fa-fw",
                      "item_action_name": "Jalonner"},
                     {"item_action_id":   "course_detach_item_form",
                      "item_action_icon": "fa fa-chain-broken fa-fw",
                      "item_action_name": "Détacher"},
                     {"item_action_id":   "course_delete_item_form",
                      "item_action_icon": "fa fa-trash-o fa-fw",
                      "item_action_name": "Supprimer"}]

    _add_course_map_item_dict = {"1": {"form_title":    "titre",
                                       "is_type_title": True,
                                       "item_type":     "Titre",
                                       "form_js":       "setRevealFormPlanRefresh('js-planTextCreator','reveal-main')"},
                                 "2": {"form_title":    "texte libre",
                                       "is_type_title": False,
                                       "item_type":     "TexteLibre",
                                       "form_js":       "setRevealFormPlanRefresh('js-planTextCreator','reveal-main','titreElement')"}}

    def __init__(self, *args, **kwargs):
        super(JalonCours, self).__init__(*args, **kwargs)
        self._elements_cours = {}

    #------------#
    # Utilitaire #
    #------------#
    def getCoursePasswordBreadcrumbs(self):
        LOG.info("----- getCoursePasswordBreadcrumbs -----")
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

    def checkCourseAuthorized(self, user, request):
        LOG.info("----- checkCourseAuthorized -----")
        #LOG.info("***** SESSION : %s" % request.SESSION.get("course_authorized_list", []))
        if self.getLibre():
            return True
        if user.has_role(["Manager", "Owner"]):
            return True
        if user.has_role(["Personnel", "Secretaire"]):
            user_id = user.getId()
            if self.isAuteurs(user_id):
                return True
            if self.isCoLecteurs(user_id):
                return True
        if not self.getId() in request.SESSION.get("course_authorized_list", []):
            request.RESPONSE.redirect("%s/insufficient_privileges" % self.absolute_url())

    def useJalonUtils(self, method_name, method_parameters_dict):
        LOG.info("----- useJalonUtils -----")
        LOG.info("***** method_name : %s" % method_name)
        return jalon_utils.__getattribute__(method_name)(**method_parameters_dict)

    def getLastLogin(self):
        LOG.info("----- getLastLogin -----")
        member = self.portal_membership.getAuthenticatedMember()
        last_login = member.getProperty('last_login_time', None)
        if isinstance(last_login, basestring):
            last_login = DateTime(last_login)
        return last_login

    def getElementCours(self, key=None):
        LOG.info("----- getElementCours -----")
        LOG.info("***** item_id : %s" % key)
        if key:
            return self._elements_cours.get(key, None)
        return self._elements_cours

    def getKeyElementCours(self):
        LOG.info("----- getKeyElementCours -----")
        return self._elements_cours.keys()

    def getAffElement(self, idElement, attribut):
        LOG.info("----- getAffElement -----")
        infos_element = self.getElementCours(idElement)
        if infos_element:
            LOG.info("item_property : %s" % str(infos_element))
            if infos_element[attribut] != "":
                return infos_element[attribut].strftime("%Y/%m/%d %H:%M")
        return DateTime().strftime("%Y/%m/%d %H:%M")

    def setElementsCours(self, elements_cours):
        LOG.info("----- setElementsCours -----")
        if type(self._elements_cours).__name__ != "PersistentMapping":
            self._elements_cours = PersistentDict(elements_cours)
        else:
            self._elements_cours = elements_cours

    def setProprietesElement(self, infos_element):
        LOG.info("----- setProprietesElement -----")
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

    def setProperties(self, dico):
        LOG.info("----- setProprietesElement -----")
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        if key == "DateDerniereModif":
            self.reindexObject()

    def getMySpaceFolder(self, user_id, folder_id):
        LOG.info("----- getMySpaceFolder -----")
        return getattr(getattr(portal.Members, user_id), self._folder_my_space_dict[folder_id])

    def getMySubSpaceFolder(self, user_id, folder_id, portal):
        LOG.info("----- getMySubSpaceFolder -----")
        return getattr(getattr(portal.Members, user_id), folder_id)

    def getCategorieCours(self):
        LOG.info("----- getCategorieCours -----")
        try:
            return self.categorie[0]
        except:
            return 1

    def getRole(self):
        LOG.info("----- getRole -----")
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

    #getSousObjet renvoie le sous-objet idElement
    #def getSousObjet(self, idElement):
    #    LOG.info("----- getSousObjet -----")
    #    if "*-*" in idElement:
    #        idElement = idElement.split("*-*")[-1]
    #    return getattr(self, idElement)

    #getTypeSousObjet renvoie le type du sous-objet idElement
    def getTypeSousObjet(self, idElement):
        LOG.info("----- getTypeSousObjet -----")
        if "*-*" in idElement:
            typeSousObjet = idElement.split("*-*")[0]
        else:
            typeSousObjet = idElement.split("-")[0]
        return typeSousObjet

    def isPersonnel(self, user, mode_etudiant="false"):
        LOG.info("----- isPersonnel -----")
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

    def getLocaleDate(self, date, format="%d/%m/%Y"):
        LOG.info("----- getLocaleDate -----")
        return jalon_utils.getLocaleDate(date, format)

    def convertirDate(self, date):
        LOG.info("----- convertirDate -----")
        return jalon_utils.convertirDate(date)

    def getShortText(self, text, limit=75):
        LOG.info("----- getShortText -----")
        return jalon_utils.getShortText(text, limit)

    def supprimerMarquageHTML(self, chaine):
        LOG.info("----- supprimerMarquageHTML -----")
        return jalon_utils.supprimerMarquageHTML(chaine)

    def test(self, condition, valeurVrai, valeurFaux):
        LOG.info("----- test -----")
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

    def jalon_quote(self, encode):
        LOG.info("----- jalon_quote -----")
        return jalon_utils.jalon_quote(encode)

    #--------------------------#
    # Course action My Courses #
    #--------------------------#
    def addCourseForum(self, forum_title, forum_description, user_id):
        LOG.info("----- addCourseForum -----")

        forum_folder = self.forum
        forum_id = forum_folder.invokeFactory(type_name="PloneboardForum", id="Forum-%s-%s" % (user_id, DateTime().strftime("%Y%m%d%H%M%S%f")))
        forum_object = getattr(forum_folder, forum_id)

        forum_object.setTitle(forum_title)
        forum_object.setDescription(forum_description)
        forum_object.setMaxAttachments(0)
        forum_object.reindexObject()

        return forum_id

    def getDataCourseFormAction(self, user_id, course_id):
        LOG.info("----- getDataCourseFormAction -----")
        return {"course_name":     self.getShortText(self.Title(), 80),
                "is_course_owner": self.isCourseOwner(user_id)}

    def modifyFavorite(self, user_id):
        LOG.info("----- modifyFavorite -----")
        subjects = list(self.Subject())
        if not user_id in subjects:
            subjects.append(user_id)
            archives = list(self.getArchive())
            if user_id in archives:
                archives.remove(user_id)
                self.setArchive(tuple(archives))
        else:
            subjects.remove(user_id)
        self.setSubject(tuple(subjects))
        self.setProperties({"DateDerniereModif": DateTime()})

    def modifyArchive(self, user_id):
        LOG.info("----- modifyArchive -----")
        archives = list(self.getArchive())
        if not user_id in archives:
            archives.append(user_id)
            subjects = list(self.Subject())
            if user_id in subjects:
                subjects.remove(user_id)
                self.setSubject(tuple(subjects))
        else:
            archives.remove(user_id)
        self.setArchive(tuple(archives))
        self.setProperties({"DateDerniereModif": DateTime()})

    #----------------#
    # Course Heading #
    #----------------#
    def getDescriptionCourte(self):
        LOG.info("----- getDescriptionCourte -----")
        description = self.Description()
        if not description:
            return {"link": False, "desc": "ce cours n'a pas encore de description."}
        if len(description) > 100:
            return {"link": True, "desc": self.getShortText(description, 100)}
        return {"link": False, "desc": description}

    def isCourseOwner(self, user_id):
        LOG.info("----- isCourseOwner -----")
        return True if self.aq_parent.getId() == user_id else False

    def isAuteur(self, username):
        LOG.info("----- isAuteur -----")
        if username == self.Creator():
            return 1
        if username == self.getAuteurPrincipal():
            return 1
        return 0

    def isAuteurs(self, username):
        LOG.info("----- isAuteurs -----")
        return self.isAuteur(username) or self.isCoAuteurs(username)

    def isInscriptionsLibre(self):
        LOG.info("----- isInscriptionsLibre -----")
        if len(self.getInscriptionsLibre()) > 0:
            return True
        else:
            return False

    def getCreateur(self):
        LOG.info("----- getCreateur -----")
        return self.useJalonUtils("getInfosMembre", {"username": self.Creator()})

    def getAuteur(self):
        LOG.info("----- getAuteur -----")
        username = self.getAuteurPrincipal()
        if username:
            return self.useJalonUtils("getInfosMembre", {"username": username})
        return self.useJalonUtils("getInfosMembre", {"username": self.Creator()})

    def getAuteurs(self):
        LOG.info("----- getAuteurs -----")
        return {"principal": self.getAuteur(), "coAuteurs": self.getCoAuteursCours()}

    def getAuthorForm(self):
        LOG.info("----- getAuthorForm -----")
        course_author = self.getAuteur()
        course_creator = self.getCreateur()

        course_author_dict = {"course_author_name":  course_author["fullname"],
                              "course_creator_name": course_creator["fullname"]}

        if self.useJalonUtils("isLDAP", {}):
            ldap_base = context.useJalonUtils("getBaseAnnuaire", {})
            course_author_dict["course_author_link"] = self.useJalonUtils("getFicheAnnuaire", {"valeur": course_author,
                                                                                               "base":   ldap_base})
            course_author_dict["course_creator_link"] = self.useJalonUtils("getFicheAnnuaire", {"valeur": course_creator,
                                                                                                "base":   ldap_base})
        return course_author_dict

    def setAuteur(self, form):
        LOG.info("----- setAuteur -----")
        ancienPrincipal = self.getAuteurPrincipal()
        if not ancienPrincipal:
            ancienPrincipal = self.Creator()
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été ajouté comme auteur du cours "%s" ayant eu pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace Mes cours.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), portal.absolute_url(), portal.Title())
        self.auteurPrincipal = form["username"]
        infosMembre = self.useJalonUtils("getInfosMembre", {"username": form["username"]})
        #self.tagBU(ancienPrincipal)
        self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                    "objet":   "Vous avez été ajouté à un cours",
                                                    "message": message}})
        infosMembre = self.useJalonUtils("getInfosMembre", {"username": ancienPrincipal})
        message = 'Bonjour\n\nVous avez été retiré du cours "%s" ou vous êtiez auteur.\n\nCordialement,\n%s.' % (self.Title(), portal.Title())
        self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                    "objet":   "Vous avez été retiré d'un cours",
                                                    "message": message}})
        self.manage_setLocalRoles(form["username"], ["Owner"])
        self.setProperties({"DateDerniereModif": DateTime()})

    def getCoAuteursCours(self):
        LOG.info("----- getCoAuteursCours -----")
        retour = []
        for username in self.getCoAuteurs():
            if username:
                retour.append(self.useJalonUtils("getInfosMembre", {"username": username}))
        return retour

    def addCoAuteurs(self, form):
        LOG.info("----- addCoAuteurs -----")
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été ajouté comme co-auteur du cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), portal.absolute_url(), portal.Title())
        coAuteurs = list(self.getCoAuteurs())
        usernames = form["username"].split(",")
        if usernames != ['']:
            for username in usernames:
                if not username in coAuteurs:
                    coAuteurs.append(username)
                    self.manage_setLocalRoles(username, ["Owner"])
                    infosMembre = self.useJalonUtils("getInfosMembre", {"username": username})
                    self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                                "objet":   "Vous avez été ajouté à un cours",
                                                                "message": message}})
            self.coAuteurs = tuple(coAuteurs)
        self.setProperties({"DateDerniereModif": DateTime()})

    def deleteCoAuteurs(self, form):
        LOG.info("----- deleteCoAuteurs -----")
        auteurs = []
        if "auteur-actu" in form:
            auteurs = form["auteur-actu"]
        ancienAuteurs = set(self.getCoAuteurs())
        supprAuteurs = ancienAuteurs.difference(set(auteurs))

        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été retiré du cours "%s" ayant pour auteur %s ou vous êtiez co-auteur.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())

        for idMember in supprAuteurs:
            infosMembre = self.useJalonUtils("getInfosMembre", {"username": idMember})
            self.useJalonUtils("envoyerMail", {"form": {"a":      infosMembre["email"],
                                                        "objet":  "Vous avez été retiré d'un cours",
                                                        "message": message}})
        self.coAuteurs = tuple(auteurs)
        self.setProperties({"DateDerniereModif": DateTime()})

    def setCoursePublicAccess(self, course_public_access):
        LOG.info("----- setCoursePublicAccess -----")
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
        LOG.info("----- isCoAuteurs -----")
        u""" Détermine si l'utilisateur 'username' est un auteur ou co-auteur du cours."""
        if self.isAuteur(username):
            return True
        if username in self.coAuteurs:
            return True
        # Dans le cas de l'admin, isCoAuteurs renvoi 0 aussi
        LOG.info("----- isCoAuteurs = 0 (ni auteur, ni coAuteur)")
        return 0

    def isCoLecteurs(self, username):
        LOG.info("----- isCoLecteurs -----")
        return True if username in self.coLecteur else False

    #------------#
    # Course Map #
    #------------#
    def getProprietesVideo(self, id_video):
        LOG.info("----- getProprietesVideo -----")
        infos_element = self.getElementCours(id_video)
        video_title = infos_element["titreElement"]
        video_title_my_space = video_title
        if "titreElementMonEspace" in infos_element:
            video_title_my_space = infos_element["titreElementMonEspace"]
        return {"video_title":          video_title,
                "video_title_my_space": video_title_my_space,
                "is_display_in_map":    "checked" if infos_element["complementElement"]["value"] else ""}

    def getCommentaireEpingler(self, idTester=None):
        LOG.info("----- getCommentaireEpingler -----")
        if len(self.getAvancementPlan()) <= 1:
            return ""

        if not idTester:
            return self.getAvancementPlan()[1]
        elif idTester == self.getAvancementPlan()[0]:
            return self.getAvancementPlan()[1]

        return ""

    def getDisplayCourseMapAttributes(self, user):
        LOG.info("----- getDisplayCourseMapAttributes -----")
        return {"is_personnel":         self.isPersonnel(user),
                "user_last_login_time": user.getProperty('login_time', ""),
                "course_news":          self.getActualitesCours(),
                "portal":               self.portal_url.getPortalObject()}

    def getAddCourseMapItemForm(self, item_type):
        LOG.info("----- getAddCourseMapItemForm -----")
        LOG.info("***** dict : %s" % str(self._add_course_map_item_dict[item_type]))
        return self._add_course_map_item_dict[item_type]

    def getCourseMap(self, user_id, user_last_login_time, is_personnel, course_actuality_list, portal):
        LOG.info("----- getCourseMap -----")
        return self.getCourseMapItems(self.getPlan(), user_id, user_last_login_time, is_personnel, course_actuality_list, portal, True)

    def getCourseMapItems(self, course_map_items_list, user_id, user_last_login_time, is_personnel, course_actuality_list, portal, is_map_top_level=False):
        LOG.info("----- getCourseMapItems -----")
        ol_css_id = ""
        ol_css_class = ""
        if is_map_top_level:
            ol_css_id = "course_plan-plan"
            ol_css_class = "ui-sortable"

        item_jalonner = self.getCourseMapItemJalonner()

        #index = 0
        course_map_list = []
        for course_map_item in course_map_items_list:
            #index = index + 1
            item_properties = self.getElementCours(course_map_item["idElement"])

            item = {"item_id":      course_map_item["idElement"],
                    "item_title":   item_properties["titreElement"],
                    "item_drop_id": "drop-%s" % course_map_item["idElement"].replace("*-*", "")}

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
                    item["item_css_class"] = "chapitre"
                    course_map_sub_items_list = course_map_item["listeElement"]
                else:
                    if item_properties["typeElement"] in ["TexteLibre", "BoiteDepot", "AutoEvaluation"]:
                        item["item_link"] = "/".join([self.absolute_url(), course_map_item["idElement"]])
                    else:
                        item["item_link"] = "/".join([portal.absolute_url(), "Members", item_properties["createurElement"], self._type_folder_my_space_dict[item_properties["typeElement"].replace(" ", "")], course_map_item["idElement"].replace("*-*", "."), "view"])

                item["item_css_id"] = "%s-%s" % (item["item_css_class"], course_map_item["idElement"])
                item["course_map_sub_items_list"] = course_map_sub_items_list

                item["is_item_title_or_text"] = True if item_properties["typeElement"] in ["Titre", "TexteLibre"] else False

                item["is_item_readable"] = True if not is_personnel and not item["is_item_title"] else False

                if not is_personnel:
                    item["item_read_link"] = "%s/marquer_element_script?item_id=%s" % (self.absolute_url(), course_map_item["idElement"])
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

    def isAfficherElement(self, affElement, masquerElement):
        LOG.info("----- isAfficherElement -----")
        return jalon_utils.isAfficherElement(affElement, masquerElement)

    def getCourseMapItemJalonner(self):
        LOG.info("----- getCourseMapItemJalonner -----")
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
        LOG.info("----- getItemActions -----")
        item_actions = self._item_actions[:]

        if is_display_item_bool:
            del item_actions[0]
        else:
            del item_actions[1]

        if item_properties["typeElement"] in ["BoiteDepot", "AutoEvaluation", "Examen", "Titre", "TexteLibre"]:
            del item_actions[-2]
        else:
            del item_actions[-1]

        if item_properties["typeElement"] in ["AutoEvaluation", "Examen"]:
            del item_actions[-1]

        return item_actions

    def getCourseMapForm(self):
        LOG.info("----- getCourseMapForm -----")
        return self.restrictedTraverse("cours/%s/%s/course_map_form" % (self.aq_parent.getId(), self.getId()))()

    def getCourseMapList(self, liste=None):
        LOG.info("----- getCourseMapList -----")
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
        LOG.info("----- getCourseMapList -----")
        if not listeElement:
            listeElement = self.getCourseMapList()
        if idElement in listeElement:
            return 1
        return 0

    def getCourseAddActivityForm(self, activity_type):
        LOG.info("----- getCourseAddActivityForm -----")
        return self._activity_dict[activity_type]["activity_title"]

    def getUrlWebconference(self, url):
        LOG.info("----- getUrlWebconference -----")
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

    def getWebconferencesAuteurs(self, personnel):
        LOG.info("----- getWebconferencesAuteurs -----")
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
        LOG.info("----- getWebconferencesUser -----")
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
        LOG.info("----- getWebconferenceUrlById -----")
        for reunion in self.getWebconferencesUser(True, authMember):
            if reunion["id"] == webid:
                return self.getUrlWebconference(reunion['url'])
        return ""

    def activerWebconference(self, idwebconference):
        LOG.info("----- activerWebconference -----")
        webconferences = list(self.webconferences)
        if not idwebconference in webconferences:
            webconferences.append(idwebconference)
        else:
            webconferences.remove(idwebconference)
        self.webconferences = tuple(webconferences)

    def setLecture(self, lu, idElement, authMember):
        LOG.info("----- setLecture -----")
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
        LOG.info("----- marquerElement -----")
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

    def getDisplayItemForm(self, item_id):
        LOG.info("----- getDisplayItemForm -----")
        form_properties = {"is_authorized_form":       True,
                           "is_item_title":            False,
                           "is_item_parent_title":     False,
                           "help_css":                 "panel callout radius",
                           "help_text":                "Vous êtes sur le point d'afficher cette ressource à vos étudiants."}
        item_properties = self.getElementCours(item_id)
        form_properties["is_wims_examen"] = True if item_properties["typeElement"] == "Examen" else False

        display_properties = self.isAfficherElement(item_properties["affElement"], item_properties["masquerElement"])
        if display_properties["val"]:
            form_properties["form_button_css"] = "button small radius warning"
            form_properties["form_button_directly_text"] = "Masquer l'élément maintenant"
            form_properties["form_button_lately_text"] = "Programmer le masquage de l'élément à l'instant choisi"
            form_properties["item_property_name"] = "masquerElement"
            form_properties["form_title_text"] = "Masquer l'élément : %s" % item_properties["titreElement"]
            form_properties["form_title_icon"] = "fa fa-eye-slash no-pad"
            form_properties["item_parent_title"] = ""
            form_properties["wims_help_text"] = False

            form_properties["text_title_lately"] = "… ou programmer son masquage."
            if item_properties["typeElement"] == "Titre":
                form_properties["is_item_title"] = True
                form_properties["text_title_directly"] = "Masquer directement le titre / sous titre et son contenu…"
            else:
                form_properties["text_title_directly"] = "Masquer directement…"

            form_properties["form_name"] = "masquer-element"
            form_properties["item_date"] = self.getAffElement(item_id, "masquerElement")
        else:
            form_properties["form_button_css"] = "button small radius"
            form_properties["form_button_directly_text"] = "Afficher l'élément maintenant"
            form_properties["form_button_lately_text"] = "Programmer l'affichage de l'élément à l'instant choisi"
            form_properties["item_property_name"] = "affElement"
            form_properties["is_wims_examen"] = False
            form_properties["form_title_text"] = "Afficher l'élément : %s" % item_properties["titreElement"]
            form_properties["form_title_icon"] = "fa fa-eye no-pad"

            item_parent_properties = self.getParentPlanElement(item_id, "racine", "")
            if item_parent_properties["idElement"] != "racine":
                display_parent_properties = self.isAfficherElement(item_parent_properties["affElement"], item_parent_properties["masquerElement"])
                if not display_parent_properties["val"]:
                    form_properties["is_item_parent_title"] = True
                    form_properties["item_parent_title_id"] = item_parent_properties["idElement"]
                    form_properties["item_parent_title"] = item_parent_properties["titreElement"]

            if item_properties["typeElement"] in ["AutoEvaluation", "Examen"]:
                is_authorized_activity = getattr(self, item_id).autoriser_Affichage()
                #is_authorized_activity = self.autoriserAffichageSousObjet(item_id, item_properties["typeElement"])
                if not is_authorized_activity["val"]:
                    form_properties["is_authorized_form"] = False
                    form_properties["help_css"] = "panel warning radius"
                    if is_authorized_activity["reason"] == "listeExos":
                        form_properties["help_text"] = "Vous ne pouvez pas afficher une auto-évaluation ou un examen tant que sa liste d'exercices est vide."
                    else:
                        form_properties["help_text"] = "Vous ne pouvez pas afficher cette ressource. %s" % is_authorized_activity["reason"]

            form_properties["text_title_lately"] = "… ou programmer son affichage."
            if item_properties["typeElement"] == "Titre":
                form_properties["is_item_title"] = True
                form_properties["text_title_directly"] = "Afficher directement le titre / sous titre et son contenu…"
                form_properties["wims_help_text"] = True
            else:
                form_properties["text_title_directly"] = "L'afficher directement…"
                form_properties["wims_help_text"] = False

            form_properties["form_name"] = "afficher-element"
            form_properties["item_date"] = self.getAffElement(item_id, "affElement")

        return form_properties

    def editCourseTitleVisibility(self, item_id, item_date, item_property_name, items_list=None):
        LOG.info("----- editCourseTitleVisibility -----")
        actuality_code = "chapdispo" if item_property_name == "affElement" else ""

        if actuality_code:
            self.updateActualities(item_id, item_date, actuality_code)

        if items_list is None:
            items_list = list(self.getPlan())

        for item in items_list:
            if item["idElement"] == item_id or item_id == "all":
                # On commence par afficher le chapitre lui-même
                self.editCourseItemVisibility(item["idElement"], item_date, item_property_name, True)
                if "listeElement" in item:
                    for sub_item in item["listeElement"]:
                        #Puis on affiche tous les elements du chapitre
                        self.editCourseItemVisibility(sub_item["idElement"], item_date, item_property_name, True)
                        if "listeElement" in sub_item:
                            # Si un des éléments est un sous-chapitre, on affiche son contenu recursivement.
                            self.editCourseTitleVisibility("all", item_date, item_property_name, sub_item["listeElement"])
                #Lorsqu'on a trouvé le chapitre qu'on cherchait, plus besoin de continuer à parcourir le plan.
                if item["idElement"] == item_id:
                    break
            elif "listeElement" in item:
                self.editCourseItemVisibility(item_id, item_date, item_property_name, item["listeElement"])

    def editCourseItemVisibility(self, item_id, item_date, item_property_name, is_update_from_title=False):
        LOG.info("----- editCourseItemVisibility -----")
        u""" Modifie l'etat de la ressource quand on modifie sa visibilité ("attribut" fournit l'info afficher / masquer)."""
        item_properties = self.getElementCours(item_id)

        if item_properties["typeElement"] in ["BoiteDepot", "AutoEvaluation", "Examen"]:
            item_object = getattr(self, item_id)
            item_object.afficherRessource(item_id, item_date, item_property_name)

        update_actuality = False
        if item_property_name == "affElement":
            item_properties["masquerElement"] = ""
            if item_properties["typeElement"] in self._type_folder_my_space_dict:
                portal_workflow = getToolByName(self.portal_url.getPortalObject(), "portal_workflow")
                course_state = portal_workflow.getInfoFor(self, "review_state", wf_id="jalon_workflow")
                if course_state == "published":
                    item_object = getattr(getattr(getattr(portal.Members, item_properties["createurElement"]), self._type_folder_my_space_dict), item_id.replace("*-*", "."))
                    item_object_state = portal_workflow.getInfoFor(item_object, "review_state", wf_id="jalon_workflow")
                    if cours_state != item_object_state:
                        portal_workflow.doActionFor(objet, "publish", "jalon_workflow")

            if not is_update_from_title:
                update_actuality = True
                self.updateActualities(item_id, item_date, "dispo")
        else:
            self.delActu(item_id)

        item_properties[item_property_name] = item_date
        self._elements_cours[item_id] = item_properties
        self.setElementsCours(self._elements_cours)

        if not update_actuality:
            self.setProperties({"DateDerniereModif": DateTime()})

    def editCourseParentTitleVisibility(self, item_parent_id, item_date):
        LOG.info("----- editCourseParentTitleVisibility -----")
        item_properties = self.getElementCours(item_parent_id)

        item_properties["affElement"] = item_date
        item_properties["masquerElement"] = ""
        self._elements_cours[item_parent_id] = item_properties
        self.setElementsCours(self._elements_cours)

        item_parent = self.getParentPlanElement(item_parent_id, 'racine', '')
        if item_parent["idElement"] == "racine":
            self.updateActualities(item_parent_id, item_date, "chapdispo")
        else:
            self.editCourseParentTitleVisibility(item_parent["idElement"], item_date)

    def updateActualities(self, item_id, item_date, actuality_code):
        LOG.info("----- updateActualities -----")
        actualities_list = list(self.getActualites())
        actuality_dict = {"reference":      item_id,
                          "dateActivation": item_date,
                          "code":           actuality_code,
                          "nb":             0,
                          "dateDepot":      None,
                          "acces":          ["auteurs", "etudiants"]}
        if not actuality_dict in actualities_list:
            self.setActuCours(actuality_dict)

    def getParentPlanElement(self, idElement, idParent, listeElement):
        LOG.info("----- getParentPlanElement -----")
        if idParent == "racine":
            listeElement = self.plan
        LOG.info("***** listeElement : %s" % str(listeElement))
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
        LOG.info("----- getEnfantPlanElement -----")
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
        LOG.info("----- addMySpaceItem -----")
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
        if not self in item_object_related:
            item_object_related.append(self)
            item_object.setRelatedItems(item_object_related)
            item_object.reindexObject()

        course_related = self.getRelatedItems()
        if not item_object in course_related:
            course_related.append(item_object)
            self.setRelatedItems(course_related)

        complement_element = None
        if item_type in ["Video", "VOD"]:
            complement_element = {"value":  display_in_plan,
                                  "auteur": item_object.getVideoauteurname(),
                                  "image":  item_object.getVideothumbnail()}

        self.addItemInCourseMap(item_id_no_dot, map_position)
        self.addItemProperty(item_id_no_dot, item_type, item_object.Title(), user_id, display_item, complement_element)

    def addItemInCourseMap(self, item_id, map_position):
        LOG.info("----- addItemInCourseMap -----")
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

    def setCourseMapPosition(self, item_id, item_properties, items_list, course_title_list):
        LOG.info("----- setCourseMapPosition -----")
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
        LOG.info("----- addItemProperty -----")
        parent = self.getParentPlanElement(item_id, 'racine', '')
        LOG.info("***** parent : %s" % str(parent))
        if parent and parent['idElement'] != 'racine':
            is_display_parent = self.isAfficherElement(parent['affElement'], parent['masquerElement'])
            LOG.info("***** is_display_parent : %s" % str(is_display_parent))
            if not is_display_parent['val']:
                display_item = ""

        items_properties = self.getElementCours()
        if not item_id in items_properties:
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
            self.setElementsCours(items_properties)

    def addCourseActivity(self, user_id, activity_type, activity_title, activity_description, map_position):
        LOG.info("----- addCourseActivity -----")
        activity_dict = self._activity_dict[activity_type]
        activity_id = self.invokeFactory(type_name=activity_dict["activity_portal_type"], id="-".join([activity_dict["activity_id"], user_id, DateTime().strftime("%Y%m%d%H%M%S%f")]))

        activity = getattr(self, activity_id)
        activity.setProperties({"Title":       activity_title,
                                "Description": activity_description})

        self.addItemInCourseMap(activity_id, map_position)
        self.addItemProperty(activity_id, activity_dict["activity_id"], activity_title, user_id, "", None)

    def detacherElement(self, ressource, createur, repertoire):
        LOG.info("----- detacherElement -----")
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

    def modifierInfosBoitePlan(self, idElement, param):
        LOG.info("----- modifierInfosBoitePlan -----")
        dico = self.getElementCours(idElement)
        for attribut in param.keys():
            dico[attribut] = param[attribut]
        self._elements_cours[idElement] = dico
        self.setElementsCours(self._elements_cours)
        self.setProperties({"DateDerniereModif": DateTime()})

    def modifierInfosElementPlan(self, idElement, titreElement):
        LOG.info("----- modifierInfosElementPlan -----")
        dico = self.getElementCours(idElement)
        dico["titreElement"] = titreElement
        self._elements_cours[idElement] = dico
        self.setElementsCours(self._elements_cours)
        self.setProperties({"DateDerniereModif": DateTime()})

    def ordonnerElementPlan(self, pplan):
        LOG.info("----- ordonnerElementPlan -----")
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

    def retirerElement(self, idElement):
        LOG.info("----- retirerElement -----")
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
            if not self.isInCourseMap(idElement):
                infos_element = self.getElementCours()
                infosElement = infos_element[idElement]
                self.detacherElement(idElement, infosElement["createurElement"], infosElement["typeElement"].replace(" ", ""))
                del infos_element[idElement]
        self.setProperties({"DateDerniereModif": DateTime()})

    def retirerElementPlan(self, idElement, listeElement=None, force_WIMS=False):
        LOG.info("----- retirerElementPlan -----")
        """ Fonction recursive qui supprime l'element idElement du plan, ainsi que tout son contenu si c'est un Titre."""
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

    def verifType(self, typeElement):
        LOG.info("----- verifType -----")
        return typeElement.replace(" ", "")

    def isStreamingAuthorized(self, streaming_id, request):
        LOG.info("----- ----- isStreamingAuthorized -----")
        if not request.has_key("HTTP_X_REAL_IP"):
            return False
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        return portal_jalon_wowza.isStreamingAuthorized(streaming_id, request["HTTP_X_REAL_IP"])

    def delElem(self, element):
        LOG.info("----- ----- delElem -----")
        del self._elements_cours[element]
        self.getElementCours()
        self.setElementsCours(self._elements_cours)

    #---------------------------------#
    # Course Activity (WIMS Activity) #
    #---------------------------------#
    def setListeClasses(self, valeur):
        LOG.info("----- setListeClasses -----")
        self.listeclasses = tuple(valeur)

    def authUser(self, quser=None, qclass=None, request=None):
        LOG.info("----- authUser -----")
        return jalon_utils.authUser(self, quser, qclass, request)

    def getDataCourseWimsActivity(self, user_id, course_id):
        LOG.info("----- getDataCourseWimsActivity -----")
        wims_classe_list = self.getListeClasses()
        can_delete = True if user_id in wims_classe_list[0] or self.isAuteur(user_id) else False

        course_author_data = self.getAuteur()

        #à finir ne tiens pas compte de si pas d'annuaire LDAP
        record_user_book_base = self.useJalonUtils("getBaseAnnuaire", {})
        course_author_record_user_link = self.useJalonUtils("getFicheAnnuaire", {"valeur": course_author_data,
                                                                                 "base":   record_user_book_base})

        is_course_author = self.isAuteur(user_id)
        can_delete_all_wims_classes_css = "" if is_course_author else "disabled"

        return {"course_name":                     self.getShortText(self.Title(), 80),
                "is_course_owner":                 self.isCourseOwner(user_id),
                "wims_classe_list":                wims_classe_list,
                "can_delete":                      can_delete,
                "course_author_fullname":          course_author_data["fullname"],
                "course_author_record_user_link":  course_author_record_user_link,
                "is_course_author":                is_course_author,
                "can_delete_all_wims_classes_css": can_delete_all_wims_classes_css}

    def purgerActivitesWims(self):
        LOG.info("----- purgerActivitesWims -----")
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
        LOG.info("----- getScoresWims -----")
        u"""Télécharger les notes de tous les examens WIMS créées par 'auteur' dans le cours."""
        dicoClasses = list(self.getListeClasses())[0]

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
            LOG.info("----- [jaloncours/getScoresWims] listeClasses :'%s'" % listeClasses)
            #for user in dicoClasses:
            #    if auteur == "All" or user == auteur:
            columns = "login,name,%s" % (",".join(liste_activitesWIMS))
            if auteur in dicoClasses:
                dico = {"qclass": dicoClasses[auteur],
                        "code": authMember,
                        "job": "getcsv",
                        "format": file_format,
                        "option": columns}
                LOG.info("----- [jaloncours/getScoresWims] callJob dico :'%s'" % dico)
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
                    if file_format == "xls":
                        # Pour le format xls, on remplace le séparateur décimal (.) par une virgule.
                        rep_wims = rep_wims.replace(".", ",")
                    # Si "fichier" n'est pas un JSON correct, ce doit bien etre un OEF.
                    retour = {"status": "OK", "nb_activity": len(liste_activitesWIMS), "data": rep_wims}

        else:
            retour = {"status": "not_relevant", "nb_activity": len(liste_activitesWIMS)}

        return retour

    def supprimerActivitesWims(self, utilisateur="All", request=None):
        LOG.info("----- supprimerActivitesWims -----")
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
                    LOG.info("----- [jaloncours/supprimerActivitesWims] suppression de '%s'" % element)
                    liste_activitesWIMS.append(idElement)

                    # On parcourt ensuite les exo des activitées retirées, pour que chaque exercice n'y fasse plus référence dans ses "relatedITEMS"
                    # retire l'activité des relatedItems pour ses exercices et ses documents.
                    activite.retirerTousElements(force_WIMS=True)

                    # Supprime l'activité (du plan du cours et du cours)
                    self.retirerElementPlan(idElement, force_WIMS=True)
                    # Supprime l'activité des actus du cours
                    self.delActu(idElement)

                    ### A utiliser dans un patch correctif :
                    #(on refait ce que fait normalement retirerElementPlan, dans le cas ou l'element n'est plus dans le plan mais toujours dans _elements_cours) :
                    if idElement in self._elements_cours:
                        self.manage_delObjects(idElement)
                        del self._elements_cours[idElement]

        # Supprime toutes les classes du serveur WIMS
        listeClasses = list(self.getListeClasses())
        removing_classes = []
        dico = listeClasses[0]
        LOG.info("----- [jaloncours/supprimerActivitesWims] Ancienne liste :'%s'" % listeClasses)
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
        LOG.info("----- [jaloncours/supprimerActivitesWims] Nouvelle liste :'%s'" % new_listeClasses)
        self.setListeClasses(new_listeClasses)

        # Renvoit le nombre d'activités supprimées.
        return len(liste_activitesWIMS)

    #autoriserAffichageSousObjet : définit si l'affichage de l'objet 'idElement' est autorisé ou pas.
    # utile pour empecher l'affichage des activités vides par exemple
    def autoriserAffichageSousObjet(self, idElement, typeElement=None):
        LOG.info("----- autoriserAffichageSousObjet -----")
        ret = {"val": True, "reason": ""}
        if not typeElement:
            typeElement = self.getTypeSousObjet(idElement)
        if typeElement in ['AutoEvaluation', 'Examen']:
            # dans le cas d'une activité WIMS, on n'affiche l'objet que s'il contient des exercices.
            infosActivite = self.getSousObjet(idElement)
            ret = infosActivite.autoriser_Affichage()
        return ret

    #pour montrer les nouveaux éléments dans le cours
    def isNouveau(self, idElement, listeActualites=None):
        LOG.info("----- isNouveau -----")
        if listeActualites is None:
            LOG.info("----- ***** Not listeActualites")
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

    #---------------------------------#
    # Course Activity (Adobe Connect) #
    #---------------------------------#
    def connect(self, methode, param):
        LOG.info("----- connect -----")
        return self.portal_connect.__getattribute__(methode)(param)

    def getSessionConnect(self, user_id, repertoire):
        LOG.info("----- ----- getSessionConnect -----")
        portal = self.portal_url.getPortalObject()
        home = getattr(getattr(portal.Members, user_id), repertoire)
        return home.getSessionConnect(user_id)

    def getReunion(self, user_id, request, repertoire):
        LOG.info("----- ----- getReunion -----")
        portal = self.portal_url.getPortalObject()
        home = getattr(getattr(portal.Members, user_id), repertoire)
        return home.getReunion(user_id)

    #---------------------#
    # Course Participants #
    #---------------------#
    def getCoLecteursCours(self):
        LOG.info("----- getCoLecteursCours -----")
        retour = []
        for username in self.getCoLecteurs():
            retour.append(self.useJalonUtils("getInfosMembre", {"username": username}))
        return retour

    def addLecteurs(self, form):
        LOG.info("----- addLecteurs -----")
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été ajouté comme lecteur du cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), portal.absolute_url(), portal.Title())
        lecteurs = list(self.getCoLecteurs())
        usernames = form["username"].split(",")
        if usernames != ['']:
            for username in usernames:
                if not username in lecteurs:
                    lecteurs.append(username)
                    infosMembre = self.useJalonUtils("getInfosMembre", {"username": username})
                    self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                                "objet":   "Vous avez été ajouté à un cours",
                                                                "message": message}})
            self.coLecteurs = tuple(lecteurs)
        self.setProperties({"DateDerniereModif": DateTime()})

    def deleteLecteurs(self, form):
        LOG.info("----- deleteLecteurs -----")
        lecteurs = []
        if "auteur-actu" in form:
            lecteurs = form["auteur-actu"]
        ancienLecteurs = set(self.getCoLecteurs())
        supprLecteurs = ancienLecteurs.difference(set(lecteurs))
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été retiré du cours "%s" ayant pour auteur %s ou vous êtiez lecteur.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())
        for idMember in supprLecteurs:
            infosMembre = self.useJalonUtils("getInfosMembre", {"username": idMember})
            self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                        "objet":   "Vous avez été retiré d'un cours",
                                                        "message": message}})
        self.coLecteurs = tuple(lecteurs)
        self.setProperties({"DateDerniereModif": DateTime()})

    def getInfosGroupe(self):
        LOG.info("----- getInfosGroupe -----")
        groupe = self.getGroupe()
        return jalon_utils.getIndividus(list(groupe), "listdict")

    def getInfosLibre(self):
        LOG.info("----- getInfosLibre -----")
        libre = self.getInscriptionsLibres()
        return jalon_utils.getIndividus(list(libre), "listdict")

    def getInfosInvitations(self):
        LOG.info("----- getInfosInvitations -----")
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

    def getAffichageFormation(self):
        LOG.info("----- getAffichageFormation -----")
        listeFormations = self.getAffichageFormations()
        nbEtuFormations = self.getNbEtuFormation(listeFormations)
        return {"nbFormations": len(listeFormations),
                "nbEtuFormations": nbEtuFormations}

    def getAffichageFormations(self):
        LOG.info("----- getAffichageFormations -----")
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
        res.sort()
        return res

    def getNbEtuFormation(self, listeFormations):
        LOG.info("----- getNbEtuFormation -----")
        nbEtuFormations = 0
        for formation in listeFormations:
            nbEtuFormations = nbEtuFormations + int(formation[2])
        return nbEtuFormations

    def getAffichageInscriptionIndividuelle(self, typeAff):
        LOG.info("----- getAffichageInscriptionIndividuelle -----")
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
        LOG.info("----- getInfosListeAcces -----")
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
        return res

    def getRechercheAcces(self):
        LOG.info("----- getRechercheAcces -----")
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

    def addOffreFormations(self, elements):
        LOG.info("----- addOffreFormations -----")
        listeOffreFormations = list(self.getListeAcces())
        for formation in elements:
            if not formation in listeOffreFormations:
                listeOffreFormations.append(formation)
        self.listeAcces = tuple(listeOffreFormations)
        self.setProperties({"DateDerniereModif": DateTime()})

    def deleteOffreFormations(self, elements):
        LOG.info("----- deleteOffreFormations -----")
        self.listeAcces = tuple(elements)
        self.setProperties({"DateDerniereModif": DateTime()})

    def addInscriptionsNomminatives(self, form):
        LOG.info("----- addInscriptionsNomminatives -----")
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été inscrit au cours "%s" ayant pour auteur %s.\n\nPour accéder à ce cours, connectez vous sur %s (%s), le cours est listé dans votre espace "Mes cours".\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title(), portal.absolute_url(), portal.Title())
        nomminatives = list(self.getGroupe())
        usernames = form["username"].split(",")
        if usernames != ['']:
            for username in usernames:
                if not username in nomminatives:
                    nomminatives.append(username)
                    infosMembre = self.useJalonUtils("getInfosMembre", {"username": username})
                    self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                                "objet":   "Vous avez été inscrit à un cours",
                                                                "message": message}})
        self.setGroupe(tuple(nomminatives))
        self.setProperties({"DateDerniereModif": DateTime()})

    def deleteInscriptionsNomminatives(self, form):
        LOG.info("----- deleteInscriptionsNomminatives -----")
        nomminatives = []
        if "etu_groupe" in form:
            nomminatives = form["etu_groupe"]
        ancienNomminatives = set(self.getGroupe())
        supprNomminatives = ancienNomminatives.difference(set(nomminatives))
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été désinscrit du cours "%s" ayant pour auteur %s.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())
        for idMember in supprNomminatives:
            infosMembre = self.useJalonUtils("getInfosMembre", {"username": idMember})
            self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                        "objet":   "Vous avez été désincrit d'un cours",
                                                        "message": message}})
        self.setGroupe(tuple(nomminatives))
        self.setProperties({"DateDerniereModif": DateTime()})

    def addInvitationsEmail(self, form):
        LOG.info("----- addInvitationsEmail -----")
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
                    self.useJalonUtils("envoyerMail", {"form": {"a":       emailInvit,
                                                                "objet":   "Vous avez été inscrit à un cours",
                                                                "message": message}})
                self.setInvitations(tuple(invitations))
        self.setProperties({"DateDerniereModif": DateTime()})

    def deleteInvitationsEmail(self, form):
        LOG.info("----- deleteInvitationsEmail -----")
        invitations = []
        if "etu_email" in form:
            invitations = form["etu_email"]
        ancienInvitations = set(self.getInvitations())
        supprInvitations = ancienInvitations.difference(set(invitations))
        portal = self.portal_url.getPortalObject()
        message = 'Bonjour\n\nVous avez été désinscrit du cours "%s" ayant pour auteur %s.\n\nCordialement,\n%s.' % (self.Title(), self.getAuteur()["fullname"], portal.Title())
        for idMember in supprInvitations:
            infosMembre = self.useJalonUtils("getInfosMembre", {"username": idMember})
            self.useJalonUtils("envoyerMail", {"form": {"a":       infosMembre["email"],
                                                        "objet":   "Vous avez été désincrit d'un cours",
                                                        "message": message}})
        self.setInvitations(tuple(invitations))
        self.setProperties({"DateDerniereModif": DateTime()})

    def rechercheApogee(self, recherche, termeRecherche):
        LOG.info("----- rechercheApogee -----")
        if not termeRecherche:
            return None
        termeRecherche.strip()
        termeRecherche = "%" + termeRecherche + "%"
        termeRecherche = termeRecherche.replace(" ", "% %")
        listeRecherche = termeRecherche.split(" ")

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
        LOG.info("----- rechercherUtilisateur -----")
        return jalon_utils.rechercherUtilisateur(username, typeUser, match, json)

    def hasParticipants(self):
        LOG.info("----- hasParticipants -----")
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
        LOG.info("----- telechargerListingParticipants -----")
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

    #--------------------#
    # Course Life - News #
    #--------------------#
    def getActualitesCours(self, toutes=None):
        LOG.info("----- getActualitesCours -----")
        actualites = []
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
        LOG.info("----- getActuCoursFull -----")
        actualites = []

        listeActualites = list(self.getActualites())
        listeActualites.sort(lambda x, y: cmp(y["dateActivation"], x["dateActivation"]))
        infos_elements = self.getElementCours()

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
        LOG.info("----- setActuCours -----")
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
        LOG.info("----- delActu -----")
        newActu = []
        listeActualites = list(self.getActualites())
        for actu in listeActualites:
            if idElement != actu["reference"]:
                newActu.append(actu)
        self.actualites = tuple(newActu)
        self.setProperties({"DateDerniereModif": DateTime()})

    #Pour passer l'information dans le portal_catalog et l'utiliser dans la liste de cours
    def getDateDerniereActu(self):
        LOG.info("----- getDateDerniereActu -----")
        try:
            return DateTime(self.getLastDateActu())
        except:
            return DateTime()

    def setDateDerniereActu(self, listeActualites=None):
        LOG.info("----- setDateDerniereActu -----")
        retour = self.created()
        paramDate = "dateActivation"
        if listeActualites is None:
            listeActualites = self.getActualitesCours(True)["listeActu"]
            paramDate = "date"
        for actualite in listeActualites:
            if cmp(actualite[paramDate], retour) > 0:
                retour = actualite[paramDate]
        self.dateDerniereActu = retour

    #---------------------#
    # Course Life - Forum #
    #---------------------#
    def toPloneboardTime(self, context, request, time_=None):
        LOG.info("----- toPloneboardTime -----")
        """Return time formatted for Ploneboard."""
        return toPloneboardTime(context, request, time_)

    def getDicoForums(self, all=None):
        LOG.info("----- getDicoForums -----")
        listeForums = list(self.forum.objectValues())
        listeForums.sort(lambda x, y: cmp(y.modified(), x.modified()))
        if len(listeForums) > 5:
            return {"nbForums":    len(listeForums),
                    "listeForums": listeForums[:5]}
        else:
            return {"nbForums":    len(listeForums),
                    "listeForums": listeForums}

    #------------------------#
    # Course Life - Announce #
    #------------------------#
    def getAnnonces(self, authMember, request, personnel, all=None):
        LOG.info("----- getAnnonces -----")
        annonces = []
        listeAnnonces = list(self.annonce.objectValues())
        listeAnnonces.sort(lambda x, y: cmp(y.modified(), x.modified()))
        if listeAnnonces and personnel and all:
            return {"listeAnnonces": listeAnnonces, "nbAnnonces": len(listeAnnonces)}
        elif listeAnnonces and personnel:
            return {"listeAnnonces": [listeAnnonces[0]], "nbAnnonces": len(listeAnnonces)}

        groupes = []
        diplomes = []
        portal = self.portal_url.getPortalObject()
        portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")
        try:
            idMember = authMember.getId()
        except:
            idMember = authMember
        if idMember and not "@" in idMember:
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
                #pas besoin de la ligne suivante, si tout est decoche c'est une annonce juste pour l'auteur lui meme
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
        if annonces and all:
            return {"listeAnnonces": annonces, "nbAnnonces": len(listeAnnonces)}
        elif annonces:
            return {"listeAnnonces": [annonces[0]], "nbAnnonces": len(listeAnnonces)}
        else:
            return {"listeAnnonces": [], "nbAnnonces": 0}

    def getPublicsAnnonce(self):
        LOG.info("----- getPublicsAnnonce -----")
        res = self.getInfosListeAcces()
        if self.getCoAuteurs():
            res.append(["Tous les co-auteurs", "coauteurs", len(self.getCoAuteurs()), "coauteurs"])
        if self.getCoLecteurs():
            res.append(["Tous les co-lecteurs", "colecteurs", len(self.getCoLecteurs()), "colecteurs"])
        return res

    def supprimerAnnonce(self, annonce):
        LOG.info("----- supprimerAnnonce -----")
        self.annonce.manage_delObjects([annonce])

    #--------------------------------#
    # Course Glossary & Bibliography #
    #--------------------------------#
    def getGloBib(self, glo_bib):
        LOG.info("----- getGloBib -----")
        dicoLettres = {}
        if glo_bib == "glossaire":
            elements = self.getGlossaire()
        else:
            elements = self.getBibliographie()
        if elements:
            infos_element = self.getElementCours()

        portal_link = self.portal_url.getPortalObject().absolute_url()
        for idElement in elements:
            info_element = infos_element.get(idElement)
            if info_element:
                info_element["idElement"] = idElement
                lettre = info_element["titreElement"][0].upper()
                info_element["urlElement"] = "%s/Members/Externes/%s/%s" % (portal_link, idElement, info_element["createurElement"])
                if not lettre in dicoLettres:
                    dicoLettres[lettre] = [info_element]
                else:
                    dicoLettres[lettre].append(info_element)
        return dicoLettres

    #-------------------#
    # Course indicators #
    #-------------------#
    def insererConsultation(self, user, type_cons, id_cons):
        LOG.info("----- insererConsultation -----")
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
        LOG.info("----- getConsultation -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByCoursByDate(self.getId())

    def getConsultationByCoursByUniversityYearByDate(self, DATE_CONS_YEAR, FILTER_DATE, PUBLIC_CONS):
        LOG.info("----- getConsultationByCoursByUniversityYearByDate -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByCoursByUniversityYearByDate(self.getId(), DATE_CONS_YEAR, FILTER_DATE, PUBLIC_CONS)

    def getConsultationByCoursByYearForGraph(self):
        LOG.info("----- getConsultationByCoursByYearForGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByCoursByYearForGraph(self.getId())

    def getConsultationByCoursByUniversityYearForGraph(self):
        LOG.info("----- getConsultationByCoursByYearForGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByCoursByUniversityYearForGraph(self.getId())

    def getFrequentationByCoursByUniversityYearByDateForGraph(self, PUBLIC_CONS):
        LOG.info("----- getFrequentationByCoursByUniversityYearForGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getFrequentationByCoursByUniversityYearByDateForGraph(self.getId(), PUBLIC_CONS)

    def getConsultationElementsByCours(self, elements_list, elements_dict):
        LOG.info("----- getConsultationElementsByCours -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationElementsByCours(self.getId(), elements_list=elements_list, elements_dict=elements_dict)

    def getConsultationByElementByCours(self, element_id):
        LOG.info("----- getConsultationByElementByCours -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByElementByCours(self.getId(), element_id)

    def getConsultationByElementByCoursByYearForGraph(self, element_id):
        LOG.info("----- getConsultationByElementByCoursByYearForGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByElementByCoursByYearForGraph(self.getId(), element_id)

    def getConsultationByElementByCoursByUniversityYearForGraph(self, element_id):
        LOG.info("----- getConsultationByElementByCoursByUniversityYearForGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.getConsultationByElementByCoursByUniversityYearForGraph(self.getId(), element_id)

    def genererGraphIndicateurs(self, months_dict):
        LOG.info("----- genererGraphIndicateurs -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.genererGraphIndicateurs(months_dict)

    def genererFrequentationGraph(self, months_dict):
        self.plone_log("genererFrequentationGraph -----")
        portal = self.portal_url.getPortalObject()
        return portal.portal_jalon_bdd.genererFrequentationGraph(months_dict)

# enregistrement dans la registery Archetype
registerATCT(JalonCours, PROJECTNAME)
