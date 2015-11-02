## Controller Python Script "saveConfigInfos"
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
context.setPropertiesInfos(form)
context.REQUEST.RESPONSE.redirect("%s/gestion_infos" % context.absolute_url())
