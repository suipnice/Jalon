## Controller Python Script "cours_attacher_apogee"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Attache le cours à apogee
##

elements = []
if context.REQUEST.form.has_key("elements"):  elements = context.REQUEST.form["elements"]
context.setAccesApogee(elements)
context.tagBU("diplome")

return context.REQUEST.RESPONSE.redirect("%s/cours_acces_view?onglet=gestion-acces-etu" % context.absolute_url())