## Script (Python) "caslogin"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=CAS Login
##
from Products.PythonScripts.standard import url_quote

# container = container
# context = context
request = container.REQUEST

portal = context.portal_url.getPortalObject()
plugin = portal.acl_users.cas_unice

if plugin.casServerUrlPrefix:
    came_from = ""
    if request.has_key("came_from"):
        came_from = url_quote("?came_from=%s" % request["came_from"])
    url = "".join([plugin.getLoginURL(), '?service=', plugin.getService(), came_from])
    if plugin.renew:
        url += '&renew=true'
    if plugin.gateway:
        url += '&gateway=true'
    request.RESPONSE.redirect(url, lock=1)
