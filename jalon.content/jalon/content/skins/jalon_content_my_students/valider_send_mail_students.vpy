# -*- coding: utf-8 -*-
##Script (Python) "valider_send_mail_students"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validation
##

from Products.CMFPlone import PloneMessageFactory as _

error = False
form = context.REQUEST.form

obligatory_fields = ["objet", "message"]

for validate_field in obligatory_fields:
    if not validate_field in form or form[validate_field] in ["", " ", None]:
        state.setError(validate_field, _(u"Champ obligatoire"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if not error:
    state.set(status="success")

return state
