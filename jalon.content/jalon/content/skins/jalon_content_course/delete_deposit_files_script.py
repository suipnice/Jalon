# -*- coding: utf-8 -*-
## Controller Python Script "delete_deposit_files_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Purger les dépôts d'une boite de dépôts
##


#### On commence par s'assurer que c'est bien un coauteur qui lance la commande.
authMember = context.REQUEST["AUTHENTICATED_USER"]
if context.isAuteurs(authMember.getId()):
    context.purgerDepots()
else:
    message = u"Vous tentez d'accéder à une page qui ne vous appartient pas. Une suspicion de fraude vous concernant a été envoyée à l'administrateur du site."
    context.plone_utils.addPortalMessage(message, "alert")

    context.envoyerMailErreur({"objet":   "Unauthorized access to purger_depots",
                               "message": "<p>Suspicion de fraude de l'utilisateur <strong>%s</strong></p><div>%s</div>" % (authMember.getId(), context.REQUEST)})

context.REQUEST.RESPONSE.redirect("%s?tab=deposit" % context.absolute_url())