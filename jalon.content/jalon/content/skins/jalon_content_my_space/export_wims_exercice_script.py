##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
#import OEF_to_OLX

u"""  Script (Python) "export_wims_exercice_script".

Fournit un fichier telechargeable de l'exo WIMS courant, selon le format demandé (QTI, EDX, OEF...)

"""
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
    # Ici, context doit etre un jalonexercicewims
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

elif file_format == "FLL":
    filename = "%s.fll" % context.getId()
    request.RESPONSE.setHeader('content-type', "application/xml")
    request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
    # Ici, context doit etre un jalonexercicewims
    return context.getExoXML(file_format, version)

else:
    filename = "%s_WIMS_%s.xml" % (modele, file_format)
    request.RESPONSE.setHeader('content-type', "application/xml")
    request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
    # Ici, context doit etre un jalonexercicewims
    return context.getExoXML(file_format, version)
