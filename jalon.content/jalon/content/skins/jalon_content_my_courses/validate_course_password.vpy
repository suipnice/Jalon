# -*- coding: utf-8 -*-
##Script (Python) "validate_course_password"
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

if not "course_password" in form or form["course_password"] in ["", " ", None]:
        state.setError("course_password", _(u"Champ obligatoire"), "course_password_required")
        state.set(status='failure')
        error = True
elif form["course_password"] != context.getLienMooc():
        state.setError("course_password", _(u"Mot de passe incorrect"), "course_password_required")
        state.set(status='failure')
        error = True

if not error:
    state.set(status="success")

return state
