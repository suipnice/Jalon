## Controller Python Script "saveConfigAdobeConnect"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cours edit
##

form = context.REQUEST.form
redirection = "%s/gestion_mes_ressources?gestion=%s" % (context.absolute_url(), form["gestion"])
del form["form.button.save"]
del form["gestion"]
context.setPropertiesAdobeConnect(form)
context.REQUEST.RESPONSE.redirect(redirection)
