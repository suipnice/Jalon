## Controller Python Script "edit_file_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
form = REQUEST.form

context.setTitle(form["title"])
context.setDescription(form["description"])

if "image_file" in form:
    context.setImage(form["image_file"])
if "file_file" in form:
    context.setFile(form["file_file"])

context.reindexObject()

context.aq_parent.majFichier(context)

context.REQUEST.RESPONSE.redirect("%s/mes_ressources/mes_fichiers" % context.portal_url.getPortalObject().absolute_url())
