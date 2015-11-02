##Python Script "inscrireEnseignant_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=inscrireEnseignant_script
##

form = context.REQUEST.form
redirection = "%s/@@jalon-bdd?gestion=gestion_bdd" % context.absolute_url()

if not "enseignants_mod" in form and "enseignants_actu" in form:
    dico = {"COD_ELP"     : form["COD_ELP"],
            "enseignants" : form["enseignants_actu"]}
    context.desinscrireEnseignant(dico)

if "enseignants_mod" in form and "enseignants_actu" in form:
    for enseignant in form["enseignants_mod"]:
        form["enseignants_actu"].remove(enseignant)
        dico = {"COD_ELP"     : form["COD_ELP"],
                "enseignants" : form["enseignants_actu"]}
    context.desinscrireEnseignant(dico)

if form["username"]:
    context.inscrireEnseignant(form)

"""
if form["from"] == "listeTousEns:list":
	context.inscrireEnseignant(form)
else:
	context.desinscrireEnseignant(form)

if "redirection" in form.keys():
    redirection = form["redirection"]
"""

#return form
context.REQUEST.RESPONSE.redirect(redirection)
