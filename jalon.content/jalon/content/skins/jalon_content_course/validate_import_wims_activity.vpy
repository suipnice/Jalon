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

# state = state
# context = context

error = True
form = context.REQUEST.form
# validate_key = form["validate_key"]


# On vérifie qu'un etudiant malveillant (ou un anonyme) ne puisse pas modifier une activité
if not context.checkRoles(function="validate_import_wims_activity"):
    state.set(status='failure')
    return state

file_object = form["file"]
file_name = getattr(file_object, 'filename', '')
file_name = file_name.split("\\")[-1]

if file_name in ["", " ", None]:
    state.setError("file", _(u"Champ obligatoire") , "file_required")
    state.set(status='failure')
elif not (context.isFileOfTypes(file_object, file_name, ["text/xml", "application/xml", "application/octet-stream"])):
    state.setError("file", _(u"Mauvais type de fichier") , "file_type")
    state.set(status='failure')
else:
    state.set(status="success_import_exercices")
    error = False

return state
