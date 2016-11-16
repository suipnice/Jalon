# -*- coding: utf-8 -*-
##Script (Python) "valider_forum"
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
formulaire = str(form["formulaire"])

dicoObligatoire = {"ajout-forum":           ["title", "description"],
                   "modifier-forum":        ["title", "description"],
                   "ajout-conversation":    ["title", "text"],
                   "modifier-conversation": ["title", "text"],
                   "ajout-reponse":         ["text"]}

retour = context.absolute_url()
numeriques_Obligatoires = []

for obligatoire in dicoObligatoire[formulaire]:
    if not obligatoire in form:
        state.setError(obligatoire, _(u"Champ obligatoire"), "%s_required" % obligatoire)
        state.set(status='failure')
        error = True
    elif (not form[obligatoire]) or form[obligatoire] in ["", " ", None]:
        state.setError(obligatoire, _(u"Champ obligatoire"), "%s_required" % obligatoire)
        state.set(status='failure')
        error = True

if not error:
    state.set(status="success-%s" % formulaire)

return state
