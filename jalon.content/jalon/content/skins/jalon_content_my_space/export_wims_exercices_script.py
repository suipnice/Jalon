# -*- coding: utf-8 -*-
"""Controller Python Script "export_wims_exercices_script"."""
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Export d'une selection d'exercices WIMS
##

from Products.CMFPlone import PloneMessageFactory as _
# context = context
form = context.REQUEST.form


user_id = context.supprimerCaractereSpeciaux(form["authMember"])

# TODO : voir le code de "export_wims_exercice_script" pour l'appliquer ici

if "paths" in form:
    listeIdsExos = []
    for path in form["paths"]:
        if "groupe-" not in path:
            listeIdsExos.append(path.split("/")[-1])
    file_content = context.exportExercicesWIMS(listeIdsExos, user_id, "Moodle", "latest")
    context.plone_utils.addPortalMessage(_(u"Votre export d'exercices a bien été généré."), 'success')
else:
    message = _(u"Aucun exercice selectionné")
    file_content = "<error>%s</error>" % message
    context.plone_utils.addPortalMessage(message, 'failure')

filename = "export_WIMS_%s.xml" % user_id
context.REQUEST.RESPONSE.setHeader('content-type', "application/xml")
context.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)

return file_content
