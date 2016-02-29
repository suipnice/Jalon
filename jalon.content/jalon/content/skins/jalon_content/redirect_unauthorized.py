## Controller Python Script "redirect_unauthorized"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.REQUEST.RESPONSE.redirect("%s/insufficient_privileges" % context.portal_url.getPortalObject().absolute_url())
