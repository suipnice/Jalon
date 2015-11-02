## Controller Python Script "activer_depot_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
context.activerDepot(request.form["idDepot"], request.form["actif"])

context.REQUEST.RESPONSE.redirect("%s/cours_boite_view" % context.absolute_url())
