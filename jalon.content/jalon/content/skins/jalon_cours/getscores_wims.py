# -*- coding: utf-8 -*-
## Controller Python Script "getscores_wims"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Télécharger les notes de toutes les activités WIMS d'un cours
##
u""" Script pour télécharger les notes de l'ensemble des activités WIMS d'un cours."""

# MessageFactory permet d'utiliser le systeme i18n
#normalement on devrait utiliser celui de jalon.content, mais souci de privileges ?
#from jalon.content import contentMessageFactory as _
from Products.CMFPlone import PloneMessageFactory as _

#### On commence par s'assurer que c'est bien un coauteur qui lance la commande.
request = context.REQUEST
authMember = request["AUTHENTICATED_USER"]
authMember_id = authMember.getId()


if context.isPersonnel(authMember):

    titre_cours = context.aq_parent.getShortText(context.Title()).decode("utf-8")

    if "utilisateur" in request:
        utilisateur = request["utilisateur"]
    else:
        utilisateur = "--aucun--"
        message = u"Vous n'avez selectionné aucun utilisateur."
        context.plone_utils.addPortalMessage(_(message), "info")

    file_format = "csv"
    if "file_format" in request:
        file_format = request["file_format"]

    dico_format = {"csv": ["csv", "csv"],
                   "tsv": ["tsv", "tab-separated-values"],
                   "xls": ["csv", "csv"]}

    # On demande les notes à WIMS
    resultat = context.getScoresWims(auteur=utilisateur, authMember=authMember_id, request=request, file_format=file_format)
    if resultat["status"] == "OK":
        #message = u"Les notes des activités WIMS du cours « <strong>%s</strong> » ont bien été téléchargées ." % (titre_cours)
        #context.plone_utils.addPortalMessage(_(message), "info")
        filename = "%s.%s" % (context.getId(), dico_format[file_format][0])
        request.RESPONSE.setHeader('content-type', "text/%s" % dico_format[file_format][1])
        request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
        return resultat["data"]
    elif resultat["status"] == "not_relevant":
        message = _(u"Votre cours ne contient aucun examen ou autoévaluation active créé(s) par l'utilisateur « <strong>%s</strong> ».<br/>\
                      Commencez par afficher une autoévaluation pour pouvoir télécharger des notes." % utilisateur)
        context.plone_utils.addPortalMessage(_(message), "warning")
    else:
        message = _(u"Une erreur est survenue.<blockquote>%s</blockquote>" % resultat["message"])
        context.plone_utils.addPortalMessage(_(message), "alert")
else:
    message = _(u"Vous tentez d'accéder à une page qui ne vous appartient pas. Une suspicion de fraude vous concernant a été envoyée à l'administrateur du site.")
    context.plone_utils.addPortalMessage(_(message), "alert")
    context.envoyerMailErreur({"objet"  : "Unauthorized access to getscores_wims",
                               "message": "<p>Suspicion de fraude de l'utilisateur <strong>%s</strong></p><div>%s</div>" % (authMember_id, request)})


#if "came_from" in request and request["came_from"] == "cours_plan_view":
request.RESPONSE.redirect(context.absolute_url())
"""
else:
    onglet = 2
    if "onglet" in request:
        onglet = request["onglet"]
    request.RESPONSE.redirect("%s?onglet=%s" % (context.aq_parent.absolute_url(), onglet))
"""
