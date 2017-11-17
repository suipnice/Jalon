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
wims_exercice_folder = context.getMySubSpaceFolder(user_id, "Wims")


# TODO : voir le code de "export_wims_exercice_script" pour l'appliquer ici

if "paths" in form:
    listeIdsExos = []
    for path in form["paths"]:
        if "groupe-" not in path:
            object_id = path.split("/")[-1]
            listeIdsExos.append(object_id)
            obj = getattr(wims_exercice_folder, object_id)
            # TODO : ici il faut réussir à combiner plusieurs exos dans un fichier, et non écraser le précédent !
            file_content = obj.getExoXML("Moodle", "latest")
    context.plone_utils.addPortalMessage(_(u"Votre export d'exercices a bien été généré."), 'success')
else:
    context.plone_utils.addPortalMessage(_(u"Aucun exercice selectionné"), 'failure')

filename = "export_WIMS_%s.xml" % user_id
context.REQUEST.RESPONSE.setHeader('content-type', "application/xml")
context.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)

# Ici, context doit etre un jalonexercicewims
return file_content
