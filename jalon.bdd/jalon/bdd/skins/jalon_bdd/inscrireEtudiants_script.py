##Python Script "inscrireEtudiants_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=inscrireEtudiants_script
##

form = context.REQUEST.form
redirection = context.absolute_url()

form = context.REQUEST.form
redirection = "%s/@@jalon-bdd?gestion=gestion_bdd" % context.absolute_url()

if not "etudiants_mod" in form and "etudiants_actu" in form:
    dico = {"COD_ELP"   : form["COD_ELP"],
            "etudiants" : form["etudiants_actu"]}
    context.desinscrireEtudiant(dico)

if "etudiants_mod" in form and "etudiants_actu" in form:
    for enseignant in form["etudiants_mod"]:
        form["etudiants_actu"].remove(enseignant)
        dico = {"COD_ELP"   : form["COD_ELP"],
                "etudiants" : form["etudiants_actu"]}
    context.desinscrireEtudiant(dico)

if form["username"]:
    context.inscrireEtudiant(form)

"""
if form["from"] == "listeTousEtu:list":
	context.inscrireEtudiant(form)
else:
	context.desinscrireEtudiant(form)

if "redirection" in form.keys():
    redirection = form["redirection"]
"""
context.REQUEST.RESPONSE.redirect(redirection)
