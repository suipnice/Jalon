## Controller Python Script "cours_retirerElementPlan"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST

try:
    if request.form["repertoire"] and request.form["repertoire"] == "CatalogueBU":
        context.tagBU("remove", request.form["idElement"])
except:
    pass

context.retirerElementPlan(context.REQUEST["idElement"], None)
context.delActu(context.REQUEST["idElement"])
context.REQUEST.RESPONSE.redirect(context.absolute_url())
