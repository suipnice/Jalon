##Python Script "modifierInfosELP_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=modifierInfosELP_script
##

form = context.REQUEST.form
context.setInfosELP(form)
context.REQUEST.RESPONSE.redirect("%s/@@jalon-bdd?gestion=gestion_bdd" % context.absolute_url())
