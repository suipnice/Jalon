## Controller Python Script "add_pod_video_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
if "video_id" in REQUEST:
    user_id = REQUEST["member_id"]
    video_id_list = [REQUEST["video_id"]]
else:
    form = context.REQUEST.form
    user_id = form["member_id"]
    video_id_list = form["video_ids"]

pod_videos_folder = context.getMySubSpaceFolder(user_id, "Video")
for video_id in video_id_list:
    video_properties = context.searchElasticsearch(type_search="video", term_search=video_id)
    object_id = "Externe-%s-%s" % (video_properties["owner"], video_id)
    object_video = getattr(pod_videos_folder, object_id, None)
    if not object_video:
        pod_videos_folder.invokeFactory(type_name='JalonRessourceExterne', id=object_id)
        object_video = getattr(pod_videos_folder, object_id)
        param = {"Title":                video_properties["title"],
                 "TypeRessourceExterne": "Video",
                 "Videourl":             video_properties["full_url"],
                 "Description":          video_properties["text"],
                 "Lecteur":              video_properties["iframe"],
                 "Videoauteur":          video_properties["owner"],
                 "Videoauteurname":      video_properties["owner_full_name"],
                 "Videothumbnail":       video_properties["thumbnail"]}
        object_video.setProperties(param)

context.REQUEST.RESPONSE.redirect(context.absolute_url())
