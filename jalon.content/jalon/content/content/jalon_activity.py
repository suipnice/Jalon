# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.Archetypes.public import *
#from Products.ATExtensions.ateapi import *

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.base import registerATCT

from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonActivity

from DateTime import DateTime

# Messages de debug :
from logging import getLogger
LOG = getLogger("[JalonActivity]")


class JalonActivity(ATFolder):
    """ Une activité pour Jalon
    """

    implements(IJalonActivity)
    meta_type = 'JalonActivity'

    ##--------------------------##
    # Fonctions onglet Documents #
    ##--------------------------##
    def isChecked(self, idElement, formulaire, listeElement=None):
        if formulaire == "ajout-sujets":
            if idElement in list(self.getListeSujets()):
                return 1
            return 0
        if formulaire == "ajout-corrections":
            if idElement in list(self.getListeCorrections()):
                return 1
            return 0

    def editCourseItemVisibility(self, item_id, item_date, item_property_name, is_update_from_title=False):
        LOG.info("----- editCourseItemVisibility -----")
        u""" Modifie l'etat de la ressource quand on modifie sa visibilité ("attribut" fournit l'info afficher / masquer)."""
        is_deposit_box = True if item_id == self.getId() else False

        if is_deposit_box:
            course = self.aq_parent
            if item_property_name == "affElement":
                self.dateAff = item_date
                self.dateMasq = ""
            else:
                self.dateMasq = item_date
                course.deleteCourseActuality(item_id)
            course.editCourseItemVisibility(item_id, item_date, item_property_name, False)
            course.setCourseProperties({"DateDerniereModif": DateTime()})
        else:
            item_properties = self.getDocumentsProperties(item_id)
            if item_property_name == "affElement":
                item_properties["masquerElement"] = ""
            item_properties[item_property_name] = item_date
            self._infos_element[item_id] = item_properties
            self.setDocumentsProperties(self._infos_element)

    def addMySpaceItem(self, folder_object, item_id, item_type, user_id, display_item, map_position, display_in_plan, portal_workflow):
        LOG.info("----- addMySpaceItem -----")
        item_id_no_dot = item_id.replace(".", "*-*")

        item_object = getattr(folder_object, item_id)

        complement_element = None
        if item_type in ["Video", "VOD"]:
            complement_element = {"value":  display_in_plan,
                                  "auteur": item_object.getVideoauteurname(),
                                  "image":  item_object.getVideothumbnail()}

        item_object_related = item_object.getRelatedItems()
        if not self in item_object_related:
            item_object_related.append(self)
            item_object.setRelatedItems(item_object_related)
            item_object.reindexObject()

        deposit_box_related = self.getRelatedItems()
        if not item_object in deposit_box_related:
            deposit_box_related.append(item_object)
            self.setRelatedItems(deposit_box_related)

        self.addItemProperty(item_id_no_dot, item_type, item_object.Title(), user_id, display_item, complement_element)

    def addItemProperty(self, item_id, item_type, item_title, item_creator, display_item, complement_element):
        LOG.info("----- addItemProperty -----")

        items_properties = self.getDocumentsProperties()
        if not item_id in items_properties:
            items_properties[item_id] = {"titreElement":    item_title,
                                         "typeElement":     item_type,
                                         "createurElement": item_creator,
                                         "affElement":      display_item,
                                         "masquerElement":  ""}

            if complement_element:
                items_properties[item_id]["complementElement"] = complement_element
            self.setDocumentsProperties(items_properties)
            listeSujets = list(self.getListeSujets())
            listeSujets.append(item_id)
            setattr(self, "listeSujets", tuple(listeSujets))

    def displayDocumentsList(self, is_personnel, portal):
        LOG.info("----- displayDocumentsList -----")
        course_parent = self.aq_parent

        documents_list = []
        documents_dict = self.getDocumentsProperties()
        for document_id in self.getDocumentsList():
            document_properties = documents_dict[document_id]

            document_dict = {"document_id":      document_id,
                             "document_title":   document_properties["titreElement"],
                             "document_drop_id": "drop-%s" % document_id.replace("*-*", ""),
                             "document_link":    ""}

            is_display_item = self.isAfficherElement(document_properties["affElement"], document_properties["masquerElement"])
            document_dict["is_display_item_bool"] = True if is_display_item["val"] else False
            document_dict["is_display_item_icon"] = "fa %s fa-fw fa-lg no-pad right alert" % is_display_item["icon"]
            document_dict["is_display_item_text"] = is_display_item["legende"]

            if is_personnel or document_dict["is_display_item_bool"]:
                document_dict["document_link"] = "/".join([portal.absolute_url(), "Members", document_properties["createurElement"], course_parent._type_folder_my_space_dict[document_properties["typeElement"].replace(" ", "")], document_id.replace("*-*", "."), "view"])
            if is_personnel:
                document_dict["document_actions"] = self.getItemActions(course_parent, document_properties, document_dict["is_display_item_bool"])
            documents_list.append(document_dict)
        return documents_list

    def getItemActions(self, course_parent, item_properties, is_display_item_bool):
        LOG.info("----- getItemActions -----")
        item_actions = course_parent._item_actions[:]

        if is_display_item_bool:
            del item_actions[0]
        else:
            del item_actions[1]

        del item_actions[-1]
        del item_actions[-2]
        del item_actions[-2]

        return item_actions

    def getDisplayItemForm(self, item_id):
        LOG.info("----- getDisplayItemForm -----")
        form_properties = {"is_authorized_form":       True,
                           "is_item_title":            False,
                           "is_item_parent_title":     False,
                           "help_css":                 "panel callout radius",
                           "help_text":                "Vous êtes sur le point d'afficher cette ressource à vos étudiants.",
                           "is_wims_examen":           False}
        if self.getId() == item_id:
            form_properties = self.aq_parent.getDisplayItemForm(item_id)
        else:
            item_properties = self.getDocumentsProperties(item_id)
            display_properties = self.isAfficherElement(item_properties["affElement"], item_properties["masquerElement"])
            if display_properties["val"]:
                form_properties["help_text"] = "Vous êtes sur le point de masquer cette ressource à vos étudiants."
                form_properties["help_css"] = "panel radius warning"
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
                form_properties["item_date"] = self.getDisplayOrHiddenDate(item_properties, "masquerElement")
            else:
                form_properties["form_button_css"] = "button small radius"
                form_properties["form_button_directly_text"] = "Afficher l'élément maintenant"
                form_properties["form_button_lately_text"] = "Programmer l'affichage de l'élément à l'instant choisi"
                form_properties["item_property_name"] = "affElement"
                form_properties["form_title_text"] = "Afficher l'élément : %s" % item_properties["titreElement"]
                form_properties["form_title_icon"] = "fa fa-eye no-pad"

                form_properties["text_title_lately"] = "… ou programmer son affichage."
                if item_properties["typeElement"] == "Titre":
                    form_properties["is_item_title"] = True
                    form_properties["text_title_directly"] = "Afficher directement le titre / sous titre et son contenu…"
                    form_properties["wims_help_text"] = True
                else:
                    form_properties["text_title_directly"] = "L'afficher directement…"
                    form_properties["wims_help_text"] = False

                form_properties["form_name"] = "afficher-element"
                form_properties["item_date"] = self.getDisplayOrHiddenDate(item_properties, "affElement")

        return form_properties

    def getDisplayOrHiddenDate(self, item_properties, attribut):
        LOG.info("----- getDisplayOrHiddenDate -----")
        LOG.info("***** item_properties : %s" % item_properties)
        if item_properties[attribut] != "":
            LOG.info("***** attribut: %s" % attribut)
            LOG.info("***** item_properties[attribut]: %s" % item_properties[attribut])
            return item_properties[attribut].strftime("%Y/%m/%d %H:%M")
        return DateTime().strftime("%Y/%m/%d %H:%M")

    def detachDocument(self, item_id):
        LOG.info("----- detachDocument -----")
        document_properties = self.getDocumentsProperties()
        document_dict = document_properties[item_id]
        del document_properties[item_id]
        self.setDocumentsProperties(document_properties)

        documents_list = list(self.getListeSujets())
        documents_list.remove(item_id)
        self.setListeSujets(tuple(documents_list))

        item_object = getattr(getattr(getattr(self.portal_url.getPortalObject().Members, document_dict["createurElement"]), self.aq_parent._type_folder_my_space_dict[document_dict["typeElement"].replace(" ", "")]), item_id.replace("*-*", "."))
        item_relatedItems = item_object.getRelatedItems()
        item_relatedItems.remove(self)
        item_object.setRelatedItems(item_relatedItems)
        item_object.reindexObject()

        deposit_relatedItems = self.getRelatedItems()
        deposit_relatedItems.remove(item_object)
        self.setRelatedItems(deposit_relatedItems)

        self.reindexObject()

registerATCT(JalonActivity, PROJECTNAME)
