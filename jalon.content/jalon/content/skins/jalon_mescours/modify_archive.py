## Controller Python Script "modify_archive"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

user_id = context.REQUEST.form["user_id"]
context.modifyArchive(user_id)

context.REQUEST.RESPONSE.redirect("%s/cours/%s?onglet=2" % (context.portal_url.getPortalObject().absolute_url(), user_id))
