##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

u"""  Script (Python) "export_wims_exercice_script".

Fournit un fichier telechargeable de l'exo WIMS courant, selon le format demandé (QTI, EDX, OEF...)

"""
# Ici, context doit etre un jalonexercicewims
# context = context
request = context.REQUEST
modele  = context.getModele()

portal = context.aq_parent
authMember = portal.portal_membership.getAuthenticatedMember()

# request n'est pas un veritable dico, donc pas de "in"
if request.has_key("format"):
    file_format = request["format"]
else:
    # Par défaut, on exporte en QTI
    file_format = "QTI"

if request.has_key("version"):
    version = request["version"]
else:
    # Par défaut, on exporte dans la derniere version
    version = "latest"

if file_format == "QTI":
    filename = "%s_WIMS_%s-%s.zip" % (modele, file_format, version)
    zipfile = context.getExoZIP("questionDB.xml", context.getExoXML(file_format, version))
    request.RESPONSE.setHeader('content-type', "application/zip")
    request.RESPONSE.setHeader('content-length', zipfile["length"])
    request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
    return zipfile["data"]

elif file_format == "OEF":
    filename = "%s.oef" % context.getId()
    request.RESPONSE.setHeader('content-type', "text/plain")
    request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
    exo_file = context.getExoOEF(modele, authMember, request)
    if exo_file["request_status"] == "OK":
        return exo_file["code_source"]
    else:
        return exo_file["error_message"]

else:

    # liste des etiquettes du dossier
    folder_subjects = context.aq_parent.getDisplaySubjects()

    # id des etiquettes de l'exercice
    cat_ids = context.Subject()
    cat_list = []
    if len(cat_ids) > 0:
        for subject in folder_subjects:
            if subject['tag_id'] in cat_ids:
                cat_list.append(subject['tag_title'])

    if file_format == "FLL":
        filename = "%s.fll" % context.getId()
    else:
        filename = "%s_WIMS_%s.xml" % (modele, file_format)
    request.RESPONSE.setHeader('content-type', "application/xml")
    request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
    return context.getExoXML(formatXML=file_format, version=version, xml_file=None, cat_list=cat_list)
