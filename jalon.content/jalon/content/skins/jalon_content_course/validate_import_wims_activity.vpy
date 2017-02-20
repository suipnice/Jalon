# -*- coding: utf-8 -*-
##Script (Python) "validate_import_wims_activity"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validation du formulaire d'import d'une d'activite WIMS (Hotpotatoes)
##

from Products.CMFPlone import PloneMessageFactory as _

# context.plone_log("[valider_form]")
state = state
context = context

error = False
form = context.REQUEST.form
# validate_key = form["validate_key"]

"""
# On vérifie qu'un etudiant malveillant (ou un anonyme) ne puisse pas modifier une activité
if not context.checkRoles(function="validate_wims_activity_property"):
    state.set(status='failure')
    error = True
    return state
"""
required_fields = ["file"]

for validate_field in required_fields:
    if validate_field not in form or form[validate_field] in ["", " ", None]:
        state.setError(validate_field, _(u"Champ obligatoire"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if not error:
    validate_key = "import_exercices"
    state.set(status="success_%s" % validate_key)

return state
