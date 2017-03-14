# -*- coding: utf-8 -*-
"""Gestion des elements de type Feuille (autoevaluation) et Examen WIMS dans un cours Jalon."""

from zope.interface import implements

from Products.Archetypes.public import *
# from Products.ATExtensions.ateapi import *

from Products.ATContentTypes.content.document import ATDocument, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.utils import getToolByName

from DateTime import DateTime
from persistent.dict import PersistentDict

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonCoursWims

# import os
import json
import copy
import jalon_utils
from jalon_activity import JalonActivity

# Messages de debug :
from logging import getLogger
LOG = getLogger('[jaloncourswims]')
"""
# Log examples :
LOG.debug('debug message')
LOG.info('info message')
LOG.warn('warn message')
LOG.error('error message')
LOG.critical('critical message')
"""

languages = DisplayList((
    # ('', _(u'Laisser les apprenants choisir')),
    ('', _(u'Par défaut (français)')),
    ('fr', 'Français'),
    ('en', 'English'),
    ('it', 'Italiano'),
    ('cn', '简体中文(中国)'),
))
# Correspondance des langues Plone <=> WIMS :
# zh-cn <=> cn
# (les autres code de langues correspondent)


JalonCoursWimsSchema = ATDocumentSchema.copy() + Schema((
    StringField("typeWims",
                required=False,
                accessor="getTypeWims",
                searchable=False,
                widget=StringWidget(label=_(u"Type de l'activité"),
                                    description=_(u"Type de l'objet JalonCoursWims (feuille (Entrainement) ou Examen)"),
                                    )
                ),
    StringField("idFeuille",
                required=False,
                accessor="getIdFeuille",
                searchable=False,
                widget=StringWidget(label=_(u"Identifiant Wims de la feuille"),
                                    description=_(u"Numero de la feuille sur WIMS"),
                                    )
                ),
    StringField("idExam",
                required=False,
                accessor="getIdExam",
                searchable=False,
                widget=StringWidget(label=_(u"Identifiant Wims de l'examen"),
                                    description=_(u"Numero de l'examen sur WIMS"),
                                    )
                ),
    StringField("note_max",
                required=True,
                accessor="getNoteMax",
                searchable=False,
                default="100",
                widget=StringWidget(label=_(u"Barême"),
                                    description=_(u"Un quotient sera effectu&eacute; pour calculer la note en fonction de ce bar&ecirc;me"),
                                    placeholder=_(u"Un nombre entier (obligatoire)")
                                    )
                ),
    StringField("duree",
                required=True,
                accessor="getDuree",
                searchable=False,
                default="60",
                widget=IntegerWidget(label=_(u"Durée de l’examen (en minutes)"),
                                     description=_(u"Un compte &agrave; rebours d&eacute;marera d&egrave;s l&rsquo;affichage de la premi&egrave;re question. Une fois atteint, l&rsquo;&eacute;tudiant ne pourra plus r&eacute;pondre."),
                                     placeholder=_(u"Durée en minutes (obligatoire)")
                                     )
                ),
    StringField("attempts",
                required=True,
                accessor="getAttempts",
                searchable=False,
                default="1",
                widget=StringWidget(label=_(u"Nombre de passages autorisés"),
                                    description=_(u"Nombre de fois o&ugrave; l&rsquo;&eacute;tudiant pourra passer cet examen"),
                                    placeholder=_(u"Un nombre entier (obligatoire)")
                                    )
                ),
    LinesField("listeExercices",
               required=False,
               accessor="getListeExercices",
               searchable=False,
               widget=LinesWidget(label=_(u"Liste des exercices"),
                                  description=_(u"Liste des exercices de l&rsquo;entrainement / examen"),
                                  visible={'view': 'visible', 'edit': 'invisible'},
                                  )
               ),
    LinesField("listeSujets",
               required=False,
               accessor="getListeSujets",
               searchable=False,
               widget=LinesWidget(label=_(u"Liste des documents"),
                                  description=_(u"Liste des documents de cette activité"),
                                  visible={'view': 'visible', 'edit': 'invisible'},
                                  )
               ),
    StringField("dateAff",
                required=False,
                accessor="getDateAff",
                searchable=False,
                widget=CalendarWidget(label=_(u"Date d'affichage"),
                                      description=_(u"Date a laquelle cette activite s'affiche"),
                                      )
                ),
    StringField("dateMasq",
                required=False,
                accessor="getDateMasq",
                searchable=False,
                widget=CalendarWidget(label=_(u"Date à laquelle cette activité est masquée"),
                                      description=_(u"Date servant &agrave; masquer cette activit&eacute;"),
                                      )
                ),
    StringField("cut_hours",
                required=False,
                accessor="getCut_hours",
                searchable=False,
                widget=StringWidget(label=_(u"Heures de coupure"),
                                    description=_(u"Heures pendant lesquelles l&rsquo;examen ne sera pas accessible."),
                                    )
                ),
    StringField("verrou",
                required=False,
                accessor="getVerrou",
                searchable=False,
                widget=StringWidget(label=_(u"Mot de passe"),
                                    description=_(u"Ajoutez un mot de passe pour s&eacute;curiser votre examen."),
                                    )
                ),
    StringField("wims_lang",
                required=False,
                accessor='getWims_lang',
                searchable=False,
                widget=SelectionWidget(label=_(u"Langue des exercices"),
                                       description=_(u"Langue dans laquelle s'affichera l&rsquo;interface des exercices. La tol&eacute;rance des exercices &agrave; r&eacute;ponse ouverte d&eacute;pendra de cette langue."),
                                       ),
                vocabulary=languages
                ),
    StringField("dateDerniereModif",
                required=False,
                accessor="getDateDerniereModif",
                searchable=False,
                widget=StringWidget(label=_(u"Date de dernière modification"),
                                    description=_(u"Date de dernière modification"),
                                    )),

    # pour ajouter une propriete modifiable, il faut l'ajouter egalement dans "activite_edit.py"

    # RecordField("infos_element",
    #            required=False,
    #            accessor="getInfosElement",
    #            searchable=False,
    #            widget=RecordWidget(label=_(u"Liste des informations sur les éléments d'un cours"),
    #                                visible={'view': 'visible', 'edit': 'invisible'},)
    #            )
))

# Liste des type d'elements susceptibles d'etre ajoutés à un jaloncoursWIMS
_dicoRep = {"Image"                    : "Fichiers",
            "File"                     : "Fichiers",
            "Page"                     : "Fichiers",

            "Lienweb"                  : "Externes",
            "Lien web"                 : "Externes",
            "Lecteurexportable"        : "Externes",
            "Lecteur exportable"       : "Externes",
            "Referencebibliographique" : "Externes",
            "Reference bibliographique": "Externes",

            "Presentationssonorisees"  : "Sonorisation",
            "Presentations sonorisees" : "Sonorisation",

            "ExerciceWims"             : "Wims",
            "ExercicesWims"            : "Wims",
            "Exercice Wims"            : "Wims"
            }


