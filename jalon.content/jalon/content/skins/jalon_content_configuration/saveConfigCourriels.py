## Controller Python Script "saveConfigCourriels"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
del form["form.button.save"]
context.setPropertiesCourriels(form)
context.REQUEST.RESPONSE.redirect("%s/gestion_email" % context.absolute_url())
