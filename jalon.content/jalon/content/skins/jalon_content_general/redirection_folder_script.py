## Controller Python Script "rediriger_etudiant"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=user
##title=
##

REQUEST = context.REQUEST
came_from = REQUEST.get("came_from", None)
if came_from:
    return True
else:
    context.REQUEST.RESPONSE.redirect("%s/mes_cours" % context.absolute_url())
    #portal_link = context.absolute_url()
    #redirection = "%s/mes_ressources" % portal_link
    #if user.has_role(["Etudiant", "EtudiantJalon"]):
    #    redirection = "%s/mes_cours" % portal_link
    #context.REQUEST.RESPONSE.redirect(redirection)
