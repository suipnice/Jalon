# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from my_space_view import MySpaceView

from jalon.content import contentMessageFactory as _

import urllib

from logging import getLogger
LOG = getLogger('[MyPodVideosView]')


class MyPodVideosView(MySpaceView):
    """ Class View du fichier my_pod_videos_view.pt
    """

    def __init__(self, context, request):
        #LOG.info("----- Init -----")
        MySpaceView.__init__(self, context, request)
        self.context = context
        self.request = request

    def getBreadcrumbs(self):
        return [{"title": _(u"Mon espace"),
                 "icon":  "fa fa-home",
                 "link":  self.context.aq_parent.absolute_url()},
                {"title": _(u"Mes vidéos POD"),
                 "icon":  "fa fa-youtube-play",
                 "link":  self.context.absolute_url()}]

    def getMyPodVideosView(self, user):
        LOG.info("----- getMyPodVideosView -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        folder = getattr(portal.Members, user.getId()).Video

        selected_tags_list = folder.getSelectedTags().split(",")

        tags = self.getTags(folder, selected_tags_list)
        tags_dict = tags["tags_dict"]
        tags_list = tags["tags_list"]

        return {"tags_list":        tags_list}
