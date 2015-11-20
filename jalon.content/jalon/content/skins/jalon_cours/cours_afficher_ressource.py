## Controller Python Script "cours_afficher_ressource"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Affiche ou Masque un element du cours
##

request = context.REQUEST

if request.form.has_key("date-affichage-now"):
    # 1er cas : On affiche immediatement
    dateAffichage = DateTime()
else:
    # 2e Cas on programme l'affichage / masquage
    #dateAffichage = DateTime("%s/%s/%s %s:%s" % (request["date-affichage_year"], request["date-affichage_month"], request["date-affichage_day"], request["date-affichage_hour"], request["date-affichage_minute"]))
    dateAffichage = DateTime(request["datetime"])

# attribut nous informe de l'action a effectuer (attribut = masquerElement ou affElement)
if request.has_key("chapitre") and request["chapitre"] == "contenu":
    context.afficherRessourceChapitre(request["idElement"], dateAffichage, request["attribut"])
else:
    context.afficherRessource(request["idElement"], dateAffichage, request["attribut"])

if request.form.has_key("idParent"):
    context.afficherChapitresParent(request["idParent"], dateAffichage)

redirection = context.absolute_url()
#if request["idElement"].startswith("BoiteDepot"):
#    redirection = "%s?menu=%s" % (redirection, menu)

return context.REQUEST.RESPONSE.redirect(redirection)
