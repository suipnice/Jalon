## Script (Python) "cours_supprimer_annonce"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
if request["annonce"] != "actu": context.supprimerAnnonce(request["annonce"])
else: context.setProperties({"Actualites" : ()})

redirection = context.absolute_url()
#if request.form.has_key("redirection"): redirection = "%s/cours_lister?lister=%s" % (redirection, request.form["redirection"])
if request.form.has_key("redirection"): redirection = "%s/cours_lister_annonces" % (redirection)

request.RESPONSE.redirect(redirection)