## Controller Python Script "setFavori"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

authMember = context.portal_membership.getAuthenticatedMember().getId()
context.setFavoris(authMember)

context.REQUEST.RESPONSE.redirect("%s/cours/%s/" % (context.portal_url.getPortalObject().absolute_url(), authMember))