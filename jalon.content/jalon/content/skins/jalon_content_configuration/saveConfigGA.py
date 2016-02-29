## Controller Python Script "saveConfigGA"
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
context.setPropertiesGA(form)
context.REQUEST.RESPONSE.redirect("%s/gestion_ga" % context.absolute_url())
