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

request = container.REQUEST

portal = context.portal_url.getPortalObject()
plugin = portal.acl_users.cas_unice

if plugin.casServerUrlPrefix:

    pod_action = "/video_edit/"
    jalon_action = str(traverse_subpath[0])
    if jalon_action in ["edit", "delete"]:
        video_slug = context.getVideourl().split("/")[-2]
        pod_action = "/video_%s/%s/" % (jalon_action, video_slug)

    service = url_quote("%s/accounts/cas/login/?next=%s" % (context.getUrlServeurElasticsearch(), pod_action))

    url = "".join([plugin.getLoginURL(), '?service=', service])
    request.RESPONSE.redirect(url, lock=1)
