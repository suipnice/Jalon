## Controller Python Script "cours_supprimer_element_plan"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST

if request.form["repertoire"] == "CatalogueBU":
	context.tagBU("remove", request.form["idElement"])

context.supprimerElementPlan(context.REQUEST["idElement"])
context.REQUEST.RESPONSE.redirect(context.absolute_url())