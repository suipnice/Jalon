## Controller Python Script "modifierProprietes_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
context.setProprietesElement(request.form)

request.RESPONSE.redirect(context.absolute_url())
