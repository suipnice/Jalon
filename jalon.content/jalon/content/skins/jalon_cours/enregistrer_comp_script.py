## Controller Python Script "enregistrer_comp_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

compEtudiants = dict(context.getCompEtudiants())
for etudiantForm in form["etudiants"]:
    etudiant = dict(etudiantForm)
    etudiant_id = etudiant["id"]
    del etudiant["id"]
    compEtudiants[etudiant_id] = etudiant

context.setCompEtudiants(compEtudiants)
context.REQUEST.RESPONSE.redirect("%s?menu=competences" % context.absolute_url())