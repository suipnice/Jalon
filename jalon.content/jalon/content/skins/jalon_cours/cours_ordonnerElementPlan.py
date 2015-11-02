## Controller Python Script "cours_ordonnerElementPlan"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

if "attente" in context.REQUEST.form["classe"]:
    context.retirerElementAttente(context.REQUEST.form["idAttente"])
context.ordonnerElementPlan(context.REQUEST.form["plan"])