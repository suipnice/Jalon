##Python Script "bloquerUtilisateur"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=bloquerUtilisateur
##

form = context.REQUEST.form
context.bloquerIndividu({"SESAME_ETU" : form["SESAME_ETU"]})
context.REQUEST.RESPONSE.redirect("%s/%s?gestion=gestion_utilisateurs" % (context.absolute_url(), form["redirection"]))
