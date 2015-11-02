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

error = False
form = context.REQUEST.form
modele = form["modele"]

# La validation de l'ajout d'exercice se fait dans valider_form.vpy 
# "ajout-wims":                 ["title"],

dicoObligatoire = {
    "qcmsimple":                  ["title", "bonnesrep"],
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
    "qcmsuite":                   ["title"]
}

#retour = context.absolute_url()
for obligatoire in dicoObligatoire[modele]:
    if not form.has_key(obligatoire):
        state.setError(obligatoire, _(u"Vous n'avez pas renseigné ce champ obligatoire."))
        state.set(status='failure')
        error = True
    elif (not form[obligatoire]) or form[obligatoire] in ["", " ", None]:
        state.setError(obligatoire, _(u"Vous n'avez pas renseigné ce champ obligatoire."))
        state.set(status='failure')
        error = True

if error:
    context.plone_utils.addPortalMessage(_(u"Un champ obligatoire n'a pas été renseigné. Votre exercice n'a pas été modifié."),'error')
    if modele == "qcmsuite":
        form["list_id_questions"]=range(int(form["nb_questions"]))
    return state

#Avant de modifier un exercice WIMS, on teste la compilation de celui-ci dans la "sandbox"
if modele != "externe":
    #obj = getattr(context.aq_parent, idobj)
    #le dernier parametre "True" permet de tester l'exo en mode "bac à sable"
    rep = context.addExoWims(form["idobj"], form["title"], form["authMember"], form["modele"], form, True)

    if not (rep and rep["status"] == "OK"):
        if modele == "qcmsuite":
            form["list_id_questions"] = rep["list_id_questions"]
        state.setError("syntax_error", _(u"Erreur de syntaxe"))
        state.set(status='failure')
        error = True
        #context.plone_utils.addPortalMessage(_(u"Il y a une erreur de syntaxe dans votre exercice."),'error')

else:
    permalink = context.parser_permalien(form["permalink"])
    if permalink == "":
        state.setError("permalink", _(u"Permalien mal formé"))
        state.set(status='failure')
        error = True
    else:
        form["permalink"] = permalink

if not error:
    state.set(status="success")
else:
    context.plone_utils.addPortalMessage(_(u"Une erreur est survenue. Votre exercice n'a pas été modifié."),'error')

return state
