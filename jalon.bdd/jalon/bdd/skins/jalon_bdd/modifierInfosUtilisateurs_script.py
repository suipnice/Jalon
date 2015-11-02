##Python Script "modifierInfosUtilisateurs_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=modifierInfosUtilisateurs_script
##

form = context.REQUEST.form
context.setInfosUtilisateurs(form)
context.REQUEST.RESPONSE.redirect("%s/%s?gestion=gestion_utilisateurs" % (context.absolute_url(), form["redirection"]))
