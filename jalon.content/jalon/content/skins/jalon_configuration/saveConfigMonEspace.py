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
redirection = "%s/gestion_mon_espace?gestion=%s" % (context.absolute_url(), form["gestion"])
del form["form.button.save"]
del form["gestion"]
context.setPropertiesMonEspace(form)
context.REQUEST.RESPONSE.redirect(redirection)
