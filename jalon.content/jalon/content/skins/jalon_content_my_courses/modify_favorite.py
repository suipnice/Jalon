## Controller Python Script "modify_favorite"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

user_id = context.REQUEST.form["user_id"]
context.modifyFavorite(user_id)

context.REQUEST.RESPONSE.redirect("%s/cours/%s?onglet=1" % (context.portal_url.getPortalObject().absolute_url(), user_id))
