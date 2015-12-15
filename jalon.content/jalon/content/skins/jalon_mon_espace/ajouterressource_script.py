## Controller Python Script "ajouterressource_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

param = {}
REQUEST = context.REQUEST
redirection = context.absolute_url()
#dans le cas ou ça n'est pas une ressource Bu
if not REQUEST.form.has_key("recordsid"):
    #si la ressource n'existe pas on la creer
    if not REQUEST.form.has_key("idobj"):
        if REQUEST["formulaire"] == "ajout-web":
            idobj = context.invokeFactory(type_name='JalonRessourceExterne', id="Externe-%s-%s" % (REQUEST["authMember"], DateTime().strftime("%Y%m%d%H%M%S")))
            obj = getattr(context, idobj)
            param = {"Title":                REQUEST["title"],
                     "TypeRessourceExterne": "Lien web",
                     "Description":           REQUEST["description"],
                     "Urlbiblio":             REQUEST["urlbiblio"]}
            obj.setProperties(param)
        if REQUEST["formulaire"] == "ajout-video":
            idobj = context.invokeFactory(type_name='JalonRessourceExterne', id="Externe-%s-%s" % (REQUEST["authMember"], DateTime().strftime("%Y%m%d%H%M%S")))
            obj = getattr(context, idobj)
            param = {"Title":                REQUEST["title"],
                     "TypeRessourceExterne": "Lecteur exportable",
                     "Description":          REQUEST["description"],
                     "Lecteur":              REQUEST["lecteur"]}
            obj.setProperties(param)
        if REQUEST["formulaire"] == "ajout-elasticsearch":
            if "video_id" in REQUEST:
                videos = [REQUEST["video_id"]]
            else:
                videos = REQUEST["video_ids"]
            for video_id in videos:
                idobj = "Externe-%s-%s" % (REQUEST["authMember"], video_id)
                obj = getattr(context, idobj, None)
                if not obj:
                    context.invokeFactory(type_name='JalonRessourceExterne', id=idobj)
                    obj = getattr(context, idobj)
                    video = context.searchElasticsearch(type_search="video", term_search=video_id)
                    param = {"Title":                video["title"],
                             "TypeRessourceExterne": "Video",
                             "Videourl":             video["full_url"],
                             "Description":          video["text"],
                             "Lecteur":              video["iframe"],
                             "Videoauteur":          video["owner"],
                             "Videoauteurname":      video["owner_full_name"],
                             "Videothumbnail":       video["thumbnail"]}
                    obj.setProperties(param)
    #sinon on la modifie juste
    else:
        obj = context
        dicoAttribut = obj.getAttributsTypeMod()
        for attribut in REQUEST.form.keys():
            if dicoAttribut.has_key(attribut): param[dicoAttribut[attribut]] = REQUEST.form[attribut]
        redirection = "%s/" % context.aq_parent.absolute_url()
        obj.setProperties(param)
else:
    for recordid in REQUEST.form["recordsid"]:
        idobj = "Externe-%s-%s" % (REQUEST["authMember"], recordid)
        obj = getattr(context, idobj, None)
        if not obj:
            context.invokeFactory(type_name='JalonRessourceExterne', id=idobj)
            obj = getattr(context, idobj)
            obj.majCatalogueBU(recordid)

context.REQUEST.RESPONSE.redirect(redirection)