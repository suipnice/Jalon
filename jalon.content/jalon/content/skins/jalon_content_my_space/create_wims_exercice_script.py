# -*- coding: utf-8 -*-
"""##Controller Python Script "create_wims_exercice_script"."""
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

""" Script de creation des exercices WIMS de Mon Espace."""
""" Cheminement normal : my_wims_exercices_view.pt -> javascript:setRevealFormNewPage()
                            -> create_wims_exercice_form.cpt -> validate_my_space
                                -> create_wims_exercice_script -> javascript:setRevealFormNewPage() -> $page_url """
# Le contexte est un jalonfolder
#context = context
REQUEST = context.REQUEST
form = REQUEST.form

wims_exercice_model = form["modele"]

# attention : possible "faille" de securité : si un utilisateur envoi un autre member_id, il créé l'exercice dans un autre espace.
user_id = context.supprimerCaractereSpeciaux(form["member_id"])
wims_exercice_folder = context.getMySubSpaceFolder(user_id, "Wims")

# Create a new JalonExerciceWIMS
object_id = wims_exercice_folder.invokeFactory(type_name='JalonExerciceWims', id="%s-%s-%s" % (wims_exercice_model, user_id, DateTime().strftime("%Y%m%d%H%M%S")))
wims_exercice_object = getattr(wims_exercice_folder, object_id)

page_url = context.absolute_url()

title = form["title"].decode("utf-8")
success_message       = _(u"L'exercice « %s » a été ajouté. Construisez-le ci-dessous." % title)
unknown_model_message = _(u"Une erreur est survenue sur votre exercice « %s » (modèle introuvable ?). Merci de contacter l'administrateur de cette plateforme, en fournissant tous les détails possibles permettant de reproduire cette erreur svp." % title)
unavailable_message   = _(u"Le serveur WIMS est actuellement injoignable. Merci de réessayer ultérieurement.")

# Cas des Modules externes
if wims_exercice_model == "externe":
    permalink = REQUEST.get("permalink", '')
    wims_exercice_object.setProperties({"Title":     form["title"],
                                        "Modele":    wims_exercice_model,
                                        "Permalink": permalink})

# Cas classique : on ajoute l'exercice côté WIMS
else:
    rep = wims_exercice_object.addExoWims(idobj=object_id, title=form["title"], author_id=user_id, modele=wims_exercice_model)
    # print rep
    if not("status" in rep):
        # La creation a planté (Cause : modele inconnu ?)
        wims_exercice_folder.manage_delObjects(ids=[object_id])
        context.plone_utils.addPortalMessage(unknown_model_message, 'error')
    else:
        # L'appel à WIMS s'est bien passé, on applique les modifications à l'objet Jalon
        if rep["status"] == "OK":
            wims_exercice_object.setProperties({"Title":  form["title"],
                                                "Modele": wims_exercice_model})
            context.plone_utils.addPortalMessage(success_message, 'success')
            page_url = "%s/edit_wims_exercice_form" % wims_exercice_object.absolute_url()
        else:
            # La creation a planté coté WIMS, on supprime l'objet que l'on vient de créer sur Jalon.
            wims_exercice_folder.manage_delObjects(ids=[object_id])
            context.plone_utils.addPortalMessage(unavailable_message, 'error')

return page_url
