# -*- coding: utf-8 -*-
## Controller Python Script "delete_wims_activity_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Dupliquer un cours
##

from Products.CMFPlone import PloneMessageFactory as _
# context = context
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
    # si user_id est auteur/createur, il peut choisir quelles activités il souhaite supprimer
    if course_object.isAuteur(user_id):
        if "utilisateur" in request:
            utilisateur = request["utilisateur"]
        else:
            utilisateur = "--aucun--"
            message = _(u"Vous n'avez selectionné aucun utilisateur. Aucune activité supprimée.")
            context.plone_utils.addPortalMessage(message, "info")
    # Si user_id est un co-auteur, il ne peux supprimer que ses propres activités
    else:
        utilisateur = user_id

    # On supprime les activités WIMS
    resultat = course_object.supprimerActivitesWims(utilisateur=utilisateur, request=request)
    if resultat > 0:
        message = _(u"<strong>%s</strong> activité(s) WIMS a(ont) bien été supprimée(s) du cours « <strong>%s</strong> »." % (resultat, course_object.getShortText(course_object.Title()).decode("utf-8")))
        context.plone_utils.addPortalMessage(message, "info")
else:
    message = _(u"Vous tentez d'accéder à une page qui ne vous appartient pas. Une suspicion de fraude vous concernant a été envoyée à l'administrateur du site.")
    context.plone_utils.addPortalMessage(message, "alert")
    context.envoyerMailErreur({"objet":   "Unauthorized access to supprimer_WIMS",
                               "message": "<p>Suspicion de fraude de l'utilisateur <strong>%s</strong></p><div>%s</div>" % (user_id, request)})

request.RESPONSE.redirect(redirection)
