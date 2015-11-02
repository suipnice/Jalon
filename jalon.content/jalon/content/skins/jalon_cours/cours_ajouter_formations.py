##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

elements = []
if context.REQUEST.form.has_key("elements"):
    elements = context.REQUEST.form["elements"]
context.addOffreFormations(elements)
#context.tagBU("diplome")

context.REQUEST.RESPONSE.redirect(context.absolute_url())
