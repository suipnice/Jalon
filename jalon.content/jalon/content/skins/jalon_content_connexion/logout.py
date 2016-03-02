## Script (Python) "caslogout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=CAS Logout
##
from Products.CMFCore.utils import getToolByName

request = container.REQUEST
portal = context.portal_url.getPortalObject()
mt = getToolByName(context, 'portal_membership')
portal_jalon_properties = getToolByName(context, 'portal_jalon_properties')

redirection = "%s?came_from=" % portal.absolute_url()
if portal_jalon_properties.getPropertiesConnexion("activer_cas"):
    membership_tool=getToolByName(context, 'portal_membership')
    member = membership_tool.getAuthenticatedMember()
    location = member.getProperty("location")
    if location != "jalon":
        cas_client_plugin = getattr(portal.acl_users, "cas_%s" % location)
        redirection = cas_client_plugin.casServerUrlPrefix + '/logout'

mt.logoutUser(REQUEST=request)

request.RESPONSE.redirect(redirection)
