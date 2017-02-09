# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from my_space_view import MySpaceView

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[MyPodVideosView]')


class MyPodVideosView(MySpaceView):
    """ Class View du fichier my_pod_videos_view.pt
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
                {"title": _(u"Mes contenus UNSPod"),
                 "icon":  "fa fa-youtube-play",
                 "link":  self.context.absolute_url()}]

    def getMyPodVideosView(self, user):
        # LOG.info("----- getMyPodVideosView -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        member_id = user.getId()
        folder = getattr(portal.Members, member_id).Video

        selected_tags_list = folder.getSelectedTags().split(",")

        tags = self.getTags(folder, selected_tags_list)
        tags_dict = tags["tags_dict"]
        tags_list = tags["tags_list"]

        my_pod_videos_list = self.getMyPodVideosList(folder, selected_tags_list, member_id, portal)

        one_and_selected_tag = self.getOneAndSelectedTag(my_pod_videos_list, selected_tags_list, tags_dict)

        nb_display_items = len(my_pod_videos_list)
        nb_items = len(folder.objectIds())

        return {"tags_list":        tags_list,
                "is_no_items":      one_and_selected_tag["is_no_items"],
                "is_one_tag":       one_and_selected_tag["is_one_tag"],
                "one_tag":          one_and_selected_tag["one_tag"],
                "is_selected_tags": one_and_selected_tag["is_selected_tags"],
                "my_items_list":    my_pod_videos_list,
                "nb_display_items": nb_display_items,
                "nb_items":         nb_items,
                "folder_path":      "/".join(folder.getPhysicalPath()),
                "folder_link":      folder.absolute_url()}

    def getMyPodVideosList(self, folder, selected_tags_list, member_id, portal):
        if selected_tags_list == ["last"]:
            self.updateJalonVideos(folder, portal, member_id)
        content_filter = {"portal_type": ["JalonRessourceExterne"]}
        return self.getItemsList(folder, selected_tags_list, content_filter)

    def updateJalonVideos(self, folder, portal, member_id):
        # LOG.info("----- updateJalonVideos -----")
        my_videos_ids = []
        for video in folder.objectIds():
            if member_id in video:
                my_videos_ids.append(video)
        jalon_videos_id = set([int(object_id.split("-")[-1]) for object_id in my_videos_ids])

        portal_elasticsearch = getattr(portal, "portal_jalon_elasticsearch", None)
        response_elasticsearch = portal_elasticsearch.searchElasticsearch("mes_videos", "", 1)

        nb_pages = response_elasticsearch["nb_pages"]
        if not nb_pages:
            videos_del = jalon_videos_id
        else:
            dico_videos_pod = {}
            videos_ids = []
            for video in response_elasticsearch["liste_videos"]:
                videos_ids.append(video["id"])
                dico_videos_pod[video["id"]] = video

            if nb_pages > 1:
                for page in range(2, nb_pages):
                    response_elasticsearch = portal_elasticsearch.searchElasticsearch("mes_videos", "", page)
                    for video in response_elasticsearch["liste_videos"]:
                        videos_ids.append(video["id"])
                        dico_videos_pod[video["id"]] = video

            videos_ids = set(videos_ids)
            videos_del = jalon_videos_id.difference(videos_ids)

            # LOG.info("jalon_videos_id : %s" % jalon_videos_id)
            # LOG.info("videos_ids : %s" % videos_ids)
            # LOG.info("videos_del : %s" % videos_del)

            videos_add = videos_ids.difference(jalon_videos_id)
            # LOG.info(videos_add)
            # LOG.info(dico_videos_pod)
            for video_id in videos_add:
                video = dico_videos_pod[video_id]
                object_id = "Externe-%s-%s" % (member_id, video_id)
                object_video = getattr(folder, object_id, None)
                if not object_video:
                    folder.invokeFactory(type_name='JalonRessourceExterne', id=object_id)
                    object_video = getattr(folder, object_id)
                    video = portal_elasticsearch.searchElasticsearch(type_search="video", term_search=video_id)
                    param = {"Title":                video["title"],
                             "TypeRessourceExterne": "Video",
                             "Videourl":             video["full_url"],
                             "Description":          video["text"],
                             "Lecteur":              video["iframe"],
                             "Videoauteur":          video["owner"],
                             "Videoauteurname":      video["owner_full_name"],
                             "Videothumbnail":       video["thumbnail"]}
                    object_video.setProperties(param)

        for video_id in videos_del:
            # LOG.info("Del Video : %s" % video_id)
            object_id = "Externe-%s-%s" % (member_id, video_id)
            video_object = getattr(folder, object_id)
            relatedItems = ["/".join(related_item.getPhysicalPath()) for related_item in video_object.getRelatedItems()]
            # LOG.info("relatedItems : %s" % str(relatedItems))
            brains = folder.portal_catalog(path={"query": relatedItems, "depth": 0})
            for brain in brains:
                brain_object = brain.getObject()
                # LOG.info("brain_object : %s" % brain_object.getId())
                # LOG.info("brain_object : %s" % brain_object.portal_type)
                if brain_object.portal_type == "JalonCours":
                    brain_object.deleteCourseMapItem(object_id, None)
                else:
                    brain_object.retirerElement(object_id, "sujets")
            folder.manage_delObjects(object_id)
