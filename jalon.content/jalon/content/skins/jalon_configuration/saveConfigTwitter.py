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
del form["form.submitted"]
context.setPropertiesTwitter(form)
context.REQUEST.RESPONSE.redirect("%s/@@jalon-configuration?gestion=gestion_twitter" % context.absolute_url())
