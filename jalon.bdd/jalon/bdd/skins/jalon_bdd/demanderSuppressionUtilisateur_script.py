##Python Script "demanderSuppressionUtilisateur"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=suppresstUtilisateur
##

form = context.REQUEST.form
context.envoyerMail(form["idSuppression"], form["idDemande"])
context.REQUEST.RESPONSE.redirect("%s/gestion_utilisateurs" % context.absolute_url())
