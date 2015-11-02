##Python Script "creerUtilisateur_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=creerUtilisateur_script
##

form = context.REQUEST.form
if not "PROMO_IND" in form:
    form["PROMO_IND"] = 1
context.creerUtilisateur(form)
context.REQUEST.RESPONSE.redirect("%s/%s?gestion=gestion_utilisateurs" % (context.absolute_url(), form["redirection"]))
