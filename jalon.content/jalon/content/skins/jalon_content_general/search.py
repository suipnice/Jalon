## Controller Python Script "search"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.REQUEST.RESPONSE.redirect("%s/search_form" % context.portal_url.getPortalObject().absolute_url())