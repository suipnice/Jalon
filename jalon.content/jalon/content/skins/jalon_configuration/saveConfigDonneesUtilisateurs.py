## Controller Python Script "saveConfigDonneesUtilisateurs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cours edit
##

form = context.REQUEST.form
del form["form.button.save"]
context.setPropertiesDonneesUtilisateurs(form)
context.REQUEST.RESPONSE.redirect("%s/gestion_donnees_utilisateurs" % context.absolute_url())
