# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[MySpaceView]')


class MySpaceView(BrowserView):
    """Class pour le first_page
    """

    def __init__(self, context, request):
        # LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getBreadcrumbs(self):
        return [{"title": _(u"Mes ressources"),
                 "icon":  "fa fa-folder-open",
                 "link":  self.context.absolute_url()}]

    def getTags(self, folder, selected_tags_list):
        # LOG.info.info("----- getTags -----")
        #tags_dict = {"last": "Les 20 derniers"}
        tags_list = []
        tags = list(folder.Subject())
        # LOG.info.info(tags)
        tags_dict = folder.getSubjectsDict()
        # LOG.info.info(tags_dict)
        #tags.sort()
        for tag in tags:
            #tags_dict[tag] = tag
            tags_list.append({"tag_id":    tag,
                              "tag_title": tags_dict[tag],
                              "tag_css":   "filter-button selected" if tag in selected_tags_list else "filter-button unselected"})

        tags_list.sort(lambda x, y: cmp(x["tag_title"], y["tag_title"]))
        tags_list.insert(0, {"tag_id":    "last",
                             "tag_title": "Les 20 derniers",
                             "tag_css":   "filter-button fixed_filter selected" if "last" in selected_tags_list else "filter-button fixed_filter unselected"})
        tags_dict["last"] = "Les 20 derniers"
        return {"tags_dict": tags_dict,
                "tags_list": tags_list}

    def getOneAndSelectedTag(self, items_list, selected_tags_list, tags_dict):
        is_no_items = False
        if not items_list:
            if "last" in selected_tags_list:
                selected_tags_list.remove("last")
            is_no_items = True if len(selected_tags_list) == 0 else False

        one_tag = ""
        is_one_tag = False
        try:
            selected_tags_list.remove("")
        except:
            pass
        if len(selected_tags_list) == 1:
            is_one_tag = True
            one_tag = {"tag_id": selected_tags_list[-1],
                       "tag_title": tags_dict[selected_tags_list[-1]]}

        is_selected_tags = "remove_tags_objects" if selected_tags_list != ["last"] and len(selected_tags_list) >= 1 else "isnt_selected_tags"

        return {"is_no_items":      is_no_items,
                "is_one_tag":       is_one_tag,
                "one_tag":          one_tag,
                "is_selected_tags": is_selected_tags}

    def getItemsList(self, folder, selected_tags_list, content_filter):
        # LOG.info("----- getItemsList -----")
        content_filter["sort_on"] = "modified"
        content_filter["sort_order"] = "descending"
        if selected_tags_list and selected_tags_list != ["last"]:
            last = False
            subjects = []
            if "last" in selected_tags_list:
                selected_tags_list.remove("last")
                last = True
            for tag in selected_tags_list:
                subjects.append(tag)
            if len(subjects) > 1:
                content_filter['Subject'] = {'query': subjects, 'operator': 'and'}
            else:
                content_filter['Subject'] = subjects[0]
            if last:
                #content_filter["sort_on"] = "modified"
                #content_filter["sort_order"] = "descending"
                return folder.getFolderContents(contentFilter=content_filter, batch=True, b_size=20)
            else:
                return folder.getFolderContents(contentFilter=content_filter)
        elif selected_tags_list == ["last"]:
            #content_filter["sort_on"] = "modified"
            #content_filter["sort_order"] = "descending"
            return folder.getFolderContents(contentFilter=content_filter, batch=True, b_size=20)
        else:
            #content_filter["sort_on"] = "modified"
            #content_filter["sort_order"] = "descending"
            return folder.getFolderContents(contentFilter=content_filter)
