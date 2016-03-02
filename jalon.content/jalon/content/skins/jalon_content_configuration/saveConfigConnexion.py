## Controller Python Script "saveConfigTwitter"
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
context.setPropertiesConnexion(form)
context.REQUEST.RESPONSE.redirect("%s/gestion_connexion" % context.absolute_url())
