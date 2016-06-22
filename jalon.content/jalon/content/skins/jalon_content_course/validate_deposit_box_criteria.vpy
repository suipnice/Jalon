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

obligatory_fields = ["title", "description", "notation", "coefficient", "comment", "gap"]
if form["comment"] in ["1", "2"]:
    obligatory_fields.append("comment_min")
    obligatory_fields.append("comment_max")

for validate_field in obligatory_fields:
    if not validate_field in form or form[validate_field] in ["", " ", None]:
        state.setError(validate_field, _(u"Champ obligatoire"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

failed = False
try:
    notation = int(form["notation"])
    failed = True if notation < 1 or notation > 10 else False 
except:
    failed = True
if failed:
    state.setError(validate_field, _(u"Veuillez saisir un entier compris entre 1 et 10"), "%s_required" % validate_field)
    state.set(status='failure')
    error = True

failed = False
try:
    coefficient = int(form["coefficient"])
    failed = True if coefficient < 0 and coefficient > 5 else False 
except:
    failed = True
if failed:
    state.setError(validate_field, _(u"Veuillez saisir un entier compris entre 0 et 5"), "%s_required" % validate_field)
    state.set(status='failure')
    error = True

failed = False
try:
    gap = int(form["gap"])
    failed = True if gap < 0 and gap > 5 else False 
except:
    failed = True
if failed:
    state.setError(validate_field, _(u"Veuillez saisir un entier compris entre 0 et 5"), "%s_required" % validate_field)
    state.set(status='failure')
    error = True

if form["comment"] in ["1", "2"]:
    failed = False
    try:
        comment_min = int(form["comment_min"])
        failed = True if comment_min < 1 and comment_min > 300 else False 
    except:
        failed = True
    if failed:
        state.setError(validate_field, _(u"Veuillez saisir un entier compris entre 1 et 300"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

    failed = False
    try:
        comment_max = int(form["comment_max"])
        failed = True if comment_max < 500 and comment_max > 1500 else False 
    except:
        failed = True
    if failed:
        state.setError(validate_field, _(u"Veuillez saisir un entier compris entre 500 et 1500"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

    failed = False
    try:
        failed = True if comment_max < comment_min else False
    except:
        failed = True
    if failed:
        state.setError(validate_field, _(u"Veuillez saisir un entier supérieur au minimum"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if not error:
    state.set(status="success")

return state
