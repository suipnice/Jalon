## Controller Python Script "setRoleUtilisateur"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
context.etudiants.setRoleUtilisateurExterieur(request["utilisateur"], request["role"], request["value"])
request.RESPONSE.redirect("%s/@@jalon-user" % context.absolute_url())