# -*- coding: utf-8 -*-
## Controller Python Script "create_wims_exercice_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# PloneMessageFactory permet d'utiliser le systeme i18n
from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST
form = REQUEST.form

wims_exercice_model = form["modele"]
user_id = context.supprimerCaractereSpeciaux(form["member_id"])
wims_exercice_folder = context.getMySubSpaceFolder(user_id, "Wims")

object_id = wims_exercice_folder.invokeFactory(type_name='JalonExerciceWims', id="%s-%s-%s" % (wims_exercice_model, user_id, DateTime().strftime("%Y%m%d%H%M%S")))

message = "exercice_added"
param = None

#obj est un element de type "jalonexercicewims"
wims_exercice_object = getattr(wims_exercice_folder, object_id)
page_url = "%s/exercicewims_edit?" % wims_exercice_object.absolute_url()


# Cas des Modules externes
if wims_exercice_model == "externe":
    permalink = REQUEST.get("permalink", '')
    wims_exercice_object.setProperties({"Title":     form["title"],
                                        "Modele":    wims_exercice_model,
                                        "Permalink": permalink,})

# Cas classique : on ajoute l'exercice côté WIMS
else:
    rep = wims_exercice_object.addExoWims(object_id, form["title"], user_id, wims_exercice_model, param)
    #print rep
    if not("status" in rep):
        # La creation a planté (Cause : modele inconnu ?)
        wims_exercice_object.manage_delObjects(ids=[object_id])
        message = "unknown_model"
    else:
        #L'appel à WIMS s'est bien passé, on applique les modifications à l'objet Jalon
        if rep["status"] == "OK":
            wims_exercice_object.setProperties({"Title":  form["title"],
                                                "Modele": wims_exercice_model})
        else:
            # La creation a planté coté WIMS, on supprime l'objet que l'on vient de créer sur Jalon.
            wims_exercice_folder.manage_delObjects(ids=[object_id])
            message = "wims_unavailable"
            page_url = "%s/?" % context.absolute_url()

#On encode le titre pour qu'il passe correctement dans l'url
title = wims_exercice_object.Title().replace("&", "%26").replace(";", "%3B").replace(" ", "%20")

redirection = "%smessage=%s&title=%s" % (page_url, message, title)
context.plone_utils.addPortalMessage(_(u"L'exercice « %s » a été ajouté. Construisez-le ci-dessous." % wims_exercice_object.Title().decode("utf-8")), 'success')

return redirection