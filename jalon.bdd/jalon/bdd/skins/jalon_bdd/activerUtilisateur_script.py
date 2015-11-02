##Python Script "activerUtilisateur_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=activerUtilisateur_script
##

form = context.REQUEST.form
context.activerIndividu({"SESAME_ETU" : form["SESAME_ETU"]})
context.REQUEST.RESPONSE.redirect("%s/%s?gestion=gestion_utilisateurs" % (context.absolute_url(), form["redirection"]))
