# -*- coding: utf-8 -*-
"""Python Script "export_wims_exercices_script"."""
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Export d'une selection d'exercices WIMS
##
from Products.CMFPlone import PloneMessageFactory as _

u"""  Script (Python) "export_wims_exercice_script".

Fournit un fichier telechargeable des exos WIMS selectionnés, selon le format demandé (Moodle, OEF...)
"""

# context = context
request = context.REQUEST
form = request.form

user_id = context.supprimerCaractereSpeciaux(form["authMember"])

# TODO : voir le code de "export_wims_exercice_script" pour l'appliquer ici

# request n'est pas un veritable dico, donc pas de "in"
if request.has_key("type"):
    file_format = request["type"]
else:
    # Par défaut, on exporte en Moodle_XML
    file_format = "Moodle"


if "paths" in form:
    listeIdsExos = []
    for path in form["paths"]:
        if "groupe-" not in path:
            id_exo = path.split("/")[-1]
            if id_exo not in listeIdsExos:
                listeIdsExos.append(id_exo)
    if file_format == "Moodle":
        file_content = context.exportExercicesWIMS_XML(listeIdsExos, user_id, file_format, "latest")
        context.plone_utils.addPortalMessage(_(u"Votre archive d'exercices a bien été générée."), 'success')
    else:
        filename = "%s_WIMS_%s.zip" % (file_format, user_id)
        zipfile = context.exportExercicesWIMS_zip(listeIdsExos, user_id)

        request.RESPONSE.setHeader('content-type', "application/zip")
        request.RESPONSE.setHeader('content-length', zipfile["length"])
        request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
        context.plone_utils.addPortalMessage(_(u"Votre archive d'exercices a bien été générée."), 'success')
        return zipfile["data"]

else:
    message = _(u"Aucun exercice selectionné")
    file_content = "<error>%s</error>" % message
    context.plone_utils.addPortalMessage(message, 'failure')

filename = "export_WIMS_%s.xml" % user_id
context.REQUEST.RESPONSE.setHeader('content-type', "application/xml")
context.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)

return file_content
