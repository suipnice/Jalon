## Controller Python Script "cours_detacher_apogee"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Détache le cours à apogee
##

if context.REQUEST.form.has_key("elements"): context.delAccesApogee(context.REQUEST.form["elements"])

return context.REQUEST.RESPONSE.redirect("%s/cours_acces_view?section=acces" % context.absolute_url())