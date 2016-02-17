# -*- coding: utf-8 -*-
##Script (Python) "validate_create_course"
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

validate_list = ["title"]

retour = context.absolute_url()

for validate_field in validate_list:
    if not validate_field in form or form[validate_field] in ["", " ", None]:
        state.setError(validate_field, _(u"Champ obligatoire"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if not error:
    state.set(status="success")

return state
