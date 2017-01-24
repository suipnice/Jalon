# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from my_space_view import MySpaceView

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[MyGlossaryTermsView]')


class MyGlossaryTermsView(MySpaceView):
    """ Class View du fichier my_glossary_terms_view.pt
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
                {"title": _(u"Mes termes de glossaire"),
                 "icon":  "fa fa-font",
                 "link":  self.context.absolute_url()}]

    def getMyGlossaryTermsView(self, user):
        # LOG.info("----- getMyGlossaryTermsView -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        folder = getattr(portal.Members, user.getId()).Glossaire

        selected_tags_list = folder.getSelectedTags().split(",")

        tags = self.getTags(folder, selected_tags_list)
        tags_dict = tags["tags_dict"]
        tags_list = tags["tags_list"]

        my_glossary_terms_list = self.getMyGlossaryTermsList(folder, selected_tags_list)

        one_and_selected_tag = self.getOneAndSelectedTag(my_glossary_terms_list, selected_tags_list, tags_dict)

        nb_display_items = len(my_glossary_terms_list)
        nb_items = len(folder.objectIds())

        return {"tags_list":        tags_list,
                "is_no_items":      one_and_selected_tag["is_no_items"],
                "is_one_tag":       one_and_selected_tag["is_one_tag"],
                "one_tag":          one_and_selected_tag["one_tag"],
                "is_selected_tags": one_and_selected_tag["is_selected_tags"],
                "my_items_list":    my_glossary_terms_list,
                "nb_display_items": nb_display_items,
                "nb_items":         nb_items,
                "folder_path":      "/".join(folder.getPhysicalPath()),
                "folder_link":      folder.absolute_url()}

    def getMyGlossaryTermsList(self, folder, selected_tags_list):
        content_filter = {"portal_type": ["JalonTermeGlossaire"]}
        return self.getItemsList(folder, selected_tags_list, content_filter)
