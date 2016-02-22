## Script (Python) "getAuthenticatedName"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

portal = context.portal_url.getPortalObject()

member = portal.portal_membership.getAuthenticatedMember()
return member.getProperty("fullname")
