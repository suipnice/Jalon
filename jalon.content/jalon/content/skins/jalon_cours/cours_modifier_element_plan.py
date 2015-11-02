## Controller Python Script "cours_modifier_element_plan"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
context.modifierInfosElementPlan(request["idElement"], request["description"])
context.REQUEST.RESPONSE.redirect(context.absolute_url())