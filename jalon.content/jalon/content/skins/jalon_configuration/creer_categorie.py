##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

#return context.REQUEST
context.creerCategorie(context.REQUEST.form["title"])
context.REQUEST.RESPONSE.redirect("%s/gestion_mes_cours?gestion=gestion_categorie" % context.absolute_url())