## Script (Python) "cours_plan_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validate plan
##

from Products.CMFPlone import PloneMessageFactory as _

#context.plone_log("----- cours_plan_validate -----")
if context.REQUEST["typeElement"] == "": 
   state.setError("typeElement", _(u"Vous devez choisir un type d'élément"), 'typeElement_required')
   state.set(status='failure')

if not context.REQUEST.has_key("titreElement"):
   state.setError("titreElement", _(u"Champ Obligatoire"), 'titreElement_required')
   state.set(status='failure')
elif context.REQUEST["titreElement"].strip() == "":
   state.setError("titreElement", _(u"Champ Obligatoire"), 'titreElement_required')
   state.set(status='failure')

#context.plone_log("----- cours_plan_validate -----")
return state
