# -*- coding: utf-8 -*-
##Script (Python) "validate_course_property"
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

validate_dict = {"edit_course_title":        ["title"],
                 "create_activity":          ["title"],
                 "create_course_map_item":   ["title"],
                 "edit_course_map_item":     ["title"],
                 "add_course_announce":      ["title", "description"],
                 "edit_course_announce":     ["title", "description"],
                 "add_course_forum":         ["title", "description"],
                 "create_file":              ["file_file"],
                 "create_external_resource": ["title", "lien"],
                 "create_glossary_term":     ["title", "description"]}

for validate_field in validate_dict[validate_key]:
    if not validate_field in form or form[validate_field] in ["", " ", None]:
        state.setError(validate_field, _(u"Champ obligatoire"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if not error:
    state.set(status="success_%s" % validate_key)

return state
