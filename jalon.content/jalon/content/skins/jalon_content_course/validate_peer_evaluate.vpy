# -*- coding: utf-8 -*-
##Script (Python) "validate_deposit_box_property"
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

error = False
form = context.REQUEST.form

index = 1
error_index = []
criteria_order = form["criteria_order"].split(",")
for tmp in criteria_order:
    criteria_comment = "criteria%i-comment" % index
    criteria_note = "criteria%i-note" % index
    criteria_note_max = "criteria%i-note_max" % index
    if not form[criteria_comment]:
        state.setError(criteria_comment, _(u"Champ obligatoire"), "%s_required" % criteria_comment)
        error = True
        error_index.append(str(index))
    if int(form[criteria_note]) < 0  or int(form[criteria_note]) > int(form[criteria_note_max]):
        state.setError(criteria_note, _(u"Note invalide"), "%s_required" % criteria_note)
        error = True
        if not index in error_index: error_index.append(str(index))
    index = index + 1

if not error:
    state.set(status="success")
else:
    state.setError("error_index", _(u"Veuillez corriger les critères d'évaluations : %s" % ",".join(error_index)), "")
    state.set(status='failure')

return state
