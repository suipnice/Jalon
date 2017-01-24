# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from my_space_view import MySpaceView

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[MyExternalResourcesView]')


class MyExternalResourcesView(MySpaceView):
    """ Class View du fichier my_external_resources_view.pt
    """

    def __init__(self, context, request):
        # LOG.info("----- Init -----")
        MySpaceView.__init__(self, context, request)
        self.context = context
        self.request = request

    def getBreadcrumbs(self):
        return [{"title": _(u"Mes ressources"),
                 "icon":  "fa fa-folder-open",
                 "link":  self.context.aq_parent.absolute_url()},
                {"title": _(u"Mes ressources externes"),
                 "icon":  "fa fa-external-link",
                 "link":  self.context.absolute_url()}]

    def getMyExternalResourcesView(self, user):
        # LOG.info("----- getMyExternalResourcesView -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        folder = getattr(portal.Members, user.getId()).Externes

        nb_button_action = 0
        is_two_actions = False
        item_adder_list = []
        jalon_properties = portal.portal_jalon_properties.getPropertiesMonEspace()
        if jalon_properties["activer_liens"]:
            item_adder_list.append({"action_name":      "Créer un lien",
                                    "action_icon":      "fa fa-plus-circle",
                                    "action_css_class": "button expand create",
                                    "action_link":      "create_external_resource_form"})
            nb_button_action += 1
        if jalon_properties["activer_liens_catalogue_bu"]:
            item_adder_list.append({"action_name":      "Rechercher et ajouter depuis le catalogue BU",
                                    "action_icon":      "fa fa-search",
                                    "action_css_class": "button expand create",
                                    "action_link":      "search_bu_catalog_form"})
            nb_button_action += 1
        if nb_button_action == 2:
            is_two_actions = True

        selected_tags_list = folder.getSelectedTags().split(",")

        tags = self.getTags(folder, selected_tags_list)
        tags_dict = tags["tags_dict"]
        tags_list = tags["tags_list"]

        my_external_resources_list = self.getMyExternalResourcesList(folder, selected_tags_list)

        one_and_selected_tag = self.getOneAndSelectedTag(my_external_resources_list, selected_tags_list, tags_dict)

        nb_display_items = len(my_external_resources_list)
        nb_items = len(folder.objectIds())

        return {"is_two_actions":   is_two_actions,
                "item_adder_list":  item_adder_list,
                "tags_list":        tags_list,
                "is_no_items":      one_and_selected_tag["is_no_items"],
                "is_one_tag":       one_and_selected_tag["is_one_tag"],
                "one_tag":          one_and_selected_tag["one_tag"],
                "is_selected_tags": one_and_selected_tag["is_selected_tags"],
                "my_items_list":    my_external_resources_list,
                "nb_display_items": nb_display_items,
                "nb_items":         nb_items,
                "folder_path":      "/".join(folder.getPhysicalPath()),
                "folder_link":      folder.absolute_url()}

    def getMyExternalResourcesList(self, folder, selected_tags_list):
        content_filter = {"portal_type": ["JalonRessourceExterne"]}
        return self.getItemsList(folder, selected_tags_list, content_filter)
