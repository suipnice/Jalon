# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

import urllib

from logging import getLogger
LOG = getLogger('[MySpaceView]')


class MySpaceView(BrowserView):
    """Class pour le first_page
    """

    def __init__(self, context, request):
        #LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getTags(self, folder, selected_tags_list):
        tags_dict = {"last": "Les 20 derniers"}
        tags_list = []
        tags = list(folder.Subject())
        tags.sort()
        for tag in tags:
            tags_dict[tag] = tag
            tags_list.append({"tag_id":    urllib.quote(tag),
                              "tag_title": tag,
                              "tag_css":   "filter-button selected" if tag in selected_tags_list else "filter-button unselected"})

        tags_list.insert(0, {"tag_id":    "last",
                             "tag_title": "Les 20 derniers",
                             "tag_css":   "filter-button fixed_filter selected" if "last" in selected_tags_list else "filter-button fixed_filter unselected"})
        return {"tags_dict": tags_dict,
                "tags_list": tags_list}
