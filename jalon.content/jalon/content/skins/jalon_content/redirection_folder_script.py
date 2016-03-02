## Controller Python Script "rediriger_etudiant"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=user
##title=
##

portal_link = context.absolute_url()
redirection = "%s/mon_espace" % portal_link
if user.has_role(["Etudiant", "EtudiantJalon"]):
    redirection = "%s/mes_cours" % portal_link

context.REQUEST.RESPONSE.redirect(redirection)
