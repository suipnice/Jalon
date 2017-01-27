## Controller Python Script "create_tag"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Crée un tag
##

form = context.REQUEST.form
context.addTagFolder(form["tag_id"], form["title"])
context.REQUEST.RESPONSE.redirect(context.absolute_url())
