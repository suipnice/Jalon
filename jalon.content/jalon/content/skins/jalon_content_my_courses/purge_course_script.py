# -*- coding: utf-8 -*-
## Controller Python Script "dupliquer_cours"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Dupliquer un cours
##

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
    # On purge les boites de dépot
    course_object.purgerDepots()

    message = u"Le cours « <strong>%s</strong> » a bien été purgé." % course_object.getShortText(course_object.Title()).decode("utf-8")
    context.plone_utils.addPortalMessage(_(message), "success")

    # Puis on purge les activités WIMS
    resultatWIMS = course_object.purgerActivitesWims()

    if resultatWIMS:
        compteur = 0
        for userWims in resultatWIMS:
            if resultatWIMS[userWims]["cleaned"] is not None:
                compteur = compteur + resultatWIMS[userWims]["cleaned"]
            else:
                message = u"Une erreur est survenue lors de la purge des activités WIMS"
                context.plone_utils.addPortalMessage(_(message), "error")

        message = u"<strong>%s</strong> note(s) Wims supprimée(s)" % (compteur)
        context.plone_utils.addPortalMessage(_(message), "info")
else:
    message = _(u"Vous tentez d'accéder à une page qui ne vous appartient pas. Une suspicion de fraude vous concernant a été envoyée à l'administrateur du site.")
    context.plone_utils.addPortalMessage(_(message), "alert")
    context.envoyerMailErreur({"objet":   "Unauthorized access to purger_activites",
                               "message": "<p>Suspicion de fraude de l'utilisateur <strong>%s</strong></p><div>%s</div>" % (user_id, request)})

request.RESPONSE.redirect(redirection)
