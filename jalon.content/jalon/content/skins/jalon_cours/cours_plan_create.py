## Controller Python Script "cours_plan_create"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute un élément au plan intéractif
##
from DateTime import DateTime
#context.plone_log("----- cours_plan_create -----")
typeElement = context.REQUEST.form["typeElement"]

now = DateTime()
idElement = "%s-%s-%s" % (typeElement, context.REQUEST.form["createurElement"], ''.join([now.strftime('%Y%m%d'), now.strftime('%H%M%S')]))
context.ajouterInfosElement(idElement, context.REQUEST.form["typeElement"], context.REQUEST.form["titreElement"], context.REQUEST.form["createurElement"])

position = None
if context.REQUEST.form["position"] != "fin_racine":
    position = context.REQUEST.form["position"]
context.ajouterElementPlan(idElement, position)

context.setProperties({"DateDerniereModif": DateTime()})

#context.plone_log("----- cours_plan_create -----")
if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    return context.REQUEST.RESPONSE.redirect(context.absolute_url())
