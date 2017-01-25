# -*- coding: utf-8 -*-
##Script (Python) "validate_wims_activity_property"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validation du formulaire des propriétés d'activite WIMS
##

from Products.CMFPlone import PloneMessageFactory as _

# context.plone_log("[valider_form]")
# state = state
# context = context

error = False
form = context.REQUEST.form
# validate_key = form["validate_key"]

# On vérifie qu'un etudiant malveillant (ou un anonyme) ne puisse pas modifier une activité
if not context.checkRoles(function="validate_wims_activity_property"):
    state.set(status='failure')
    error = True
    return state

required_fields = ["title"]

# Les parenthèses doivent être placées par paires correctement fermées pour WIMS.
listeReplace_desc_wims = [["{", "}", u"Accolades"],
                          ["(", ")", u"Parenthèses"],
                          ["[", "]", u"Crochets"]]

desc = form["description"]
incoherence = []
typ_parenthese = []
for couple in listeReplace_desc_wims:
    nb_ouvre = desc.count(couple[0])
    nb_ferme = desc.count(couple[1])
    if nb_ouvre != nb_ferme:
        incoherence.append("%s '%s' contre %s '%s'" % (nb_ouvre, couple[0], nb_ferme, couple[1]))
        typ_parenthese.append(couple[2])
if len(incoherence) > 0:
    incoherence = " et ".join(incoherence)
    typ_parenthese = " et ".join(typ_parenthese)
    message = _(u"${typ_parenthese} mal fermées : ${incoherence}",
                        mapping={'typ_parenthese': typ_parenthese, 'incoherence': incoherence})
    state.setError("description", message, "bad_parenthesis")
    state.set(status='failure')
    error = True

# Cas de l'examen
if "duree" in form:
    required_numbers = ["note_max", "duree", "attempts"]
# Cas de l'entrainement
elif "note_max" in form:
    required_numbers = ["note_max"]

required_fields.extend(required_numbers)

for validate_field in required_fields:
    if validate_field not in form or form[validate_field] in ["", " ", None]:
        state.setError(validate_field, _(u"Champ obligatoire"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

for validate_field in required_numbers:
    if not form[validate_field].isdigit():
        state.setError(validate_field, _(u"Vous devez taper un nombre"), "%s_required" % validate_field)
        state.set(status='failure')
        error = True

if not error:
    validate_key = "edit_wims_activity"
    state.set(status="success_%s" % validate_key)

return state
