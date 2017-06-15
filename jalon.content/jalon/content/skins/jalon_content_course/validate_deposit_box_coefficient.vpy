# -*- coding: utf-8 -*-
##Script (Python) "validate_deposit_box_coefficient"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validation du formulaire de changement de coefficient
##

from Products.CMFPlone import PloneMessageFactory as _

# context.plone_log("[valider_form]")
# state = state
error = False
form = context.REQUEST.form

if "coefficient" not in form or form["coefficient"] in ["", " ", None]:
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
    state.setError(coefficient, _(u"Veuillez saisir un entier compris entre %s et %s" % (1, 5)), "%s_required" % coefficient)
    state.set(status='failure')
    error = True

if not error:
    state.set(status="success")

return state
