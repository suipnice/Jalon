## Controller Python Script "directUrl"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

return context.REQUEST.RESPONSE.redirect(context.getRemoteUrl())