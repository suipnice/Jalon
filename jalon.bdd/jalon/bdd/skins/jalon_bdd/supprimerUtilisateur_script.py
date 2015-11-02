##Python Script "suppressUtilisateur"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=suppresstUtilisateur
##

form = context.REQUEST.form
context.supprUtilisateur(form)
context.REQUEST.RESPONSE.redirect("%s/@@jalon-bdd?gestion=gestion_utilisateurs" % context.absolute_url())
