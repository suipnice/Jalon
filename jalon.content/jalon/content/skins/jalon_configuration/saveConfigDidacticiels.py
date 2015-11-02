## Controller Python Script "saveConfigDidacticiels"
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
context.setPropertiesDidacticiels(form)
context.REQUEST.RESPONSE.redirect("%s/gestion_didacticiels" % context.absolute_url())
