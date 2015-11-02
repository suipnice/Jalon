## Controller Python Script "desepingler_element_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cours edit
##

form = context.REQUEST.form
context.setProperties({"AvancementPlan": []})
context.REQUEST.RESPONSE.redirect(context.absolute_url())