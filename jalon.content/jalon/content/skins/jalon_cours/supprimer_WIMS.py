# -*- coding: utf-8 -*-
## Controller Python Script "supprimer_WIMS"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Supprimer toutes les activités WIMS d'un cours
##
u""" Script de suppression de l'ensemble des activités WIMS d'un cours."""

# MessageFactory permet d'utiliser le systeme i18n
#normalement on devrait utiliser celui de jalon.content, mais souci de privileges ?
#from jalon.content import contentMessageFactory as _
from Products.CMFPlone import PloneMessageFactory as _

#### On commence par s'assurer que c'est bien un coauteur qui lance la commande.
authMember = context.REQUEST["AUTHENTICATED_USER"]
authMember_id = authMember.getId()

if context.isAuteurs(authMember_id):

    titre_cours = context.aq_parent.getShortText(context.Title()).decode("utf-8")

    # si authmember est auteur/createur, il peut choisir quelles activités il souhaite supprimer
    if context.isAuteur(authMember_id):
        if "utilisateur" in context.REQUEST:
            utilisateur = context.REQUEST["utilisateur"]
        else:
            utilisateur = "--aucun--"
            message = u"Vous n'avez selectionné aucun utilisateur. Aucune activité supprimée."
            context.plone_utils.addPortalMessage(_(message), "info")
    # Si authmember est un coauteur, il ne peux supprimer que ses propres activités
    else:
        utilisateur = authMember_id

    # On supprime les activités WIMS
    resultat = context.supprimerActivitesWims(utilisateur=utilisateur)
    if resultat > 0:
        message = u"<strong>%s</strong> activité(s) WIMS a(ont) bien été supprimée(s) du cours « <strong>%s</strong> »." % (resultat, titre_cours)
        context.plone_utils.addPortalMessage(_(message), "info")

else:
    message = _(u"Vous tentez d'accéder à une page qui ne vous appartient pas. Une suspicion de fraude vous concernant a été envoyée à l'administrateur du site.")
    context.plone_utils.addPortalMessage(_(message), "alert")
    context.envoyerMailErreur({"objet"  : "Unauthorized access to purger_activites",
                               "message": "<p>Suspicion de fraude de l'utilisateur <strong>%s</strong></p><div>%s</div>" % (authMember_id, context.REQUEST)})


if "came_from" in context.REQUEST and context.REQUEST["came_from"] == "cours_plan_view":
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    context.REQUEST.RESPONSE.redirect(context.aq_parent.absolute_url())