class JalonCoursWims(JalonActivity, ATDocument):
    u"""
    Une autoevaluation ou un examen pour Jalon.

    ce qui correspond à une feuille d'entrainement ou un couple [feuille+examen] pour Wims

    """

    implements(IJalonCoursWims)
    meta_type = 'JalonCoursWims'
    schema = JalonCoursWimsSchema

    schema['description'].required = False
    schema['description'].default_output_type = 'text/x-html-safe'
    schema['description'].allowable_content_types = ('text/plain', 'text/html')
    schema['description'].widget.label = _(u"Consigne")
    schema['description'].widget.description = _(u"Quelques consignes que devront suivre vos &eacute;tudiants pour travailler sur cette activit&eacute;.")

    schema['text'].required = False
    schema['text'].mode = "r"

    # Liste des elements ajoutés à ce jalonCoursWims
    _infos_element = {}

    def __init__(self, *args, **kwargs):
        """Initialize JalonCoursWims."""
        # LOG.info('__init__')
        super(JalonCoursWims, self).__init__(*args, **kwargs)
        self.setDocumentsProperties({})

    # #-------------------# #
    #  Fonctions générales  #
    # #-------------------# #

    def addMySpaceItem(self, folder_object, item_id, item_type, user_id, display_item, map_position, display_in_plan, portal_workflow):
        """Ajoute un element de Mes ressources et met a jour les related items de l'activité et de l'élément."""
        # LOG.info("----- addMySpaceItem -----")
        item = super(JalonCoursWims, self).addMySpaceItem(folder_object, item_id, item_type, user_id, display_item, map_position, display_in_plan, portal_workflow)
        if folder_object.getId() == "Wims":
            liste = "Exercices"
            idClasse = self.getClasse()

            item_title = item["item_title"].decode("utf-8")
            item_object = item['item_object']

            # Exo Externes
            if item_id.startswith("externe-"):

                permalien = item_object.permalink
                dico = {"job": "putexo", "code": user_id, "qclass": idClasse, "qsheet": self.idFeuille}
                if permalien != "":
                    # exemple de permalien : module=U2/analysis/oeffourier.fr&exo=addfourier2,addfourier1,addfourier4,addfourier3&qnum=1&qcmlevel=3
                    parsed_permalien = permalien.split("&", 1)
                    if len(parsed_permalien) == 1:
                        # par defaut, si aucun parametre n'a ete defini, on definie au minima le parametre de sévérité
                        parsed_permalien.append("qcmlevel=1")
                    donnees_exercice = u"%s\nparams=%s\npoints=%s\nweight=%s\ntitle=%s\ndescription=%s" % (parsed_permalien[0],
                                                                                                           parsed_permalien[1],
                                                                                                           "10",
                                                                                                           "1",
                                                                                                           item_title,
                                                                                                           "")
                    dico["data1"] = donnees_exercice.encode("utf-8")
                    rep_wims = self.wims("callJob", dico)
                else:
                    rep_wims = '{"status": "ERROR", "message": "pas de permalien pour cet exercice externe"}'
                rep_wims = self.wims("verifierRetourWims", {"rep": rep_wims, "fonction": "jaloncourswims.py/addMySpaceItem", "message": "parametres de la requete : %s" % dico})
            # Exo Internes
            else:
                if item_id.startswith("groupe-"):
                    listeExos = item_object.getListeIdsExos()
                    qnum = item_object.getQnum()
                else:
                    listeExos = [item_id]
                    qnum = "1"

                if self.typeWims != "Examen":
                    afficher_reponses = True
                else:
                    afficher_reponses = False

                rep_wims = self.wims("lierExoFeuille", {"authMember": user_id, "title": item_title,
                                                        "qclass": idClasse, "qsheet": self.idFeuille,
                                                        "listeExos": listeExos, "qnum": qnum,
                                                        "afficher_reponses": afficher_reponses})

            if rep_wims['status'] != "OK":
                # Attention : si la creation n'a pas eu lieu coté WIMS, il ne faut rien créer côté Jalon.
                portal_jalon_properties = getToolByName(self, 'portal_jalon_properties')
                contact_link = portal_jalon_properties.getLienContact()
                admin_link = u"%s?subject=[%s] Erreur d'insertion exercice WIMS&amp;body=exercice : %s%%0D%%0DDécrivez précisément votre souci svp:\n" % (
                    contact_link["contact_link"], contact_link["portal_title"], item_id)
                message = _(u'Une erreur est survenue. Merci de <a href="%s"><i class="fa fa-envelope-o"></i>contacter un administrateur</a> svp.' % admin_link)
                message = "<p>%s</p><p><strong>%s:</strong> %s</p>" % (message, _(u"Information sur l'erreur "), rep_wims['message'])
                self.plone_utils.addPortalMessage(message, type='error')

                # L'exercice n'est pas ajouté.
                # LOG.info("\n####### jaloncourswims/addMySpaceItem -- Attention : '%s'\n" % rep_wims['message'])
                self.removeRelatedExercice(item_object)
                # message = _(u"Une erreur est survenue. Merci de contacter l'administrateur de cette plateforme, en fournissant tous les détails possibles permettant de reproduire cette erreur svp.")
                # message = "%s<br/><strong>%s:</strong>%s" % (message, _(u"Information sur l'erreur "), rep_wims['message'])
                # self.plone_utils.addPortalMessage(message, type='error')
                return item

        else:
            liste = "Sujets"
        """Ajoute l'element à la liste des items de l'activité."""
        self.addItemProperty(item["item_id_no_dot"], item["item_type"], item["item_title"], user_id, display_item, item["item_complement"], liste)

    def addItemProperty(self, item_id, item_type, item_title, item_creator, display_item, complement_element, liste):
        """Ajoute un element aux liste des items d'une activité."""
        # LOG.info("----- addItemProperty (liste = %s) -----" % liste)

        items_properties = self.getDocumentsProperties()
        if item_id not in items_properties:
            items_properties[item_id] = {"titreElement":    item_title,
                                         "typeElement":     item_type,
                                         "createurElement": item_creator,
                                         "affElement":      display_item,
                                         "masquerElement":  ""}

            if complement_element:
                items_properties[item_id]["complementElement"] = complement_element
            # setDocumentsProperties permet de s'assurer que les données sont stockées de manière persistante.
            self.setDocumentsProperties(items_properties)

        if liste == "Exercices":
            listeExercices = list(self.getListeExercices())
            listeExercices.append(item_id)
            setattr(self, "listeExercices", tuple(listeExercices))
            message = _(u"L'exercice '%s' a bien été ajouté." % item_title.decode("utf-8"))
        else:
            listeSujets = list(self.getListeSujets())
            listeSujets.append(item_id)
            setattr(self, "listeSujets", tuple(listeSujets))
            message = _(u"'%s' a bien été ajouté aux documents enseignants." % item_title.decode("utf-8"))

        self.plone_utils.addPortalMessage(message, type='success')

    def checkRoles(self, user=None, action="edit", function=""):
        u"""Permet de vérifier si l'utilisateur courant a le droit d'accéder à l'activité.

        # Si le droit n'est pas accordé, un message est affiché à l'utilisateur.
        # Si on suspecte une tentative de fraude, l'administrateur recoit un message.
        # action indique si l'utilisateur tente d'y accéder en lecture ("view") ou écriture ("edit")

        """
        # LOG.info("----- checkRoles -----")
        if user is None:
            membership_tool = self.portal_url.getPortalObject().portal_membership
            user = membership_tool.getAuthenticatedMember()
        user_roles = user.getRolesInContext(self)
        if 'Owner' in user_roles or 'Manager' in user_roles:
            return True
        else:
            if 'Anonymous' in user_roles:
                # Normalement, le mecanisme de gestion des droits de Plone ne pemretrra de toute facon pas un anonyme d'accéder à un exercice.
                # Mais ceci peux tout de même se produire dans le cas ou un exercice a été rendu public via son insertion dans un cours public justement.
                message = _(u"Vous êtes déconnecté. Merci de vous connecter pour accéder à cette page.")
                mess_type = "info"
            else:
                # TODO : Ici il faudrait vérifier qu'un etudiant malveillant ne puisse pas modifier une activité !
                message = _(u"Vous tentez d'accéder à une page qui ne vous appartient pas. Une suspicion de fraude vous concernant a été envoyée à l'administrateur du site.")
                mess_type = "alert"
                self.aq_parent.wims("verifierRetourWims", {"rep": '{"status":"ERROR", "message":"checkRoles Failed", "activity_ID":"%s"}' % self.getId(),
                                                           "fonction": "jaloncourswims.py/checkRoles in %s" % function,
                                                           "message": "Suspicion de fraude de l'utilisateur %s" % user.getId(),
                                                           "requete": "%s" % self.absolute_url(),
                                                           "jalon_request": ""
                                                           })

        self.plone_utils.addPortalMessage(message, type=mess_type)
        return False

    def detachExercice(self, item_id, ordre):
        """Supprime l'exercice de l'activité, puis met à jour les relatedItems"""
        # LOG.info("----- detachExercice -----")

        # On vérifie que l'utilisateur connecté a bien le droit de modifier l'activité.
        membership_tool = self.portal_url.getPortalObject().portal_membership
        authMember = membership_tool.getAuthenticatedMember()
        if not self.checkRoles(user=authMember, function="detachExercice"):
            return None

        document_properties = self.getDocumentsProperties()
        item_props = document_properties[item_id]

        # Supprime l'exercice de la feuille côté WIMS
        idClasse = self.getClasse()
        idFeuille = self.getIdFeuille()
        idExo = int(ordre) + 1
        item_title = item_props["titreElement"].decode("utf-8")
        dico = {"authMember": authMember.getId(),
                "qclass": idClasse,
                "qsheet": idFeuille,
                "qexo": idExo,
                "jalon_URL": self.absolute_url()}
        resp = self.wims("retirerExoFeuille", dico)
        # resp = {"status":"OK"}
        if resp["status"] != "OK":
            message = _(u"Une erreur est survenue. L'exercice '${item_title}' n'a pas été détaché",
                        mapping={'item_title': item_title})
            self.plone_utils.addPortalMessage(message, type='error')
        else:

            # Puisque la suppression est effective coté WIMS, on le détache côté Jalon :

            del document_properties[item_id]
            self.setDocumentsProperties(document_properties)

            exos_list = list(self.getListeExercices())
            exos_list.remove(item_id)
            self.setListeExercices(tuple(exos_list))

            # Puis on met à jour les related Items
            if item_id.split("-")[0] != "recover":
                item_object = getattr(getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), item_props["createurElement"]), "Wims"), item_id)
                self.removeRelatedExercice(item_object)

            message = _(u"L'exercice '${item_title}' a bien été détaché de cette activité.",
                        mapping={'item_title': item_title})
            self.plone_utils.addPortalMessage(message, type='success')

    def removeRelatedExercice(self, item_object):
        """Retire l'exercice item_object des related_items de l'activité, et inversement."""
        # LOG.info("----- removeRelatedExercice -----")

        item_relatedItems = item_object.getRelatedItems()
        if self in item_relatedItems:
            item_relatedItems.remove(self)
            item_object.setRelatedItems(item_relatedItems)
            item_object.reindexObject()

        activity_relatedItems = self.getRelatedItems()
        if item_object in activity_relatedItems:
            activity_relatedItems.remove(item_object)
            self.setRelatedItems(activity_relatedItems)
            self.reindexObject()

    def getDisplayProfile(self, profile_id=None):
        """get Display Profile."""
        # LOG.info("----- getDisplayProfile -----")
        deposit_box_profil = profile_id or self.getProfile() or "standard"
        return self._profile_title[deposit_box_profil]

    def getCrumbs(self, sub_page=""):
        """Get crumbs for some jaloncourswims subpages."""
        # LOG.info("----- getCrumbs -----")
        portal = self.portal_url.getPortalObject()
        parent = self.aq_parent
        self_link = self.absolute_url()
        response = [{"title": _(u"Mes cours"),
                     "icon":  "fa fa-university",
                     "link":  "%s/mes_cours" % portal.absolute_url()},
                    {"title": parent.Title(),
                     "icon":  "fa fa-book",
                     "link":  parent.absolute_url()},
                    {"title": self.Title(),
                     "icon":  self.getIconClass(),
                     "link":  self_link}]
        if sub_page == "edit":
            response.append({"title": _(u"Propriétés de l'activité"), "icon":  "fa fa-edit", "link": "%s/edit_wims_activity_form" % self_link})
        if sub_page == "import":
            response.append({"title": _(u"Importer des exercices"), "icon":  "fa fa-level-down", "link": "%s/import_wims_activity_form" % self_link})
        return response

    def getIconClass(self):
        """Return icon adaptated to activity type (Training or Exam)."""
        # LOG.info("----- getIconClass -----")
        return "fa fa-gamepad no-pad" if self.getId().startswith("AutoEvaluation-") else "fa fa-graduation-cap"

    """def getCourseItemProperties(self, key=None):
        # Get Course Item Properties (alias to getDocumentsProperties(key)).
        # LOG.info("----- getCourseItemProperties -----")
        return self.getDocumentsProperties(key)
    """

    def getDocumentsList(self):
        """Fournit la liste de tous les document enseignants (requis par jalon_activity)."""
        # LOG.info("----- getDocumentsList -----")
        # return self._infos_element.keys()
        return self.getListeSujets()

    def setDocumentsProperties(self, infos_element):
        """Met a jour les propriétés des sous-éléments de l'activité, en s'assurant au passage que les données sont persistantes."""
        # LOG.info("----- setDocumentsProperties -----")
        if type(self._infos_element).__name__ != "PersistentMapping":
            self._infos_element = PersistentDict(infos_element)
        else:
            self._infos_element = infos_element

    def editCourseItemVisibility(self, item_id, item_date, item_property_name, is_update_from_title=False):
        u"""Modifie la visibilité de l'activité ("item_property_name" fournit l'info afficher / masquer)."""
        # LOG.info("----- editCourseItemVisibility -----")

        portal = self.portal_url.getPortalObject()
        dico = {"authMember": portal.portal_membership.getAuthenticatedMember().getId()}

        auteur = self.getCreateur()
        dico["qclass"] = self.setClasse()
        dico["qsheet"] = self.getIdFeuilleWIMS(auteur)

        # Affichage
        if item_property_name == "affElement":
            aff_autorise = self.autoriser_Affichage()
            # Si l'affichage de l'objet est impossible, on arrete la.
            #  (cas habituel : liste d'exos vide)
            if not aff_autorise["val"]:
                return aff_autorise
            dico["status"] = 1
        # Masquage
        else:
            dico["status"] = 0

        # cas des Examens
        if self.typeWims == "Examen":

            dico_feuille = dico.copy()
            # Lorsqu'on active l'examen, la feuille doit passer
            # dans l'etat 3 (périmé+caché), et y rester.
            if dico["status"] or self.idExam:
                dico_feuille["status"] = 3
            self.wims("modifierFeuille", dico_feuille)

            dico["title"] = self.Title()
            dico["description"] = self.Description()
            dico["duration"] = self.duree
            dico["attempts"] = self.attempts
            dico["cut_hours"] = self.cut_hours

            # Lors du 1er affichage de l'examen, on le crée
            if dico["status"] and not self.idExam:
                # print "jaloncourswims/afficherRessource // dico =%s" % str(dico)
                reponse = self.wims("creerExamen", dico)
                if reponse["status"] == "OK":
                    self.idExam = str(reponse["exam_id"])
                    # L'examen est créé, on lui ajoute alors la liste des exercices de la feuille
                    reponse = self.wims("injecter_exercice", {"authMember": dico["authMember"], "qclass": dico["qclass"], "qsheet": dico["qsheet"], "qexam": self.idExam})

            # Cas de l'examen créé
            if self.idExam:
                # On cree un dictionnaire épuré, pour ne changer que le statut.
                newdico = {"status": dico["status"], "qclass": dico["qclass"], "authMember": dico["authMember"]}
                # une fois un examen activé, on ne peut plus le désactiver.
                # le statut passe à 3 (périmé+caché) pour le masquer
                if newdico["status"] == 0:
                    newdico["status"] = 3
                newdico["qexam"] = self.idExam
                reponse = self.wims("modifierExamen", newdico)

        # Cas des autoevaluations
        else:
            reponse = self.wims("modifierFeuille", dico)

        if reponse["status"] == "OK":
            super(JalonCoursWims, self).editCourseItemVisibility(item_id, item_date, item_property_name)
        else:
            message = _(u"Une erreur est survenue. La visibilité de l'activité « ${title} » n'a pas changé.", mapping={'title':  self.Title().decode("utf-8")})
            self.plone_utils.addPortalMessage(message, type='error')

    """
    def afficherRessource(self, idElement, dateAffichage, attribut):
        #""Modifie les dates de la ressource pour activer/desactiver son affichage.""
        # On agit directement sur l'activité
        if idElement == self.getId():

            portal = self.portal_url.getPortalObject()
            # portal = portal_state.portal()
            dico = {"authMember": portal.portal_membership.getAuthenticatedMember().getId()}

            # Affichage
            if attribut == "affElement":
                aff_autorise = self.autoriser_Affichage()
                # Si l'affichage de l'objet est impossible, on arrete la.
                #  (cas habituel : liste d'exos vide)
                if not aff_autorise["val"]:
                    return aff_autorise
                self.dateAff = dateAffichage
                self.dateMasq = ""
                dico["status"] = 1

                portal_workflow = getToolByName(portal, "portal_workflow")
                # Si l'etat de l'element était en mode "pending",
                #  on le passe en mode "submit"
                if portal_workflow.getInfoFor(self, "review_state", wf_id="jalon_workflow") != "pending":
                    portal_workflow.doActionFor(self, "submit", "jalon_workflow")
            # Masquage
            else:
                dico["status"] = 0
                self.dateMasq = dateAffichage

            auteur = self.getCreateur()
            dico["qclass"] = self.setClasse()
            dico["qsheet"] = self.getIdFeuilleWIMS(auteur)

            if self.typeWims == "Examen":

                dico_feuille = dico.copy()
                # Lorsqu'on active l'examen, la feuille doit passer
                # dans l'etat 3 (périmé+caché), et y rester.
                if dico["status"] or self.idExam:
                    dico_feuille["status"] = 3
                self.wims("modifierFeuille", dico_feuille)

                dico["title"] = self.Title()
                dico["description"] = self.Description()
                dico["duration"] = self.duree
                dico["attempts"] = self.attempts
                dico["cut_hours"] = self.cut_hours

                # Lors du 1er affichage de l'examen, on le crée
                if dico["status"] and not self.idExam:
                    # print "jaloncourswims/afficherRessource // dico =%s" % str(dico)
                    reponse = self.wims("creerExamen", dico)
                    self.idExam = str(reponse["exam_id"])
                    # L'examen est créé, on lui ajoute alors la liste des exercices de la feuille
                    reponse = self.wims("injecter_exercice", {"authMember": dico["authMember"], "qclass": dico["qclass"], "qsheet": dico["qsheet"], "qexam": self.idExam})
                    # si l'examen existe deja, on lui applique
                    # les modifications
                if self.idExam:
                    # On cree un dictionnaire épuré, pour ne changer que le statut.
                    newdico = {"status": dico["status"], "qclass": dico["qclass"], "authMember": dico["authMember"]}
                    # une fois un examen activé, on ne peut plus le désactiver.
                    # le statut passe à 3 (périmé+caché) pour le masquer
                    if newdico["status"] == 0:
                        newdico["status"] = 3
                    newdico["qexam"] = self.idExam
                    self.wims("modifierExamen", newdico)

            # cas des autoevaluations
            else:
                self.wims("modifierFeuille", dico)

            # self.setProperties(dico)
            self.aq_parent.modifierInfosBoitePlan(self.getId(), {"affElement": self.getDateAff(), "masquerElement": self.getDateMasq()})
            self.reindexObject()

        # On agit sur  un sous élément de l'activité
        else:
            infos_element = copy.deepcopy(self.getInfosElement())
            if infos_element:
                infos_element[idElement][attribut] = dateAffichage
                if attribut == "affElement":
                    infos_element[idElement]["masquerElement"] = ""
                self.setInfosElement(infos_element)

                rep = {"Image": "Fichiers",
                       "File": "Fichiers",
                       "Lien web": "Externes",
                       "Lecteur exportable": "Externes",
                       "Reference bibliographique": "Externes",
                       "Glossaire": "Glossaire",
                       "Webconference": "Webconference",
                       "Presentations sonorisees": "Sonorisation"}
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
        # u""permet d'ajouter un element (sujet ou exercice) à une autoevaluation ou un examen.""
        menu = "sujets"
        rep = {"Image"                      : "Fichiers",
               "File"                       : "Fichiers",
               "Page"                       : "Fichiers",
               "Lien web"                   : "Externes",
               "Lecteur exportable"         : "Externes",
               "Catalogue BU"               : "Externes",
               "Webconference"              : "Webconference",
               "Presentations sonorisees"   : "Sonorisation",
               "Exercice Wims"              : "Wims"}
        if typeElement in rep:
            if "*-*" in idElement:
                idElement = idElement.replace("*-*", ".")
            objet = getattr(getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), createurElement), rep[typeElement]), idElement)
            if typeElement == "Exercice Wims":
                menu = "exercices"
                idClasse = self.getClasse()
                if idElement.startswith("externe-"):
                    permalien = objet['permalink']
                    dico = {"job": "putexo", "code": createurElement, "qclass": idClasse, "qsheet": self.idFeuille}
                    if permalien != "":
                        # exemple de permalien : module=U2/analysis/oeffourier.fr&exo=addfourier2,addfourier1,addfourier4,addfourier3&qnum=1&qcmlevel=3
                        parsed_permalien = permalien.split("&", 1)
                        if len(parsed_permalien) == 1:
                            # par defaut, si aucun parametre n'a ete defini, on definie au minima le parametre de sévérité
                            parsed_permalien.append("qcmlevel=1")
                        donnees_exercice = u"%s\nparams=%s\npoints=%s\nweight=%s\ntitle=%s\ndescription=%s" % (parsed_permalien[0],
                                                                                                               parsed_permalien[1],
                                                                                                               u"10",
                                                                                                               u"1",
                                                                                                               titreElement.decode("utf-8"),
                                                                                                               u"")
                        dico["data1"] = donnees_exercice.encode("utf-8")
                        rep_wims = self.wims("callJob", dico)
                    else:
                        rep_wims = '{"status": "ERROR", "message": "pas de permalien pour cet exercice externe"}'
                    rep_wims = self.wims("verifierRetourWims", {"rep": rep_wims,
                                                                "fonction": "jaloncourswims.py/ajouterElement",
                                                                "message": "parametres de la requete : %s" % dico})
                    if rep_wims['status'] != "OK":
                        # Le retour sera intercepté depuis "cours_element_add" pour afficher une erreur a l'utilisateur
                        # en outre, l'exercice n'est pas ajouté.
                        # print "\n####### jaloncourswims/ajouterElement -- Attention : '%s'\n" % rep_wims['message']
                        return rep_wims
                else:
                    if idElement.startswith("groupe-"):
                        listeExos = objet.getListeIdsExos()
                        qnum = objet.getQnum()
                    else:
                        listeExos = [idElement]
                        qnum = "1"
                    # Ici il faudrait savoir si on se trouve dans une autoveal ou un examen, afin de transmettre l'info à lierExoFeuille (pour activer l'affichage des bonnes réponses)
                    afficher_reponses = False
                    if self.typeWims != "Examen":
                        afficher_reponses = True

                    rep_wims = self.wims("lierExoFeuille", {"authMember": createurElement, "title": titreElement,
                                                            "qclass": idClasse, "qsheet": self.idFeuille,
                                                            "listeExos": listeExos, "qnum": qnum,
                                                            "afficher_reponses": afficher_reponses})
                    if rep_wims["status"] != "OK":
                        # Attention si la creation n'a pas eu lieu coté WIMS, il ne faut rien créer côté Jalon.
                        return rep_wims

            # On ajoute l'activité aux relatedItems de l'objet.
            relatedItems = objet.getRelatedItems()
            if self not in relatedItems:
                relatedItems.append(self)
                objet.setRelatedItems(relatedItems)
                objet.reindexObject()

            # Et on ajoute l'exercice aux relatedItems de l'activité ??
            # ==> Inutile, l'activité connait deja ses listes d'objets.
            # activiteRelatedItems = self.getRelatedItems()
            # if not objet in activiteRelatedItems:
            #   activiteRelatedItems.append(objet)
            #   self.setRelatedItems(activiteRelatedItems)
            #   self.reindexObject()

            categorie = list(self.__getattribute__("liste%s" % menu.capitalize()))
            if menu == "sujets" and "." in idElement:
                idElement = idElement.replace(".", "*-*")
            categorie.append(idElement)
            setattr(self, "liste%s" % menu.capitalize(), tuple(categorie))
            self.ajouterInfosElement(idElement, typeElement, titreElement, createurElement, affElement=affElement)

    def ajouterInfosElement(self, idElement, typeElement, titreElement, createurElement, affElement=""):
        # ajouter Infos Element.
        infos_element = copy.deepcopy(self.getInfosElement())
        if idElement not in infos_element:
            infos_element[idElement] = {"titreElement": titreElement,
                                        "typeElement": typeElement,
                                        "createurElement": createurElement,
                                        "affElement": affElement,
                                        "masquerElement": ""}
            # self.setInfos_element(infos_element)
            self.setInfosElement(infos_element)

    def ajouterTag(self, tag):
        # ajouterTag.
        return jalon_utils.setTag(self, tag)"""

    def authUser(self, quser=None, qclass=None, request=None, session_keep=False):
        """appelle la fonction authUser de jalon_utils (authentifie un user WIMS)."""
        # LOG.info("----- authUser -----")
        return jalon_utils.authUser(self, quser, qclass, request, session_keep)

    def autoriser_Affichage(self):
        u"""définit si l'affichage de l'objet 'idElement' est autorisé ou pas.

        utile pour empecher l'affichage des activités vides par exemple

        """
        # LOG.info("----- autoriser_Affichage -----")
        listeExos = self.getListeExercices()
        if not listeExos:
            return {"val": False, "reason": "listeExos"}
        else:
            return {"val": True, "reason": ""}

    """
    DEPRECATED ? [utiliser plutot retirerElement()]

    def detacherRessource(self, ressource, repertoire, attribut):
        #Détache un sujet (la ressource) de l'activité courante.
        listeElement = list(self.getListeAttribut(attribut))
        listeElement.remove(ressource)
        setattr(self, "liste%s" % attribut.capitalize(), tuple(listeElement))
        infos_element = self.aq_parent.retirerInfosSousElement(ressource)
        categorie, idRessource = ressource.split("*-*")

        if repertoire in _dicoRep:
            repertoire = _dicoRep[repertoire]
        portal = self.portal_url.getPortalObject()
        home = getattr(getattr(portal.Members, infos_element["createurElement"]), repertoire)
        objet = getattr(home, idRessource)
        relatedItems = objet.getRelatedItems()
        relatedItems.remove(self)
        objet.setRelatedItems(relatedItems)
        objet.reindexObject()
    """

    def getAllNotes(self, quser, actif, isProf):
        u"""renvoie toutes les notes des étudiants sur l'activité courante.

        # TODO

        """
        # LOG.info('----- getAllNotes -----')
        param["qclass"] = self.getClasse()
        param["qsheet"] = self.getIdFeuille()
        # Cas des Autoevaluations activées:
        if actif and not self.idExam:
            # Cas d'un etudiant, on demande ses notes sur cette feuille
            if not isProf:
                print "Juste un test"

    def getClasse(self):
        u"""retourne l'identifiant de la classe du cours associée à l'auteur de cette activite."""
        # LOG.info('----- getClasse -----')
        auteur = self.getCreateur()
        listeClasses = list(self.aq_parent.getListeClasses())
        idClasse = None
        if listeClasses:
            dicoClasses = listeClasses[0]
            if auteur in dicoClasses:
                idClasse = dicoClasses[auteur]
        return idClasse

    def getCreateur(self):
        u"""Retourne l'auteur de l'activite courante.

        # Lors d'une duplication de cours, tous les objets appartiennent à celui qui demande la duplication.
        # On ne peut donc pas utiliser self.Creator() pour les activités dupliquées.

        # Format d'un Id d'une Activite WIMS :
        # TYPE-CREATEUR-DATE_CREATION
        # Exemple : AutoEvaluation-bado-20140910153227291052

        """
        # LOG.info('----- getCreateur -----')
        identifiant = self.getId().split("-")
        # LOG.info('*** len(identifiant)= %s ***' % len(identifiant))
        if len(identifiant) > 1:
            return identifiant[1]
        else:
            return self.Creator()

    def setClasse(self):
        u"""crée une classe associée au cours dans le groupe de classes de l'auteur de cette activite."""
        # LOG.info('----- setClasse -----')

        auteur = self.getCreateur()
        listeClasses = list(self.aq_parent.getListeClasses())
        idClasse = None
        dicoClasses = {}
        if listeClasses:
            dicoClasses = listeClasses[0]
            if auteur in dicoClasses:
                idClasse = dicoClasses[auteur]
        if not idClasse:

            member = self.portal_membership.getMemberById(auteur)
            auth_email = member.getProperty("email")
            fullname = member.getProperty("fullname")
            if not fullname:
                fullname = member.getProperty("displayName")
            if not auth_email:
                auth_email = str(member.getProperty("mail"))
            idgroupement = self.getGroupement(auteur)
            if not idgroupement:
                # Cas ou l'utilisateur a tenté de créer une autoevaluation ou un examen sans etre passé une fois par les exercices WIMS
                LOG.info('#### Creation de classe WIMS sans Groupement ####')
                return None

            classe = self.wims("creerClasse", {"authMember": auteur, "fullname": fullname, "auth_email": auth_email, "type": "1", "titre_classe": self.aq_parent.title_or_id(), "qclass": idgroupement})
            if classe and classe["status"] == "OK":
                dicoClasses[auteur] = str(classe["class_id"])
                idclasse = str(classe["class_id"])
                self.wims("callJob", {"job": "sharecontent", "qclass": "%s_1" % idgroupement, "data1": idclasse, "code": auteur})
            else:
                self.wims("verifierRetourWims", {"rep": classe,
                                                 "fonction": "jaloncourswims.py/setClasse",
                                                 "message": "job = creerClasse"
                                                 })
                LOG.info('#### CREATION DE CLASSE WIMS IMPOSSIBLE ####')
                return None
            idClasse = classe["class_id"]
            self.aq_parent.setListeClasses([dicoClasses])

        return idClasse

    def getDisplayLang(self):
        """retourne la langue de l'exercice, dans un format affichable, ainsi qu'un code d'icone de drapeau."""
        # LOG.info('----- getDisplayLang -----')
        icone = code_langue = self.getWims_lang()
        if icone == "en":
            icone = "gb"

        retour = {"icone": icone, "description": languages.getValue(code_langue)}
        return retour

    def getDicoProperties(self):
        u"""Renvoie le dico des propriétés de l'objet jalonCoursWims courant (Autoevaluation ou Examen).

        # utile pour les duplicatas par exemple.

        """
        # LOG.info('----- getDicoProperties -----')
        dico = {"Title": self.Title(),
                "Description": self.Description(),
                "DocumentsProperties": copy.deepcopy(self.getDocumentsProperties()),
                "DateAff": self.getDateAff(),
                "DateMasq": self.getDateMasq(),
                "TypeWims": self.getTypeWims(),
                "IdFeuille": self.getIdFeuille(),
                "IdExam": self.getIdExam(),
                "Note_max": self.getNoteMax(),
                "Duree": self.getDuree(),
                "Attempts": self.getAttempts(),
                "ListeExercices": copy.deepcopy(self.getListeExercices()),
                "ListeSujets": copy.deepcopy(self.getListeSujets()),
                "Cut_hours": self.getCut_hours(),
                "Verrou": self.getVerrou(),
                "Wims_lang": self.getWims_lang(),
                }
        return dico

    def getGroupement(self, auteur=None):
        u"""Renvoit le groupement de classe associé a l'auteur en parametre."""
        # LOG.info("----- getGroupement -----")
        if auteur is None:
            auteur = self.getCreateur()
        idgroupement = getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), auteur), "Wims").getComplement()
        return idgroupement

    def updateExercicesList(self, infos_elements):
        """ Met à jour la liste des exercices coté Jalon en fonction des exercices côté WIMS."""
        # LOG.info("----- updateExercicesList -----")

        listeExercices = list(self.getListeExercices())
        # infos_elements = self.getDocumentsProperties()
        portal = self.portal_url.getPortalObject()
        auteur = self.getCreateur()

        dico = {"job": "getsheet",
                "code": portal.portal_membership.getAuthenticatedMember().getId(),
                "qclass": self.setClasse(),
                "qsheet": self.getIdFeuilleWIMS(auteur)}
        donnees_feuille = self.wims("callJob", dico)
        donnees_feuille = self.wims("verifierRetourWims", {"rep": donnees_feuille,
                                                           "fonction": "jaloncourswims.py/updateExercicesList",
                                                           "message": "job = getsheet | parametres de la requete : %s" % dico
                                                           })
        if donnees_feuille["status"] != "OK":
            return donnees_feuille

        """for exoID in listeExercices:
            if exoID.split("-")[0] == "recover":
                self.retirerElement(exoID, "Exercices")
        return True
        """

        # ICI il est impossible de retrouver l'id jalon d'un exercice WIMS.
        #  La seule chose qu'on peut faire, c'est savoir s'il y en a plus sur WIMS que sur Jalon...
        nb_jalon = len(listeExercices)
        nb_wims = 0
        inner_module = "classes/%s" % self.getWims_lang()
        """
        "exolist":[{"module":"U2/analysis/oeffourier.fr",
                    "title":"in addition de fourier au hasard",
                    "params":"exo=addfourier2&exo=addfourier1&exo=addfourier4&exo=addfourier3&qnum=1&qcmlevel=3",
                    "points":"45",
                    "weight":"2",
                    "description":"un exo au hasard parmi les additions de fourier"}]
        """
        for exo_wims in donnees_feuille["exolist"]:
            nb_wims += 1
            if nb_wims > nb_jalon:
                if exo_wims["module"] == inner_module:
                    exowimsID = exo_wims["params"]
                    """if exo_wims["params"] not in listeExercices:
                            recup_id = "recover-%s-%s" % (auteur, DateTime().strftime("%Y%m%d%H%M%S"))
                    """
                else:
                    exowimsID = "recover-%s-%s-%s" % (auteur, DateTime().strftime("%Y%m%d%H%M%S"), nb_wims)

                self.addItemProperty(exowimsID, "Exercice Wims", exo_wims["title"], auteur, "", "", "Exercices")
            """
            else:
                # L'exercice est déja présent dans Jalon
                idElement = listeExercices[nb_wims - 1]
                # On met à jour les titres Jalon en fonction des titres WIMS (mais on pourrait plutot faire l'inverse ?)
                infos_elements[idElement]["titreElement"] = exo_wims["title"]
            """

    def cleanActivity(self):
        """ Supprime tout élément indésirable de l'activité (issu de mauvaises manipulations)."""
        # LOG.info("----- cleanActivity -----")

        listeSujets = list(self.getListeSujets())
        listeExercices = list(self.getListeExercices())
        infos_elements = self.getDocumentsProperties()

        # 1 Suppression d'eventuels exercices présents dans la liste des sujets
        for idElement in listeSujets:
            if idElement in infos_elements:
                if infos_elements[idElement]["typeElement"] == "Exercice Wims":
                    listeSujets.remove(idElement)

        # 2 mise à jour de la liste des exercices a partir des infos de WIMS
        self.updateExercicesList(infos_elements)

        # 3 Suppression d'eventuels elements présents la liste des exos mais qui ne sont pas des exos.
        for idElement in listeExercices:
            if idElement in infos_elements:
                if infos_elements[idElement]["typeElement"] != "Exercice Wims":
                    listeExercices.remove(idElement)

        # Nettoyage du dico "infos_elements"
        infos_elements_copy = copy.deepcopy(infos_elements)
        for idElement in infos_elements_copy:
            # Suppression d'eventuels elements présents dans infos_elements mais ni dans les sujets ni dans les exos.
            if (idElement not in listeSujets) and (idElement not in listeExercices):
                del infos_elements[idElement]

            # Suppression d'eventuels attributs inutiles
            for useless in ["idElement", "classElement", "iconElement"]:
                if useless in infos_elements[idElement]:
                    del infos_elements[idElement][useless]

        setattr(self, "listeSujets", tuple(listeSujets))
        setattr(self, "listeExercices", tuple(listeExercices))

    def displayExercicesList(self):
        """Fournit une liste de couples (ID/titre) des exercices de l'activite."""
        # LOG.info("----- displayExercicesList -----")

        exercices_list = []
        documents_dict = self.getDocumentsProperties()
        for document_id in self.getListeExercices():
            if document_id in documents_dict:
                exo_title = documents_dict[document_id]["titreElement"]
            else:
                exo_title = _(u"exercice sans titre ?")

            exo_dict = {"idElement":      document_id,
                        "titreElement":   exo_title
                        }

            exercices_list.append(exo_dict)
        return exercices_list

    def getInfosListeAttribut(self, attribut, personnel=False):
        u"""renvoit la liste des elements d'une activité WIMS."""
        # LOG.info("----- getInfosListeAttribut -----")
        retour = []
        listeElement = self.getListeAttribut(attribut)
        infos_element = self.getDocumentsProperties()

        for idElement in listeElement:
            infos = infos_element.get(idElement, None)
            if infos:
                # LOG.info("***** attribut = %s" % attribut)
                # LOG.info("***** infos = %s" % infos)
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

        # if retour:
        #    retour.sort(lambda x, y: cmp(x["titreElement"], y["titreElement"]))
        return retour

    def getNbSujets(self, is_personnel):
        """Obtient le nombre de sujets à afficher."""
        # LOG.info("----- getNbSujets -----")
        return len(self.getInfosListeAttribut("sujets", is_personnel))

    def getNbExercices(self):
        """Obtient le nombre d'exercices."""
        # LOG.info("----- getNbExercices -----")
        # return len(self.getInfosListeAttribut("exercices", True))
        return len(self.getListeExercices())

    def getListeAttribut(self, attribut):
        """get Liste Attribut."""
        # LOG.info("----- getListeAttribut -----")
        return self.__getattribute__("liste%s" % attribut.capitalize())

    def getNotes(self, quser, actif, isProf, detailed=False, site_lang="", request=None):
        u"""getNotes.

        Renvoit soit
            - les notes obtenues par l'etudiant 'quser' sur l'activité courante,
            - ou les notes de l'activité (dans ce cas, detailed permet d'obtenir les notes par etudiants)

        """
        # LOG.info("----- getNotes -----")
        no_user_message = "There is no user in this class"
        param = {"quser": quser}
        # On fait un setClasse() pour créer eventuellement la classe si ce n'etait deja fait.
        param["qclass"] = self.setClasse()

        # On donne des infos de Jalon pour debugger plus facilement en cas d'erreur.
        param["jalon_request"] = request

        if not param["qclass"]:
            if self.getGroupement():
                # Si l'obtention/creation de classe plante, la connexion a WIMS est surement rompue.
                rep_wims = '{"status": "ERROR", "message": "Impossible de créer la classe WIMS.", "quser":"%s"}' % quser
                self.wims("verifierRetourWims", {"rep": rep_wims, "fonction": "jaloncourswims.py/getNotes"})
                message = _(u"Serveur injoignable. Merci de réessayer plus tard svp. (Impossible de créer la classe WIMS)")
                self.plone_utils.addPortalMessage(message, type='error')
                return {"status": "ERROR", "message": message}
            else:
                # Si l'utilisateur n'as pas de groupement, il devra d'abord passer par "Mon espace" pour ajouter des exercices.
                return {"status": "OK", "user_cnt": 0}

        # Puis un getIdFeuilleWIMS() pour créer eventuellement la feuille si ce n'etait deja fait.
        param["qsheet"] = self.getIdFeuilleWIMS(quser)
        # Si la creation de feuille plante, la connexion a WIMS doit etre rompue.
        if not param["qsheet"]:
            message = _(u"Serveur injoignable. Merci de réessayer plus tard svp. (Impossible de créer une feuille WIMS)")
            self.plone_utils.addPortalMessage(message, type='error')
            return {"status": "ERROR", "message": message}

        retour = {"pourcentage": "", "qualite": "", "listeNotes": [], "message": ""}
        # portal = self.portal_url.getPortalObject()
        # Cas des Autoevaluations activées:
        if actif and not self.idExam:
            # Dans le cas d'un etudiant, on demande ses notes sur cette feuille
            if not isProf:
                rep = self.wims("getNote", param)
                # print "\n getnote : %s \n" % rep
                # Si on obtient des notes, c'est au moins que l'etudiant a un compte dans cette classe
                if rep["status"] == "OK":
                    index = 0
                    totalNotes = 0.0
                    totalSur = 0
                    listeNotes = []
                    erreur = False
                    liste_except = []
                    liste_erreurs = []
                    for score in rep["got_points"]:

                        try:
                            sur = rep["weights"][index]
                        except:
                            # Dans le cas ou l'exercice n'a pas encore de poid défini dans WIMS, on le place à 1
                            sur = 1

                        try:
                            note = ((float(score) / rep["require_points"][index]) * sur) * 100
                        except Exception as e:
                            # Dans certains cas, il semble que "score" soit une liste... ?
                            note = 0
                            erreur = True
                            liste_erreurs.append(score)
                            liste_except.append(e)
                        totalNotes = totalNotes + note
                        totalSur = totalSur + sur
                        note = "%.0f" % note
                        qualite = "%.2f" % rep["score_qualities"][index]
                        if site_lang == "fr":
                            # note = str(note).replace(".", ",")
                            qualite = str(qualite).replace(".", ",")
                        listeNotes.append({"note": note,
                                           "sur": sur,
                                           "qualite": qualite,
                                           })
                        index = index + 1
                    if erreur:
                        rep_wims = '{"status": "ERROR", "message": "impossible de convertir le score au type float"}'
                        self.wims("verifierRetourWims", {"rep": rep_wims,
                                                         "fonction": "jaloncourswims.py/getNotes",
                                                         "message": '<ul><li>rep["got_points"] = %s</li><li>rep["require_points"] = %s</li>\<li>Liste des scores verreux : %s</li><li>Liste des exceptions : %s</li></ul>' % (rep["got_points"], rep["require_points"], liste_erreurs, liste_except),
                                                         "requete": param,
                                                         "jalon_request": request
                                                         })
                    if totalSur == 0:
                        retour["note"] = 0
                    else:
                        retour["note"] = (totalNotes * float(self.getNoteMax())) / totalSur
                    # DEBUG
                    retour["sheet_summaries"] = rep["sheet_summaries"]
                    if len(rep["sheet_summaries"]) > 1:
                        # LOG.info("[getNotes] | rep[sheet_summaries] = %s " % rep["sheet_summaries"])
                        retour["pourcentage"] = rep["sheet_summaries"][0]
                        retour["qualite"] = (rep["sheet_summaries"][1] * float(self.getNoteMax())) / 10
                    else:
                        retour["pourcentage"] = "--"
                        retour["qualite"] = "--"

                    if site_lang == "fr":
                        retour["qualite"] = str(retour["qualite"]).replace(".", ",")
                        retour["note"] = str(retour["note"]).replace(".", ",")

                    # cas eventuel ou un exo a ete ajouté mais l'etudiant n'as pas encore eu de note dessus
                    difference = len(self.getListeExercices()) - len(listeNotes)
                    while difference > 0:
                        listeNotes.append({"note": "--",
                                           "sur": "--",
                                           "qualite": "--",
                                           })
                        difference = difference - 1

                    retour["listeNotes"] = listeNotes
                    retour["status"] = rep["status"]
                    return retour

            else:
                # Pour l'auteur et le co-auteur, cas d'une autoevaluation active
                if not detailed:
                    # dans le menu "exercices, on ne demande que les notes globales de la feuille
                    # nb : il est possible que getsheetstats ne donne pas d'infos globales d'une feuille
                    # quand il existe une feuille n-1 qui n'a jamais été activée.
                    dico = {"job": "getsheetstats", "code": quser, "qclass": param["qclass"], "qsheet": param["qsheet"]}
                    rep_wims = self.wims("callJob", dico)
                    # LOG.info("retour de getsheetstats : %s" % rep_wims)
                    if no_user_message in rep_wims:
                        rep = json.loads(rep_wims)
                    else:
                        rep = self.wims("verifierRetourWims", {"rep": rep_wims,
                                                               "fonction": "jaloncourswims.py/getNotes",
                                                               "message": 'stats globales de la feuille demandees par un auteur/coauteur',
                                                               "requete": dico})
                    # LOG.info('Retour WIMS = %s' % rep)
                    listeNotes = []
                    if rep["status"] == "OK":
                        for indice, poids in enumerate(rep["weights"]):
                            try:
                                # On multiplie la note par 10 pour avoir un pourcentage.
                                exo_note = float(rep["sheet_got_details"][indice]) * 10
                                exo_note = "%.2f " % exo_note
                                exo_qualite = rep["sheet_quality_details"][indice]
                                exo_qualite = "%.2f" % exo_qualite
                            except:
                                exo_qualite = exo_note = "--"
                                # print "EXCEPTION RAISE dans jalonCoursWims/getNotes! rep['sheet_got_details'] = %s" % rep["sheet_got_details"]

                            if site_lang == "fr":
                                exo_note = exo_note.replace(".", ",")
                                exo_qualite = exo_qualite.replace(".", ",")
                            listeNotes.append({"note": exo_note,
                                               "sur": poids,
                                               "qualite": exo_qualite
                                               })
                    rep["listeNotes"] = listeNotes
                else:
                    # dans le menu "resultats", on demande les notes detailles de la feuille
                    dico = {"job": "getsheetscores", "code": quser, "qclass": param["qclass"], "qsheet": param["qsheet"]}
                    rep_wims = self.wims("callJob", dico)
                    if no_user_message in rep_wims:
                        rep = json.loads(rep_wims)
                    else:
                        rep = self.wims("verifierRetourWims", {"rep": rep_wims,
                                                               "fonction": "jaloncourswims.py/getNotes",
                                                               "message": 'notes detaillees de la feuille demandees par un auteur/coauteur',
                                                               "requete": dico})
                        # Si on obtient des notes, c'est qu'il y a au moins un étudiant dans cette classe
                        if rep["status"] == "OK":
                            # si les etudiants ont deja eu des notes une premiere fois sur cette feuille, et qu'on a ajouté ensuite un exo, les données risquent d'etre erronées. on ne passera surmeent pas un try
                            listETU = [x["id"] for x in rep["data_scores"]]
                            dico_ETU = jalon_utils.getIndividus(listETU, type="dict")
                            for user in rep["data_scores"]:
                                if user["id"] in dico_ETU:
                                    individu = dico_ETU[user["id"]]
                                    user["first_name"] = individu["prenom"]
                                    user["last_name"]  = individu["nom"]
                                    user["num_etu"]    = individu["num_etu"]
                                # cas des comptes enseignants et invités
                                else:
                                    # attention : il est possible que le user_id de wims ne corresponde pas exactement a un user_id jalon
                                    # (user_id wims ayant pu etre tronqué par validerUserID + module raw transforme automatiquement . en @)
                                    # Si user["id"] n'est pas trouvé, on gardera simplement les infos données par WIMS.
                                    # pour debug : user["first_name"] = "%s [direct from WIMS]" % user["first_name"]
                                    user["num_etu"] = "Non disp."
                                user["user_quality"] = "%.2f" % ((float(user["user_quality"]) * float(self.getNoteMax())) / 10)
                                user["user_percent"] = "%.2f" % user["user_percent"]
                                if site_lang == "fr":
                                    user["user_quality"] = str(user["user_quality"]).replace(".", ",")
                                    user["user_percent"] = str(user["user_percent"]).replace(".", ",")
                if rep["status"] == "OK":
                    rep["sheet_max_percent"] = "%.2f" % rep["sheet_max_percent"]
                    rep["note"] = (float(rep["sheet_max_quality"]) * float(self.getNoteMax())) / 10
                    rep["note"] = "%.2f" % rep["note"]
                    rep["pourcentage"] = "%.2f" % rep["sheet_mean_percent"]
                    rep["qualite"] = "%.2f" % ((float(rep["sheet_mean_quality"]) * float(self.getNoteMax())) / 10)

                    if site_lang == "fr":
                        rep["note"] = str(rep["note"]).replace(".", ",")
                        rep["sheet_max_percent"] = str(rep["sheet_max_percent"]).replace(".", ",")
                        rep["pourcentage"] = str(rep["pourcentage"]).replace(".", ",")
                        rep["qualite"] = str(rep["qualite"]).replace(".", ",")
                    return rep
        # cas des Examens :
        elif self.idExam:

            # on demande les infos de la feuille, pour connaitre le poid de chaque exercice.
            donnees_feuille = self.wims("callJob", {"job": "getsheet", "code": quser, "qclass": param["qclass"], "qsheet": param["qsheet"]})

            donnees_feuille = self.wims("verifierRetourWims", {"rep": donnees_feuille,
                                                               "fonction": "jaloncourswims.py/getNotes",
                                                               "message": "[cas des examens] parametres de la requete : %s" % param,
                                                               "jalon_request": request
                                                               })
            if donnees_feuille["status"] != "OK":
                return donnees_feuille

            listeNotes = []
            for exo in donnees_feuille["exolist"]:
                listeNotes.append({"note": "--",
                                   "sur": exo["weight"],
                                   "qualite": "--"
                                   })

            # Dans le cas d'un etudiant, on demande ses notes sur cet exam
            if not isProf:
                # On supprime qsheet pour ne pas interferer avec l'examen
                qsheet = param["qsheet"]
                del param["qsheet"]
                rep = self.wims("getNote", param)
                # Si on obtient des notes, c'est au moins que l'etudiant a un compte dans cette classe

                retour["listeNotes"] = listeNotes
                retour["status"] = rep["status"]
                if rep["status"] == "OK":
                    retour["rep"] = rep
                    try:
                        retour["note"] = float(rep["exam_scores"][0][int(self.getIdExam()) - 1]) * float(self.getNoteMax()) / 10

                        if site_lang == "fr":
                            retour["note"] = str(retour["note"]).replace(".", ",")
                    except:
                        retour["note"] = "--"
                    return retour
                else:
                    # On replace qsheet pour obtenir des infos globales
                    retour["message"] = rep["message"]
                    param["qsheet"] = qsheet

            # Pour l'auteur et le co-auteur, on demande les notes globales de l'examen s'il est actif
            if isProf:
                rep = json.loads(self.wims("callJob", {"job": "getexamscores", "code": quser, "qclass": param["qclass"], "qexam": self.getIdExam()}))
                # Si on obtient des notes, c'est qu'il y a au moins un étudiant dans cette classe
                if rep["status"] == "OK":
                    rep["score_max"]  = (float(rep["score_max"]) * float(self.getNoteMax())) / 10
                    rep["score_mean"] = (float(rep["score_mean"]) * float(self.getNoteMax())) / 10
                    rep["score_max"]  = "%.2f" % rep["score_max"]
                    rep["score_mean"] = "%.2f" % rep["score_mean"]

                    if site_lang == "fr":
                        rep["score_max"] = str(rep["score_max"]).replace(".", ",")
                        rep["score_mean"] = str(rep["score_mean"]).replace(".", ",")
                    rep["listeNotes"] = listeNotes
                    listETU = [x["id"] for x in rep["data_scores"]]
                    dico_ETU = jalon_utils.getIndividus(listETU, type="dict")
                    for user in rep["data_scores"]:
                        if user["id"] in dico_ETU:
                            individu = dico_ETU[user["id"]]
                            user["first_name"] = individu["prenom"]
                            user["last_name"]  = individu["nom"]
                            user["num_etu"]    = dico_ETU[user["id"]]["num_etu"]
                        # cas des comptes enseignants et invités
                        else:
                            # attention : il est possible que le user_id de wims ne corresponde pas exactement a un user_id jalon
                            # (user_id wims ayant pu etre tronqué par validerUserID + modurle raw transforme automatiquement . en @)
                            # Si user["id"] n'est pas trouvé, on gardera simplement les infos données par WIMS.
                            user["num_etu"] = "Non disp."
                        user["score"] = (float(user["score"]) * float(self.getNoteMax())) / 10
                        user["score"] = "%.2f" % user["score"]
                        if site_lang == "fr":
                            user["score"] = str(user["score"]).replace(".", ",")
                    return rep
        # Si l'activité est masquée, ou que c'est une feuille pour laquelle l'etudiant n'a pas de compte dans cette classe (cad il n'a jamais fait un exercice dans ce cours)
        # on demande alors uniquement les infos de la feuille
        rep = self.wims("callJob", {"job": "getsheet", "code": quser, "qclass": param["qclass"], "qsheet": param["qsheet"]})
        rep = self.wims("verifierRetourWims", {"rep": rep,
                                               "fonction": "jaloncourswims.py/getNotes",
                                               "message": "job = getsheet | parametres de la requete : %s" % param,
                                               "jalon_request": request
                                               })

        listeNotes = []
        if rep["status"] == "OK":
            retour["sheet_status"] = rep["sheet_status"]
            liste_exos_jalon = self.getListeExercices()
            nbExos_wims = len(rep["exolist"])
            # for exo in rep["exolist"]:
            for index, exo_jalon in enumerate(liste_exos_jalon):
                if index < nbExos_wims:
                    sur = rep["exolist"][index]["weight"]
                else:
                    # Ici l'exo n'existe pas/plus coté wims. il faudrait certainement :
                        # Soit supprimer l'exercice côté Jalon
                        # Soit recréer l'exercice coté WIMS.
                    sur = "ERREUR"
                listeNotes.append({"note": "-",
                                   "sur": sur,
                                   "qualite": "-"})
        else:
            retour["message"] = rep["message"]

        retour["status"] = rep["status"]
        retour["qclass"] = param["qclass"]
        retour["qsheet"] = param["qsheet"]
        retour["user_cnt"] = 0
        retour["note"] = "-"
        retour["pourcentage"] = "-"
        retour["qualite"] = "-"
        retour["score_max"] = "-"
        retour["score_mean"] = "-"
        retour["data_scores"] = ""
        retour["listeNotes"] = listeNotes
        # retour["rep_wims"] = rep

        return retour

    def getNotesTableur(self, format="csv", site_lang="fr"):
        """renvoit les notes de l'activite courante, dans un format tableur (csv ou tsv)."""
        # LOG.info("----- getNotesTableur -----")
        separateurs = {"tsv": "\t", "csv": ";"}
        if format not in separateurs:
            format = "csv"
        sep = separateurs[format]

        # On vérifie que l'utilisateur connecté a bien le droit de modifier l'activité.
        membership_tool = self.portal_url.getPortalObject().portal_membership
        authMember = membership_tool.getAuthenticatedMember()
        if not self.checkRoles(user=authMember, function="getNotesTableur"):
            return _("Vous n'avez pas le droit de telecharger ce fichier. Vous devez vous identifier en tant qu'enseignant d'abord.")

        actif = self.isAfficherElement(self.dateAff, self.dateMasq)["val"]
        listeEtudiant = self.getNotes(authMember, actif, isProf, detailed=True, request="[jaloncourswims.py]/getNotesTableur")
        if self.idExam:
            entetes = [_("NOM"), _("PRENOM"), _("NUMERO ETU"), _("IDENTIFIANT"), _("NOMBRE d'ESSAIS"),
                       _(u"NOTE (sur ${max_score})", mapping={'max_score': self.getNoteMax()})]
        else:
            entetes = [_("NOM"), _("PRENOM"), _("NUMERO ETU"), _("IDENTIFIANT"), _("TAUX DE REUSSITE"),
                       _(u"QUALITE (sur ${max_score})", mapping={'max_score': self.getNoteMax()})]
        export = [sep.join(entetes)]

        for etudiant in listeEtudiant["data_scores"]:
            num_etu = '"%s"' % etudiant["num_etu"]
            id_etu  = '"%s"' % etudiant["id"]
            if self.idExam:
                score = '"%s"' % etudiant["score"]
                # if sep == ",":
                #    score = score.replace(",", ".")
                if site_lang == "fr":
                    score = score.replace(".", ",")
                ligne = [etudiant["last_name"], etudiant["first_name"], num_etu, id_etu, str(etudiant["attempts"]), score]
            else:
                note = '"%s %%"' % etudiant["user_percent"]
                qualite = '"%s"' % etudiant["user_quality"]
                if site_lang == "fr":
                    note = note.replace(".", ",")
                    qualite = qualite.replace(".", ",")
                # if sep == ",":
                #    qualite = qualite.replace(",", ".")
                ligne = [etudiant["last_name"], etudiant["first_name"], num_etu, id_etu, note, qualite]
            export.append(sep.join(ligne))
        return "\n".join(export)

    def getRubriqueEspace(self, ajout=None):
        """get Rubrique Espace."""
        # LOG.info("----- getRubriqueEspace -----")
        rubriques = []
        for rubrique in ["Fichiers", "Presentations sonorisees", "Ressources Externes", "Webconference"]:
            rubriques.append({"rubrique": jalon_utils.jalon_quote(rubrique), "titre": rubrique})
        return rubriques

    def getTagDefaut(self):
        """getTagDefaut."""
        # LOG.info("----- getTagDefaut -----")
        return jalon_utils.getTagDefaut(self)

    def getUserLog(self, quser, authUser, isProf, option="score"):
        u"""Renvoit les logs de connexion à wims de l'utilisateur quser.

        # Par defaut, on filtre les infos de type "noscore"
        # On ne fournit les informations de log qu'a un enseignant du cours, ou l'etudiant lui-même

        """
        # LOG.info("----- getUserLog -----")
        param = {}
        if (isProf or quser == authUser):
            param["job"]    = "getlog"
            param["qclass"] = self.getClasse()
            param["quser"]  = quser
            param["code"]   = authUser
            if self.idExam:
                param["qexam"] = self.getIdExam()
                option = "exams"
            else:
                param["qsheet"] = self.getIdFeuille()
            param["option"] = option
            rep_wims = self.wims("callJob", param)
        else:
            rep_wims = '{"status": "ERROR", "message": "Seul un enseignant ou un etudiant lui-même peut avoir accès a ses logs de connexion"}'

        rep_wims = self.wims("verifierRetourWims", {"rep": rep_wims,
                                                    "fonction": "jaloncourswims.py/getUserLog",
                                                    "message": "parametres de la requete : %s" % param})
        rep_wims["fullname"] = jalon_utils.getIndividu(quser, "dict")["fullname"]
        # On enleve un eventuel element vide a la liste :
        try:
            rep_wims["user_log"].remove("")
        except:
            pass

        if rep_wims["status"] == "ERROR":
            if "error_code" in rep_wims and rep_wims["error_code"] == "450":
                message = _(u"La ressource que vous tentez d'afficher est trop importante et dépasse la limite autorisée.")
            else:
                message = _(u"Merci de contacter l'administrateur de cette plateforme, en fournissant tous les détails possible permettant de reproduire cette erreur svp.")
            if "error_reason" in rep_wims:
                message = "<p>%s</p><strong>%s</strong>" % (message, rep_wims["error_reason"])
            self.plone_utils.addPortalMessage(message, type='error')

        # print "Retour WIMS de getUserLog : %s " % rep_wims
        return rep_wims

    def getWimsLang(self, site_lang=''):
        u"""Renvoie le code de langue de l'interface des exercices.

        # Cela correspond par défaut a la langue du site, sinon à la langue choisie par l'enseignant

        """
        # LOG.info("----- getWimsLang -----")
        if site_lang != '' and self.getWims_lang() == '':
            return jalon_utils.convertLangToWIMS(site_lang)
        else:
            return self.getWims_lang()

    def isActif(self):
        u"""Permet de savoir si l'activité courante est active (affichée ou masquée)."""
        # LOG.info("----- isActif -----")
        return self.isAfficherElement(self.dateAff, self.dateMasq)["val"] == 1

    def isAfficherElement(self, affElement, masquerElement):
        """isAfficherElement aLias to jalon_utils."""
        # LOG.info("----- isAfficherElement ? -----")
        return jalon_utils.isAfficherElement(affElement, masquerElement)

    def getParentPlanElement(self, idElement, idParent, listeElement):
        """get Parent Plan Element."""
        # LOG.info("----- getParentPlanElement -----")
        if idElement == self.getId():
            return self.aq_parent.getParentPlanElement(idElement, idParent, listeElement)
        return {"idElement": "racine", "affElement": "", "masquerElement": ""}

    def isChecked(self, idElement, formulaire, listeElement=None):
        """isChecked."""
        # LOG.info("----- isChecked -----")
        if formulaire == "ajout-sujets":
            if idElement in list(self.getListeSujets()):
                return 1
        elif idElement in list(self.getListeExercices()):
            return 1
        return 0

    def modifierExoFeuille(self, form):
        """modifie un exo de l'activite."""
        # LOG.info("----- modifierExoFeuille -----")

        param = {}
        param["qexo"]   = int(form["qexo"]) + 1
        param["qclass"] = self.getClasse()
        param["qsheet"] = self.getIdFeuille()
        param["title"]  = form["titreElement"].decode("utf-8")
        param["weight"] = form["weight"]

        # On vérifie que l'utilisateur connecté a bien le droit de modifier l'activité.
        membership_tool = self.portal_url.getPortalObject().portal_membership
        authMember = membership_tool.getAuthenticatedMember()
        if not self.checkRoles(user=authMember, function="modifierExoFeuille"):
            return None

        param["authMember"]  = authMember.getId()

        resp = self.wims("modifierExoFeuille", param)
        if resp["status"] == "OK":
            message = _(u"Le coefficient de l'exercice '${item_title}' a bien été modifié.",
                        mapping={'item_title': param["title"]})
            self.plone_utils.addPortalMessage(message, type='success')

    """
        # Remplacé par removeExercice()
    def retirerElement(self, idElement, menu, ordre=None):
        # détache un élément de l'activité.
        # LOG.info("----- retirerElement -----")
        # On recupere la liste des elements :
        liste_elements = self.getDocumentsProperties()

        # On met à jour la liste des elements du menu
        menu_list = list(self.__getattribute__("liste%s" % menu.capitalize()))
        menu_list.remove(idElement)
        self.__getattribute__("setListe%s" % menu.capitalize())(tuple(menu_list))

        # On demande les infos de l'element à supprimer
        if idElement in liste_elements:
            infosElement = liste_elements[idElement]
            # On supprime l'element de la liste
            del liste_elements[idElement]

        repertoire = infosElement["typeElement"]
        if repertoire in _dicoRep:
            repertoire = _dicoRep[repertoire]
        if "*-*" in idElement:
            idElement = idElement.replace("*-*", ".")
        if repertoire == "Wims":
            auteur = self.getCreateur()
            idClasse = self.getClasse()
            idFeuille = self.getIdFeuille()
            idEexo = int(ordre) + 1
            # Supprime l'exercice de la feuille côté WIMS
            dico = {"authMember": auteur,
                    "qclass": idClasse,
                    "qsheet": idFeuille,
                    "qexo": idEexo,
                    "jalon_URL": self.absolute_url()}
            self.wims("retirerExoFeuille", dico)

        # Supprime l'activité des relatedItems de l'objet retiré.
        objet = getattr(getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), infosElement["createurElement"]), repertoire), idElement)
        relatedItems = objet.getRelatedItems()
        if self in relatedItems:
            relatedItems.remove(self)
            objet.setRelatedItems(relatedItems)
            objet.reindexObject()
    """

    def removeAllElements(self, force_WIMS=False):
        """Retire tous les elements de l'activite (exercices et documents)."""
        # anciennement "retirerTousElements"
        # LOG.info("----- removeAllElements -----")
        # Concernant les exercices, on n'execute l'opération que si :
        # * force_WIMS=True (cas où on supprime l'intégralité des activités du cours)
        # * TODO : ou c'est une autoéval masquée
        # * TODO : ou c'est un exam non verrouillé
        if force_WIMS is True:
            liste_exos_id = self.getListeExercices()
            createur = self.getCreateur()
            # On se place dans l'espace WIMS de createurElement
            portal_members = getattr(self.portal_url.getPortalObject(), "Members")
            espace_WIMS = getattr(getattr(portal_members, createur), "Wims")

            # Pour chaque exo
            for id_exo in liste_exos_id:
                # on coupe sa relation avec l'activité à supprimer.
                exo = getattr(espace_WIMS, id_exo)
                exo.removeRelatedItem(self)

        # else:
        # TODO : Suppression côté WIMS (seulement dans les cas autorisés)
        # Pour le moment, cette fonction n'est appelée que par supprimerActivitesWims, mais si on veut
        # if ....:
        # idClasse = self.getClasse()
        # idFeuille = self.getIdFeuille()

        # Supprime les exercices de la feuille côté WIMS
        # dico = {"authMember": auteur, "qclass": idClasse, "qsheet": idFeuille}
        # ICI il faut voir si coté WIMS on a un job qui permet de supprimer d'un coup tous les exos d'une feuille.
        # self.wims("retirerExosFeuille", dico)

        # Suppression des documents
        items_properties = self.getDocumentsProperties()
        for document in self.getListeSujets():
            infosElement = items_properties[document]
            repertoire = infosElement["typeElement"]
            if repertoire in _dicoRep:
                repertoire = _dicoRep[repertoire]
            if "*-*" in document:
                document = document.replace("*-*", ".")
            doc_object = getattr(getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), infosElement["createurElement"]), repertoire), document, None)
            if doc_object:
                relatedItems = doc_object.getRelatedItems()
                if self in relatedItems:
                    relatedItems.remove(self)
                    doc_object.setRelatedItems(relatedItems)
                    doc_object.reindexObject()

    def getIdFeuilleWIMS(self, authMember, sheet_properties={}):
        u"""Obtention (et eventuellement Création) d'un identifiant Wims pour la feuille."""
        # LOG.info("----- getIdFeuilleWIMS -----")
        idFeuille = self.getIdFeuille()
        # Cas ou la feuille n'existe pas côté WIMS
        if not idFeuille:
            # Si sheet_properties n'est pas donné, c'est que l'activité existe côté Jalon mais pas côté WIMS.
            if "Title" not in sheet_properties:
                sheet_properties["Title"] = self.Title()
                sheet_properties["Description"] = self.Description()
            # On crée la classe si elle n'existe pas.
            idclasse = self.setClasse()
            if idclasse:
                if self.typeWims == "Examen":
                    sheet_title = "Feuille dediée à l'examen '%s'" % sheet_properties["Title"]
                else:
                    sheet_title = sheet_properties["Title"]
                # Quelque soit le type d'activité, on cree une feuille d'entrainement sur Wims (Elle servira également à mettre les exercices d'un examen)
                reponse = self.wims("creerFeuille", {"authMember": authMember, "title": sheet_title, "description": sheet_properties["Description"], "qclass": idclasse})
                if reponse["status"] != "OK":
                    return None
                idFeuille = str(reponse["sheet_id"])
                self.idFeuille = idFeuille

        return idFeuille

    def setJalonProperties(self, dico={}):
        u"""Modifie les propriétés de l'objet jalonCoursWims courant (Autoevaluation ou Examen), coté Jalon uniquement.

        # attention, cette fonction n'effectue volontairement aucun controle côté WIMS. Assurez-vous de définir des propriétés valables.
        # Utilisé notemment lors de la duplication de cours

        """
        # LOG.info("----- setJalonProperties -----")
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])

        if "DateDerniereModif" in dico.keys():
            # self.plone_log("DateDerniereModif")
            self.reindexObject()
        return dico

    """
    def setAttributActivite(self, form):
        # modifie les attribut de l'objet jaloncourswims.
        # LOG.info("----- setAttributActivite -----")
        for key in form.keys():
            method_name = "set%s%s" % (key[0].upper(), key[1:])
            try:
                self.__getattribute__(method_name)(form[key])
            except AttributeError:
                pass
        if "title" in form:
            # self.aq_parent.modifierInfosElementPlan(self.getId(), form["Title"])
            self.aq_parent.editCourseMapItem(self.getId(), form["title"], item_display_in_course_map)
        self.setProperties()
        """

    def setProperties(self, dico={}):
        u"""Modifie les propriétés de l'objet jalonCoursWims courant, ainsi que son homologue côté WIMS.

        # dico est renseigné lors de la création de l'objet. (issu de creerSousObjet de jaloncours)
        # Attention : si on modifie un parametre a l'interieur d'une fonction,
        #   celui-ci sera persistant et reviendra tel quel au prochain appel de la fonction
        #   si ce parametre n'est pas obligatoire. (cas de dico ici)

        """
        # LOG.info("----- setProperties -----")
        auteur = self.getCreateur()

        # On met à jour les propriétés côté Jalon
        for key in dico.keys():
            # method_name = "set%s%s" % (key[0].upper(), key[1:])
            # self.__getattribute__(method_name)(form[key])
            self.__getattribute__("set%s" % key)(dico[key])

        # Puis on le fait côté WIMS :

        # Cas où la feuille existe déjà sur WIMS
        if self.idFeuille:
            proprietes = {}
            proprietes["qclass"] = self.getClasse()
            proprietes["qsheet"] = self.idFeuille

            proprietes["authMember"]  = auteur
            proprietes["description"] = self.Description()
            if self.typeWims == "Examen":
                proprietes["title"] = "Feuille dediée à l'examen '%s'" % self.Title()
                self.wims("modifierFeuille", proprietes)

                proprietes["title"]     = self.Title()
                # LOG.info("proprietes['title']=%s" % proprietes["title"])
                proprietes["duration"]  = self.duree
                proprietes["attempts"]  = self.attempts
                proprietes["cut_hours"] = self.cut_hours

                # si l'examen existe deja, on lui applique les modifications
                if self.idExam:
                    # Une fois un examen activé, on ne peut plus le désactiver. le statut passe à 3 (périmé+caché) pour le masquer
                    proprietes["qexam"] = self.idExam
                    self.wims("modifierExamen", proprietes)
            else:
                proprietes["title"] = self.Title()
                self.wims("modifierFeuille", proprietes)
        else:
            # Cas ou la feuille n'existe pas encore sur WIMS
            # self.typeWims = self.aq_parent.getTypeSousObjet(self.getId())
            self.typeWims = self.getId().split("-")[0]

            # On crée la feuille côté WIMS
            self.getIdFeuilleWIMS(auteur, dico)

        self.reindexObject()

    def isFileOfTypes(self, file_object, file_name, required_types):
        """Return True if file_object type is in required_types list."""
        # LOG.info("----- isFileOfType -----")
        from collective.quickupload.browser.quick_upload import get_content_type
        content_type = get_content_type(self, file_object, file_name)

        # LOG.info("CONTENT TYPE = %s" % content_type)
        return (content_type in required_types)

    def importHotPotatoes(self, user_id, import_file):
        """Importe un ensemble d'exercice hotpotatoes, les place dans Mes ressources et dans l'autoevaluation/examen."""
        # LOG.info("----- importHotPotatoes -----")
        portal = self.portal_url.getPortalObject()
        wims_folder = getattr(getattr(portal.Members, user_id), "Wims")
        questions_list = portal.portal_wims.importHotPotatoes(wims_folder, user_id, import_file)
        # LOG.info("questions_list = %s" % questions_list)
        index = 1
        portal_workflow = getToolByName(portal, "portal_workflow")
        for question_dict in questions_list:
            # [TODO] ici il faudrait verifier le retour de question_dict pour savoir si tout s'est bien passé.
            self.addMySpaceItem(folder_object=wims_folder,
                                item_id=question_dict["id_jalon"],
                                item_type="Exercice Wims",
                                user_id=user_id,
                                display_item="",
                                map_position=None,
                                display_in_plan=False,
                                portal_workflow=portal_workflow)
            index = index + 1

    def getShortText(self, text, limit=75):
        """getShortText."""
        # LOG.info("----- getShortText -----")
        return jalon_utils.getShortText(text, limit)

    def supprimerMarquageHTML(self, chaine):
        """Suppression marquage HTML."""
        # LOG.info("----- supprimerMarquageHTML -----")
        return jalon_utils.supprimerMarquageHTML(chaine)

    def wims(self, methode, param):
        """permet d'appeler la methode definie en parametre depuis le connecteur wims, en lui envoyant le dico "param"."""
        # LOG.info("----- wims(%s) -----" % methode)
        return self.portal_wims.__getattribute__(methode)(param)

    """
    def majActiviteWims(self):
        #Mise à jour des activités WIMS.

        #Pour utiliser cette fonction :
        #1 - décommenter import ATExtensions puis RecordField infos_element
        #2 - mettre getInfosElement en commentaire
        #3 - appeler cette fonction depuis un script en ZMI

        # LOG.info("----- majActiviteWims -----")
        listeSujets = list(self.getListeSujets())
        listeExercices = list(self.getListeExercices())
        listeSujets.extend(listeExercices)

        infos_element = self.getInfosElement()
        if infos_element:
            dico = {}
            dicoElements = copy.deepcopy(infos_element)
            for idElement in listeSujets:
                if idElement in dicoElements:
                    dico[idElement] = {"titreElement": dicoElements[idElement]["titreElement"],
                                       "typeElement": dicoElements[idElement]["typeElement"],
                                       "createurElement": dicoElements[idElement]["createurElement"],
                                       "affElement": dicoElements[idElement]["affElement"],
                                       "masquerElement": dicoElements[idElement]["masquerElement"]}
            self.setInfosElement(dico)
    """


registerATCT(JalonCoursWims, PROJECTNAME)
