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

# context = context
# state = state
# context.plone_log("[valider_form]")

error = False
form = context.REQUEST.form
validate_key = form["validate_key"]

validate_dict = {"edit_deposit_box":  ["title"],
                 "deposit_file":      ["title", "file_file"],
                 "correction_number": ["nombreCorrection"],
                 "penality":          ["penalite"],
                 "correction_date":   ["datetime-dateCorrection"]}

for validate_field in validate_dict[validate_key]:
    if validate_field not in form or form[validate_field] in ["", " ", None]:
        state.setError(validate_field, _(u"Champ obligatoire"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if validate_key == "correction_number":
    failed = False
    try:
        nombreCorrection = int(form["nombreCorrection"])
        failed = True if nombreCorrection < 1 or nombreCorrection > 5 else False
    except:
        failed = True
    if failed:
        state.setError(validate_field, _(u"Veuillez saisir un entier compris entre 1 et 5"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if validate_key == "penality":
    failed = False
    try:
        adjustementPoints = int(form["adjustementPoints"])
        failed = True if adjustementPoints < 1 or adjustementPoints > 5 else False
    except:
        failed = True
    if failed:
        state.setError(validate_field, _(u"Veuillez saisir un entier compris entre 1 et 5"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if validate_key == "correction_date":
    if DateTime(context.getDateDepot()).strftime("%Y/%m/%d %H:%M") >= DateTime(form["datetime-dateCorrection"]).strftime("%Y/%m/%d %H:%M"):
        state.setError(validate_field, _(u"Veuillez saisir une date limite d'évaluation supérieur à la date limite de dépôts"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if not error:
    state.set(status="success_%s" % validate_key)

return state
