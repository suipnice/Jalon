# -*- coding: utf-8 -*-
"""jalon_activity.py definit la class JalonActivity."""
from zope.interface import implements

# from Products.Archetypes.public import *
from OFS.SimpleItem import SimpleItem

from jalon.content.interfaces import IJalonActivity
from jalon.content import contentMessageFactory as _

from DateTime import DateTime

# Messages de debug :
from logging import getLogger
LOG = getLogger("[JalonActivity]")


class JalonActivity(SimpleItem):
    u"""Une activité d'un cours Jalon."""

    implements(IJalonActivity)
    meta_type = 'JalonActivity'

    # -------------------------- #
    # Fonctions onglet Documents #
    # -------------------------- #
    def isChecked(self, idElement, formulaire, listeElement=None):
        """check if idElement is checked."""
        # LOG.info("----- isChecked -----")
        if formulaire == "ajout-sujets":
            if idElement in list(self.getListeSujets()):
                return 1
            return 0
        if formulaire == "ajout-corrections":
            if idElement in list(self.getListeCorrections()):
                return 1
            return 0

    def editCourseItemVisibility(self, item_id, item_date, item_property_name, is_update_from_title=False):
        u"""Modifie l'etat de la ressource quand on modifie sa visibilité."""
        # LOG.info("----- editCourseItemVisibility -----")
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
        """Met a jour les related Items de l'activité et de l'element de Mes ressources qu'on lui ajoute."""
        # LOG.info("----- addMySpaceItem -----")
        item_id_no_dot = item_id.replace(".", "*-*")

        item_object = getattr(folder_object, item_id)

        complement_element = None
        if item_type in ["Video", "VOD"]:
            complement_element = {"value":  display_in_plan,
                                  "auteur": item_object.getVideoauteurname(),
                                  "image":  item_object.getVideothumbnail()}

        item_object_related = item_object.getRelatedItems()
        if self not in item_object_related:
            item_object_related.append(self)
            item_object.setRelatedItems(item_object_related)
            item_object.reindexObject()

        activity_related = self.getRelatedItems()
        if item_object not in activity_related:
            activity_related.append(item_object)
            self.setRelatedItems(activity_related)

        return {"item_id_no_dot":  item_id_no_dot,
                "item_type":       item_type,
                "item_title":      item_object.Title(),
                "item_complement": complement_element,
                "item_object":     item_object}
        # self.addItemProperty(item_id_no_dot, item_type, item_object.Title(), user_id, display_item, complement_element)

    def addItemProperty(self, item_id, item_type, item_title, item_creator, display_item, complement_element):
        """Ajoute un element à la liste des sujets d'une activité."""
        # LOG.info("----- addItemProperty -----")

        items_properties = self.getDocumentsProperties()
        if item_id not in items_properties:
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
            message = _(u"'${item_title}' a bien été ajouté aux documents enseignants.",
                        mapping={'item_title': item_title.decode("utf-8")})
            self.plone_utils.addPortalMessage(message, type='success')

    def displayDocumentsList(self, is_personnel, portal):
        """Fournit la liste des documents à afficher."""
        # LOG.info("----- displayDocumentsList -----")
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

    def getCourseItemProperties(self, key=None):
        # LOG.info("----- getCourseItemProperties -----")
        return self.getDocumentsProperties(key)

    def getItemActions(self, course_parent, item_properties, is_display_item_bool):
        """Fournit la liste des actions possibles pour un sous-element "item_properties" de l'activité."""
        # LOG.info("----- getItemActions -----")
        item_actions = course_parent._item_actions[:]

        if is_display_item_bool:
            del item_actions[0]
        else:
            del item_actions[1]

        # Retire l'option "supprimer"
        del item_actions[-1]
        # Retire l'option "jalonner"
        del item_actions[-2]
        # Retire l'option "modifier"
        del item_actions[-2]

        return item_actions

    def getDisplayItemForm(self, item_id):
        """Fournit les infos du formulaire d'affichage/masquage de l'activité."""
        # LOG.info("----- getDisplayItemForm -----")
        if self.getId() == item_id:
            # Pour l'affichage de l'activité elle-même, on fait appel à la fonction getDisplayItemForm() du cours.
            form_properties = self.aq_parent.getDisplayItemForm(item_id)
        else:
            # Pour l'affichage des elements inclus dans l'activité, on appelle getDisplayItemFormProperties() du cours.
            item_properties = self.getDocumentsProperties(item_id)
            form_properties = self.aq_parent.getDisplayItemFormProperties(item_properties)

        return form_properties

    def getDocumentsProperties(self, key=None):
        """get Properties for one or all Documents."""
        # LOG.info("----- getDocumentsProperties (%s) -----" % self.getId())
        if key:
            return self._infos_element.get(key, None)
        return self._infos_element

    def detachDocument(self, item_id):
        # LOG.info("----- detachDocument -----")
        document_properties = self.getDocumentsProperties()
        document_dict = document_properties[item_id]
        del document_properties[item_id]
        self.setDocumentsProperties(document_properties)

        documents_list = list(self.getListeSujets())
        documents_list.remove(item_id)
        self.setListeSujets(tuple(documents_list))

        item_object = getattr(getattr(getattr(self.portal_url.getPortalObject().Members, document_dict["createurElement"]), self.aq_parent._type_folder_my_space_dict[document_dict["typeElement"].replace(" ", "")]), item_id.replace("*-*", "."))
        item_relatedItems = item_object.getRelatedItems()
        if self in item_relatedItems:
            item_relatedItems.remove(self)
            item_object.setRelatedItems(item_relatedItems)
            item_object.reindexObject()

        activity_relatedItems = self.getRelatedItems()
        activity_relatedItems.remove(item_object)
        self.setRelatedItems(activity_relatedItems)

        self.reindexObject()

    def detachAllDocuments(self):
        # LOG.info("----- detachAllDocuments -----")
        document_properties = self.getDocumentsProperties()
        #document_dict = document_properties[item_id]
        #del document_properties[item_id]
        #self.setDocumentsProperties(document_properties)

        documents_list = list(self.getListeSujets())
        #documents_list.remove(item_id)
        #self.setListeSujets(tuple(documents_list))

        for item_id in documents_list:
            document_dict = document_properties[item_id]
            item_object = getattr(getattr(getattr(self.portal_url.getPortalObject().Members, document_dict["createurElement"]), self.aq_parent._type_folder_my_space_dict[document_dict["typeElement"].replace(" ", "")]), item_id.replace("*-*", "."))
            item_relatedItems = item_object.getRelatedItems()
            item_relatedItems.remove(self)
            item_object.setRelatedItems(item_relatedItems)
            item_object.reindexObject()

        #activity_relatedItems = self.getRelatedItems()
        #activity_relatedItems.remove(item_object)
        #self.setRelatedItems(activity_relatedItems)

        self.reindexObject()
