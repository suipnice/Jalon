##Python Script "saveVariablesPodcast"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
podcasts = {"activerPodcasts": True,
            "uploadPodcasts": REQUEST.form["uploadPodcasts"],
            "dnsPodcasts":    REQUEST.form["dnsPodcasts"]}
if not "activerPodcasts" in REQUEST.form:
    podcasts["activerPodcasts"] = False

context.setVariablesPodcast(podcasts)

REQUEST.RESPONSE.redirect("%s/@@jalon-podcast?message=1" % context.absolute_url())