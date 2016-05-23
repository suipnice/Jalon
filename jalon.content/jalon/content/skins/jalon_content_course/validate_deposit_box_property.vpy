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

#context.plone_log("[valider_form]")
error = False
form = context.REQUEST.form
validate_key = form["validate_key"]

validate_dict = {"edit_deposit_box": ["title"],
                 "deposit_file":     ["title", "file_file"],
                 "add_criteria":     ["title", "description", "notation", "coefficient"]}

for validate_field in validate_dict[validate_key]:
    if not validate_field in form or form[validate_field] in ["", " ", None]:
        state.setError(validate_field, _(u"Champ obligatoire"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if validate_key == "add_criteria":
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
        failed = True if coefficient < 1 and coefficient > 5 else False 
    except:
        failed = True
    if failed:
        state.setError(validate_field, _(u"Veuillez saisir un entier compris entre 1 et 5"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if not error:
    state.set(status="success_%s" % validate_key)

return state
