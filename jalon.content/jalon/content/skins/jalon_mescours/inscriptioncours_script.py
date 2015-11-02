## Controller Python Script "inscriptioncours_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Inscrire un étudiant à un cours après vérification du mot de passe
##

REQUEST = context.REQUEST

cours = getattr(getattr(context.aq_parent, REQUEST.form["auteur"]), REQUEST.form["idcours"])
cours.inscrireMOOC(REQUEST["memberid"])

context.REQUEST.RESPONSE.redirect(cours.absolute_url())