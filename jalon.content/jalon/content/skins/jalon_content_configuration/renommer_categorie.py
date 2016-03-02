## Controller Python Script "rennomer_categorie_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Renommer une categorie
##

request = context.REQUEST
form = request.form

context.renommerCategorie(form["clef"], form["title"])
context.REQUEST.RESPONSE.redirect("%s/gestion_mes_cours?gestion=gestion_categorie" % context.absolute_url())