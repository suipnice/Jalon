# -*- coding: utf-8 -*-
# Script (Python) "validate_my_space"
# bind container=container
# bind context=context
# bind namespace=
# bind script=script
# bind state=state
# bind subpath=traverse_subpath
# parameters=
# title=Validation des formulaires
##

from Products.CMFPlone import PloneMessageFactory as _

# context.plone_log("[valider_form]")
error = False
form = context.REQUEST.form

if "is_bu" in form:
    state.set(status="success_edit_external_resource")
    return state

validate_key = form["validate_key"]

validate_dict = {"create_tag":               ["title"],
                 "edit_tag":                 ["title"],
                 "create_wims_exercice":     ["title"],
                 "create_external_resource": ["title", "urlbiblio"],
                 "create_glossary_term":     ["title", "description"],
                 "edit_file":                ["title"],
                 "edit_external_resource":   ["title", "urlbiblio"],
                 "edit_glossary_term":       ["title", "description"]}

if validate_key == "edit_external_resource":
    if "lecteur" in form:
        validate_dict[validate_key][1] = "lecteur"

for validate_field in validate_dict[validate_key]:
    if not validate_field in form or form[validate_field] in ["", " ", None]:
        state.setError(validate_field, _(u"Champ obligatoire"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if not error:
    state.set(status="success_%s" % validate_key)

return state
