##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=recherchUtilisateurs
##

context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
form = context.REQUEST.form
if form.has_key("rechercheEtu"):
	return context.rechercherUtilisateursByName(form["rechercheEtu"], "Etudiant", True)
else:
	return context.rechercherUtilisateursByName(form["rechercheEns"], "Personnel", True)
