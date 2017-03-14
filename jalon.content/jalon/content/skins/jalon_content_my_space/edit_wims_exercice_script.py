# -*- coding: utf-8 -*-
"""## Python Script "edit_wims_exercice_script"."""
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

""" Script d'edition des exercices WIMS de Mon Espace."""
# Le contexte est un JalonExerciceWims
# context = context
REQUEST = context.REQUEST
form = REQUEST.form

object_id = context.getId()
object_link = context.absolute_url()
wims_exercice_model = form["modele"]
# attention : possible faille de securité : si un utilisateur envoi un autre member_id
user_id = context.supprimerCaractereSpeciaux(form["member_id"])
wims_exercice_folder = context.aq_parent.getMySubSpaceFolder(user_id, "Wims")

title = context.Title().decode("utf-8")
success_message       = _(u"Votre exercice « %s » a bien été modifié." % title)
unknown_model_message = _(u"Une erreur est survenue sur votre exercice « %s » (modèle introuvable ?). Merci de contacter l'administrateur de cette plateforme, en fournissant tous les détails possibles permettant de reproduire cette erreur svp." % title)
syntax_error_message  = _(u"Votre exercice « %s » n'a pas été enregistré, probablement suite à une erreur de syntaxe.<br />Par exemple, lorsque vous utilisez des parenthèses, accolades ou crochets, veillez à les placer par paires correctement fermées." % title)
unavailable_message   = _(u"Le serveur WIMS est actuellement injoignable. Merci de réessayer ultérieurement svp...")

if "save_and_test" in form:
    # url de test direct de l'exercice actuel :
    page_url = object_link
else:
    # url de modification de l'exercice
    page_url = "%s/edit_wims_exercice_form" % object_link

# Cas des Modules externes
if wims_exercice_model == "externe":
    permalink = REQUEST.get("permalink", '')
    context.setProperties({"Title":     form["title"],
                           "Modele":    wims_exercice_model,
                           "Permalink": permalink})
    context.plone_utils.addPortalMessage(success_message, 'success')

# Cas classique : on modifie  l'exercice côté WIMS
else:
    rep = context.addExoWims(object_id, form["title"], user_id, wims_exercice_model, form)
    # print rep
    if not("status" in rep):
        # La creation a planté (Cause : modele inconnu ?)
        # nb : ceci ne devrait jamais survenir en modification a priori.
        # wims_exercice_folder.manage_delObjects(ids=[object_id])
        context.plone_utils.addPortalMessage(unknown_model_message, 'error')
    else:
        if rep["status"] == "OK":
            # L'appel à WIMS s'est bien passé, on applique les modifications à l'objet Jalon
            context.plone_utils.addPortalMessage(success_message, 'success')
            context.setProperties({"Title":  form["title"],
                                   "Modele": wims_exercice_model})
        else:
            # La creation a planté coté WIMS
            if "error_code" in rep and rep["error_code"] == "503":
                # L'erreur 503 indique une interruption de WIMS
                context.plone_utils.addPortalMessage(unavailable_message, 'error')
            else:
                # on suppose que la creation a planté suite a une erreur de syntaxe.
                context.plone_utils.addPortalMessage(syntax_error_message, 'error')
            page_url = object_link

context.REQUEST.RESPONSE.redirect(page_url)
