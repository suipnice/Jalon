# -*- coding: utf-8 -*-
## Controller Python Script "edit_wims_exercice_script"
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

param = form
object_id = context.getId()
object_link = context.absolute_url()
wims_exercice_model = form["modele"]
user_id = context.supprimerCaractereSpeciaux(form["member_id"])
wims_exercice_folder = context.getMySubSpaceFolder(user_id, "Wims")

message = "exercice_modified"

if "save_and_test" in form:
    # url de test direct de l'exercice actuel :
    page_url = "%s/view?" % object_link
else:
    # url de modification de l'exercice
    page_url = "%s/exercicewims_edit?" % object_link

# Cas des Modules externes
if wims_exercice_model == "externe":
    permalink = REQUEST.get("permalink", '')
    context.setProperties({"Title":     form["title"],
                           "Modele":    wims_exercice_model,
                           "Permalink": permalink})
# Cas classique : on ajoute l'exercice côté WIMS
else:
    rep = context.addExoWims(object_id, form["title"], user_id, wims_exercice_model, param)
    #print rep
    if not("status" in rep):
        # La creation a planté (Cause : modele inconnu ?)
        wims_exercice_folder.manage_delObjects(ids=[object_id])
        message = "unknown_model"
    else:
        #L'appel à WIMS s'est bien passé, on applique les modifications à l'objet Jalon
        if rep["status"] == "OK":
            context.setProperties({"Title":  form["title"],
                                   "Modele": wims_exercice_model})
        else:
            # La creation a planté coté WIMS, on supprime l'objet que l'on vient de créer sur Jalon.
            wims_exercice_folder.manage_delObjects(ids=[object_id])
            message = "wims_unavailable"
            page_url = "%s/?" % context.absolute_url()

#On encode le titre pour qu'il passe correctement dans l'url
title = context.Title().replace("&", "%26").replace(";", "%3B").replace(" ", "%20")

redirection = "%smessage=%s&title=%s" % (page_url, message, title)
context.plone_utils.addPortalMessage(_(u"Votre exercice « %s » a bien été modifié." % context.Title().decode("utf-8")),'success')

context.REQUEST.RESPONSE.redirect(redirection)