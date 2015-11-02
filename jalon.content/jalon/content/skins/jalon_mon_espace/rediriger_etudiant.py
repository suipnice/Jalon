## Controller Python Script "rediriger_etudiant"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=login=None, role=False
##title=
##

redirection = "%s/cours/%s" % (context.absolute_url(), login)
#if role:
#    redirection = "%s/portal_jalon_bdd/gestion_utilisateurs" % context.absolute_url()
return context.REQUEST.RESPONSE.redirect(redirection)