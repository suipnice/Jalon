# -*- coding: utf-8 -*-
##Script (Python) "validate_deposit_box_skill"
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

obligatory_fields = ["title", "evaluation"]

if "competences" in form:
    state.set(status="success")
    return state

for validate_field in obligatory_fields:
    if not validate_field in form or form[validate_field] in ["", " ", None]:
        state.setError(validate_field, _(u"Champ obligatoire"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if "evaluation" in form and form["evaluation"] == "note":
    obligatoires = ["note_max", "note_partielle", "note_acquise"]
    for obligatoire in obligatoires:
        if form[obligatoire] == "":
            state.setError(obligatoire, _(u"Champ obligatoire"), "%s_required" % obligatoire)
            state.set(status='failure')
            error = True
    if not error:
        if int(form["note_max"]) < int(form["note_partielle"]):
            state.setError("note_partielle", _(u"La note partielle doit être inférieure ou égale à la note maximale"), "%s_required" % obligatoire)
            state.set(status='failure')
            error = True
        if int(form["note_max"]) < int(form["note_acquise"]):
            state.setError("note_acquise", _(u"La note d'acquisition doit être inférieure ou égale à la note maximale"), "%s_required" % obligatoire)
            state.set(status='failure')
            error = True
        if int(form["note_acquise"]) < int(form["note_partielle"]):
            state.setError("note_acquise", _(u"La note d'acquisition doit être supérieure ou égale à la note \"en cours d'acquisition à partir de\""), "%s_required" % obligatoire)
            state.set(status='failure')
            error = True

if not error:
    state.set(status="success")

return state
