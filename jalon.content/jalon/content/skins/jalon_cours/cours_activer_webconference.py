## Controller Python Script "cours_activer_webconference"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.activerWebconference(context.REQUEST.form["idwebconference"])
return context.REQUEST.RESPONSE.redirect("%s/cours_webconferences_view?section=live" % context.absolute_url())