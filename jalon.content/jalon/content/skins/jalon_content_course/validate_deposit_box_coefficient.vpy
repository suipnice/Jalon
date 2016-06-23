# -*- coding: utf-8 -*-
##Script (Python) "validate_deposit_box_criteria"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validation des formulaires
##

from Products.CMFPlone import PloneMessageFactory as _

#context.plone_log("[valider_form]")
error = False
form = context.REQUEST.form

if not "coefficient" in form or form["coefficient"] in ["", " ", None]:
    state.setError("coefficient", _(u"Champ obligatoire"), "coefficient_required")
    state.set(status='failure')
    error = True

failed = False
try:
    coefficient = int(form["coefficient"])
    failed = True if coefficient < 0 and coefficient > 5 else False 
except:
    failed = True
if failed:
    state.setError(validate_field, _(u"Veuillez saisir un entier compris entre 1 et 5"), "%s_required" % validate_field)
    state.set(status='failure')
    error = True

if not error:
    state.set(status="success")

return state
