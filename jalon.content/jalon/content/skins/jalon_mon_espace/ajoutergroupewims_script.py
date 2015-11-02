# -*- coding: utf-8 -*-
"""Controller Python Script "ajoutergroupewims_script". """
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajout et/ou modification d'un exercice WIMS
##

from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST
param = None

modele = REQUEST["modele"]

if not REQUEST.has_key("idobj"):
    #--ajouter un nouveau groupe--
    idobj = context.invokeFactory(type_name='JalonExerciceWims', id="%s-%s-%s" % (modele, context.supprimerCaractereSpeciaux(REQUEST["authMember"]), DateTime().strftime("%Y%m%d%H%M%S")))
    message = "groupe_added"

#obj est un element de type "jalonexercicewims"
obj = getattr(context, idobj)

#Tant qu'il n'y a pas de page de modification des groupes d'exos, on retourne sur la page precedente.
page_url = "%s?" % (context.absolute_url())

if REQUEST["title"] != "":
    if REQUEST.has_key("paths"):
        listeIdsExos = []
        for path in REQUEST["paths"]:
            if not "groupe-" in path:
                listeIdsExos.append(path.split("/")[-1])
        obj.setProperties({"Title": REQUEST["title"],
                           "Modele": modele,
                           "Qnum": REQUEST["qnum"],
                           "ListeIdsExos": listeIdsExos})
        rep = obj.ajouterSerie(REQUEST["authMember"])
    else:
        rep = {"status": "ERROR", "err_code": "no_exercice_selected"}
else:
    rep = {"status": "ERROR", "err_code": "no_title"}


if not("status" in rep):
    # La creation a planté (Cause ?)
    context.manage_delObjects(ids=[idobj])
    message = "unknown_error"
else:
    if rep["status"] != "OK":
        if "err_code" in rep:
            message = rep["err_code"]
        else:
            #on suppose que WIMS était indisponible
            message = "wims_unavailable"

        # La creation n'a pas aboutit coté WIMS, on supprime l'objet que l'on vient de créer sur Jalon.
        context.manage_delObjects(ids=[idobj])
    else:
        context.plone_utils.addPortalMessage(_(u"Votre groupe d'exercices « %s » a bien été créé." % obj.Title().decode("utf-8")), 'success')


#On encode le titre pour qu'il passe correctement dans l'url
title = obj.Title().replace("&", "%26").replace(";", "%3B")

redirection = "%smessage=%s&title=%s" % (page_url, message, title)
return context.REQUEST.RESPONSE.redirect(redirection)
