# -*- coding: utf-8 -*-
## Controller Python Script "getscores_wims"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Télécharger les notes de tous les examens WIMS d'un cours
##
u""" Script pour télécharger les notes de l'ensemble des examens WIMS d'un cours."""

# MessageFactory permet d'utiliser le systeme i18n
#normalement on devrait utiliser celui de jalon.content, mais souci de privileges ?
#from jalon.content import contentMessageFactory as _
from Products.CMFPlone import PloneMessageFactory as _

#### On commence par s'assurer que c'est bien un coauteur qui lance la commande.
authMember = context.REQUEST["AUTHENTICATED_USER"]
authMember_id = authMember.getId()

if context.isAuteurs(authMember_id):

    titre_cours = context.aq_parent.getShortText(context.Title()).decode("utf-8")

    if "utilisateur" in context.REQUEST:
        utilisateur = context.REQUEST["utilisateur"]
    else:
        utilisateur = "--aucun--"
        message = u"Vous n'avez selectionné aucun utilisateur."
        context.plone_utils.addPortalMessage(_(message), "info")


    # On demande les notes à WIMS
    #resultat = context.supprimerActivitesWims(utilisateur=utilisateur, request=context.REQUEST)
    if resultat > 0:
        message = u"<strong>%s</strong> activité(s) WIMS a(ont) bien été téléchargée(s) du cours « <strong>%s</strong> »." % (resultat, titre_cours)
        context.plone_utils.addPortalMessage(_(message), "info")

else:
    message = _(u"Vous tentez d'accéder à une page qui ne vous appartient pas. Une suspicion de fraude vous concernant a été envoyée à l'administrateur du site.")
    context.plone_utils.addPortalMessage(_(message), "alert")
    context.envoyerMailErreur({"objet"  : "Unauthorized access to getscores_wims",
                               "message": "<p>Suspicion de fraude de l'utilisateur <strong>%s</strong></p><div>%s</div>" % (authMember_id, context.REQUEST)})


if "came_from" in context.REQUEST and context.REQUEST["came_from"] == "cours_plan_view":
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    context.REQUEST.RESPONSE.redirect("%s?onglet=%s" % (context.aq_parent.absolute_url(), context.REQUEST["onglet"]))
