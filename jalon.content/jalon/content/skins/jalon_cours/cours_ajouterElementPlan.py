## Controller Python Script "cours_ajouterElementPlan"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.ajouterElementPlan(context.REQUEST["idElement"])
context.REQUEST.RESPONSE.redirect(context.absolute_url())