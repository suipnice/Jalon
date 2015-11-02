## Controller Python Script "cours_ajouterChapitrePlan"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.ajouterChapitrePlan(context.REQUEST.form["idElement"], context.REQUEST.form["idParent"])