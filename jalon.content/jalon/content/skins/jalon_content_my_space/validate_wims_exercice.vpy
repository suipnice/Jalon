# -*- coding: utf-8 -*-
##Script (Python) "valider_exercicewims"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validation des modifications sur un exercice WIMS
##

from Products.CMFPlone import PloneMessageFactory as _
#context=context
#state=state
error = False
form = context.REQUEST.form
modele = form["modele"]

# La validation de l'ajout d'exercice se fait dans valider_form.vpy
# "ajout-wims":                 ["title"],

dicoObligatoire = {"qcmsimple":                  ["title", "bonnesrep"],
                   "equation":                   ["title", "enonce", "equation"],
                   "texteatrous":                ["title", "donnees"],
                   "marqueruntexte":             ["title", "data", "minmark", "maxmark"],
                   "marquerparpropriete":        ["title", "prop", "data", "tot", "mingood", "minbad"],
                   "questiontextuelletolerante": ["title", "data", "len"],
                   "taperlemotassocie":          ["title", "words", "size"],
                   "reordonner":                 ["title", "data", "size", "tot"],
                   "correspondance":             ["title", "data", "sizev", "sizel", "sizer", "tot"],
                   "classerparpropriete":        ["title", "prop", "data", "tot", "max1", "size1"],
                   "vraifauxmultiples":          ["title", "datatrue", "datafalse", "tot", "mintrue", "minfalse"],
                   "texteatrousmultiples":       ["title", "data"],
                   "exercicelibre":              ["title", "exercicelibre"],
                   "externe":                    ["title", "permalink"],
                   "qcmsuite":                   ["title"]}

for obligatoire in dicoObligatoire[modele]:
    if obligatoire not in form:
        state.setError(obligatoire, _(u"Vous n'avez pas renseigné ce champ obligatoire."))
        state.set(status='failure')
        error = True
    elif (not form[obligatoire]) or form[obligatoire] in ["", " ", None]:
        state.setError(obligatoire, _(u"Vous n'avez pas renseigné ce champ obligatoire."))
        state.set(status='failure')
        error = True

if error:
    context.plone_utils.addPortalMessage(_(u"Un champ obligatoire n'a pas été renseigné. Votre exercice n'a pas été modifié."), 'error')
    if modele == "qcmsuite":
        form["list_id_questions"] = range(int(form["nb_questions"]))
    return state

if modele == "externe":
    permalink = context.parser_permalien(form["permalink"])
    if permalink == "":
        state.setError("permalink", _(u"Permalien mal formé"))
        state.set(status='failure')
        error = True
    else:
        form["permalink"] = permalink
else:
    # Avant de modifier un exercice WIMS, on teste la compilation de celui-ci dans la "sandbox"
    rep = context.addExoWims(form["idobj"], form["title"], form["member_id"], form["modele"], form, sandbox=True)
    if not (rep and rep["status"] == "OK"):
        if modele == "qcmsuite":
            form["list_id_questions"] = rep["list_id_questions"]
        if "error_code" in rep and rep["error_code"] == "503":
            # state.setError("wims_unavailable", _(rep["message"]))
            context.plone_utils.addPortalMessage(_(u"Le serveur WIMS est actuellement injoignable. Merci de réessayer ultérieurement svp..."), type="error")
        else:
            state.setError("syntax_error", _(u"Erreur de syntaxe"))
        state.set(status='failure')
        error = True

if not error:
    state.set(status="success")
else:
    context.plone_utils.addPortalMessage(_(u"Votre exercice n'a pas été modifié."), 'error')

return state
