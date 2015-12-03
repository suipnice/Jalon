# -*- coding: utf-8 -*-
## Controller Python Script "purger_activites"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Purger les activités d'un cours
##

# MessageFactory permet d'utiliser le systeme i18n
#normalement on devrait utiliser celui de jalon.contnet, mais souci de privileges ?
#from jalon.content import contentMessageFactory as _
from Products.CMFPlone import PloneMessageFactory as _

#### On commence par s'assurer que c'est bien un coauteur qui lance la commande.
authMember = context.REQUEST["AUTHENTICATED_USER"]
if context.isAuteurs(authMember.getId()):
    # On purge les boites de dépot
    context.purgerDepots()

    message = u"Le cours « <strong>%s</strong> » a bien été purgé." % context.aq_parent.getShortText(context.Title()).decode("utf-8")
    context.plone_utils.addPortalMessage(_(message), "success")

    # Puis on purge les activités WIMS
    resultatWIMS = context.purgerActivitesWims()

    if resultatWIMS:
        compteur = 0
        for userWims in resultatWIMS:
            if resultatWIMS[userWims]["cleaned"] != None:
                compteur = compteur + resultatWIMS[userWims]["cleaned"]
            else:
                message = u"Une erreur est survenue lors de la purge des activités WIMS"
                context.plone_utils.addPortalMessage(_(message), "error")

        message = u"<strong>%s</strong> note(s) Wims supprimée(s)" % (compteur)
        context.plone_utils.addPortalMessage(_(message), "info")
else:
    message = _(u"Vous tentez d'accéder à une page qui ne vous appartient pas. Une suspicion de fraude vous concernant a été envoyée à l'administrateur du site.")
    context.plone_utils.addPortalMessage(_(message), "alert")
    context.envoyerMailErreur({"objet"  : "Unauthorized access to purger_activites",
                               "message": "<p>Suspicion de fraude de l'utilisateur <strong>%s</strong></p><div>%s</div>" % (authMember.getId(), context.REQUEST)})


if "came_from" in context.REQUEST and context.REQUEST["came_from"]=="cours_plan_view":
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    context.REQUEST.RESPONSE.redirect(context.aq_parent.absolute_url())
