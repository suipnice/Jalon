##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')

if form.has_key("coauteur"):
    return context.rechercherUtilisateur(form["coauteur"], "Personnel")
else:
    return context.rechercherUtilisateur(form["groupe"], "Etudiant")
