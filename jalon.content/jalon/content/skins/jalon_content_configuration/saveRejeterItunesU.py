## Controller Python Script "saveRejeterItunesU"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
redirection = "%s/gestion_mes_cours?gestion=%s&useriTunesU=%s" % (context.absolute_url(), form["gestion"], form["auteurCours"])
context.rejeterCoursiTunesU(form["idCours"], form["auteurCours"])
context.REQUEST.RESPONSE.redirect(redirection)
