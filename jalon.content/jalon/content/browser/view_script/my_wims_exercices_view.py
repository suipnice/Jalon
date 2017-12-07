# -*- coding: utf-8 -*-
"""View scripts associated to my_wims_exercices_view.pt template."""

from zope.component import getMultiAdapter
from my_space_view import MySpaceView

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[MyWimsExercicesView]')


class MyWimsExercicesView(MySpaceView):
    """Class View du fichier my_wims_exercices_view.pt."""

    def __init__(self, context, request):
        """Initialize th view class."""
        # LOG.info("----- Init -----")
        MySpaceView.__init__(self, context, request)
        self.context = context
        self.request = request

    def getBreadcrumbs(self):
        """Fournit le fil d'ariane de la vue."""
        return [{"title": _(u"Mes ressources"),
                 "icon":  "fa fa-folder-open",
                 "link":  self.context.aq_parent.absolute_url()},
                {"title": _(u"Mes exercices WIMS"),
                 "icon":  "fa fa-random",
                 "link":  self.context.absolute_url()}]

    def getMyWimsExercicesView(self, user):
        """Fournit la vue "Mes Exercices"."""
        # LOG.info("----- getMyWimsExercicesView -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        user_id = user.getId()
        folder = getattr(portal.Members, user_id).Wims

        selected_tags_list = folder.getSelectedTags().split(",")

        tags = self.getTags(folder, selected_tags_list)
        tags_dict = tags["tags_dict"]
        tags_list = tags["tags_list"]

        portal_wims = getattr(portal, "portal_wims", None)
        my_wims_exercices_list = self.getMyWimsExercicesList(folder, selected_tags_list, user_id, portal_wims)

        one_and_selected_tag = self.getOneAndSelectedTag(my_wims_exercices_list, selected_tags_list, tags_dict)

        try:
            # dans ce cas, my_wims_exercices_list est un object dont la fonction "len" est deprecated.
            nb_display_items = my_wims_exercices_list.length
        except AttributeError:
            # dans ce cas, my_wims_exercices_list est un 'LazyMap' object, qui n'a pas d'attribut 'length'
            nb_display_items = len(my_wims_exercices_list)

        nb_items = len(folder.objectIds())

        wims_exercice_model_list = folder.getModelesWims()

        return {"tags_list":                tags_list,
                "is_no_items":              one_and_selected_tag["is_no_items"],
                "is_one_tag":               one_and_selected_tag["is_one_tag"],
                "one_tag":                  one_and_selected_tag["one_tag"],
                "is_selected_tags":         one_and_selected_tag["is_selected_tags"],
                "my_items_list":            my_wims_exercices_list,
                "nb_display_items":         nb_display_items,
                "nb_items":                 nb_items,
                "folder_path":              "/".join(folder.getPhysicalPath()),
                "folder_link":              folder.absolute_url(),
                "wims_exercice_model_list": wims_exercice_model_list}

    def getMyWimsExercicesList(self, folder, selected_tags_list, user_id, portal_wims):
        """Fournit la liste des exercices WIMS de user_id."""
        # LOG.info("----- getMyWimsExercicesList -----")
        # LOG.info("selected_tags_list = ##%s##" % selected_tags_list)
        member_wims_class = folder.getComplement()
        if not member_wims_class:
            self.createWimsClass(folder, user_id, portal_wims)
        elif selected_tags_list == [""]:
            # On ne met à jour la liste des exos que si aucune étiquette est selectionnée.
            folder.updateJalonExercicesWims(user_id, member_wims_class, portal_wims)
        content_filter = {"portal_type": ["JalonExerciceWims"]}
        return self.getItemsList(folder, selected_tags_list, content_filter)

    def createWimsClass(self, folder, user_id, portal_wims):
        u"""Crée le groupement de classes WIMS pour un nouvel utilisateur si il n'existe pas déjà."""
        # LOG.info("----- createWimsClass -----")
        # 1er  cas : Aucune classe n'existe pour cet utilisateur
        member_properties = self.context.getIndividu(user_id, "dict")
        member_email = member_properties["email"]
        member_fullname = member_properties["fullname"]
        # Création du groupement de classes
        groupement_wims_class = portal_wims.creerClasse({"authMember": user_id,
                                                         "fullname":   member_fullname,
                                                         "auth_email": member_email,
                                                         "type":       "2",
                                                         "qclass":     ""})
        # Création de la 1ere classe dans le groupement (elle contiendra tous les exos)
        if groupement_wims_class["status"] == "OK":
            wims_class_id = portal_wims.creerClasse({"authMember":   user_id,
                                                     "fullname":     member_fullname,
                                                     "auth_email":   member_email,
                                                     "type":         "0",
                                                     "titre_classe": "Mes exercices",
                                                     "qclass":       groupement_wims_class["class_id"]})
            if wims_class_id:
                folder.complement = str(groupement_wims_class["class_id"])
                return {"status": "OK", "member_wims_class": folder.complement}
        else:
            # print "*****    Mauvais parametrage de votre connexion WIMS  *****"
            # print "[my_wims_exercices.py/createWimsClass] Creation du groupement impossible"
            # print " Reponse WIMS : %s" % groupement
            # print "*****                                                 *****"
            return {"status": "ERROR", "message": "wims_bad_conf"}
