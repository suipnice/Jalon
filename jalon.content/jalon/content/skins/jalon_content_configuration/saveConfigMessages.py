## Controller Python Script "saveConfigBIE"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
redirection = "%s/gestion_messages?gestion=%s" % (context.absolute_url(), form["gestion"])
del form["form.button.save"]
del form["gestion"]
context.setPropertiesMessages(form, context.REQUEST)
context.REQUEST.RESPONSE.redirect(redirection)
