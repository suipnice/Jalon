##Python Script "supprimerELP_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=supprimerELP_script
##

form = context.REQUEST.form
context.supprimerELP(form)
context.REQUEST.RESPONSE.redirect("%s/@@jalon-bdd?gestion=gestion_bdd" % context.absolute_url())