# -*- coding: utf-8 -*-
## Controller Python Script "download_wims_score_script"
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

request = context.REQUEST
user_id = request.form["user_id"]

if "course_id" in request.form:
    course_id = request.form["course_id"]
    course_user_folder = context.getCourseUserFolder(user_id)
    course_object = getattr(course_user_folder, course_id)
    redirection = "%s?tab=%s" % (context.absolute_url(), request.form["tab"])
else:
    course_object = context
    redirection = context.absolute_url()


if course_object.isAuteurs(user_id):
    titre_cours = course_object.getShortText(course_object.Title()).decode("utf-8")

    if "utilisateur" in request:
        utilisateur = request["utilisateur"]
    else:
        utilisateur = "--aucun--"
        message = u"Vous n'avez selectionné aucun utilisateur."
        context.plone_utils.addPortalMessage(_(message), "info")

    file_format = "csv" if "file_format" not in request.form else request["file_format"]

    dico_format = {"csv": ["csv", "csv"],
                   "tsv": ["tsv", "tab-separated-values"],
                   "xls": ["csv", "csv"]}

    # On demande les notes à WIMS
    resultat = course_object.getScoresWims(auteur=utilisateur, authMember=user_id, request=request, file_format=file_format)
    if resultat["status"] == "OK":
        #message = u"Les notes des activités WIMS du cours « <strong>%s</strong> » ont bien été téléchargées ." % (titre_cours)
        #context.plone_utils.addPortalMessage(_(message), "info")
        filename = "%s.%s" % (course_object.getId(), dico_format[file_format][0])
        if file_format == "xls":
            #Comme Excel (francais) ne prend pas automatiquement l'utf-8, on réencode en iso pour lui.
            charset = "Windows-1252"
            resultat["data"] = resultat["data"].decode("utf-8").encode(charset)
        else:
            charset = "utf-8"
        request.RESPONSE.setHeader('content-type', "text/%s; charset=%s" % (dico_format[file_format][1], charset))
        request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)

        return resultat["data"]
    elif resultat["status"] == "not_relevant":
        message = _(u"Votre cours ne contient aucun examen ou autoévaluation active créé(s) par l'utilisateur « <strong>%s</strong> ».<br/>\
                      Commencez par afficher une autoévaluation pour pouvoir télécharger des notes." % utilisateur)
        context.plone_utils.addPortalMessage(_(message), "warning")
    else:
        # Erreur possible : plus de 64 feuilles (sachant que pour chaque examen, une feuille est créée.)
        message = _(u"Une erreur est survenue.<blockquote>%s</blockquote> nb : attention à ne pas dépasser <strong>60</strong> activités WIMS dans un seul cours." % resultat["message"])
        context.plone_utils.addPortalMessage(_(message), "alert")
else:
    message = _(u"Vous tentez d'accéder à une page qui ne vous appartient pas. Une suspicion de fraude vous concernant a été envoyée à l'administrateur du site.")
    context.plone_utils.addPortalMessage(_(message), "alert")
    context.envoyerMailErreur({"objet"  : "Unauthorized access to getscores_wims",
                               "message": "<p>Suspicion de fraude de l'utilisateur <strong>%s</strong></p><div>%s</div>" % (authMember_id, request)})

request.RESPONSE.redirect(redirection)
